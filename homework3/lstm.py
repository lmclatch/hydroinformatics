import math
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import joblib

# =============================================================================
# 1. SETUP & DEVICE
# =============================================================================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# =============================================================================
# 2. PARAMETERS
# =============================================================================
FILE_PATH       = "data/final_lstm_data.csv"
DATE_COL        = "date"
TARGET_COL      = "flow_cms"
TEST_BASIN_ID   = "15276000"   #  — held out entirely
VAL_CUTOFF_YEAR = 2016         # train ≤ 2016, val > 2016 (for the 3 training basins)

LOOKBACK_DAYS   = 90
BATCH_SIZE      = 64
EPOCHS          = 50
PATIENCE        = 10
LEARNING_RATE   = 1e-3

# =============================================================================
# 3. LOAD & CLEAN DATA
# =============================================================================
df = pd.read_csv(FILE_PATH)

# Standardise column names → valid Python identifiers
clean_cols = []
for c in df.columns:
    c = str(c).strip().replace('"', '')
    c = ''.join(ch if ch.isalnum() else '_' for ch in c)
    while '__' in c:
        c = c.replace('__', '_')
    clean_cols.append(c.strip('_'))
df.columns = clean_cols

# Keep gauge_id as a plain string (avoids float/merge issues)
df['gauge_id'] = df['gauge_id'].astype(str).str.replace('.0', '', regex=False)

df[DATE_COL] = pd.to_datetime(df[DATE_COL])
df = df.sort_values(['gauge_id', DATE_COL]).reset_index(drop=True)

print(f"Loaded {len(df):,} rows across {df['gauge_id'].nunique()} basins")
print(f"Basins: {df['gauge_id'].unique().tolist()}")

# =============================================================================
# 4. FEATURE SELECTION
# =============================================================================
exclude_cols = {TARGET_COL, DATE_COL, 'gauge_id', 'Unnamed_0', 'index', 'basin_name'}

numeric_cols  = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
feature_cols  = [c for c in numeric_cols if c not in exclude_cols]

print(f"\nTarget : {TARGET_COL}")
print(f"Features ({len(feature_cols)}): {feature_cols}")
df[feature_cols + [TARGET_COL]] = (
    df[feature_cols + [TARGET_COL]]
    .interpolate(method='linear', limit_direction='both')
    .ffill()
    .bfill()
)
# =============================================================================
# 5. BASIN-BASED TRAIN / VAL / TEST SPLIT
# =============================================================================
test_df     = df[df['gauge_id'] == TEST_BASIN_ID].copy()
train_val_df = df[df['gauge_id'] != TEST_BASIN_ID].copy()

train_df = train_val_df[train_val_df[DATE_COL].dt.year <= VAL_CUTOFF_YEAR].copy()
val_df   = train_val_df[train_val_df[DATE_COL].dt.year  > VAL_CUTOFF_YEAR].copy()

print(f"\nTrain   : {len(train_df):,} rows | basins: {train_df['gauge_id'].unique().tolist()}")
print(f"Val     : {len(val_df):,}  rows | basins: {val_df['gauge_id'].unique().tolist()}")
print(f"Test    : {len(test_df):,}  rows | basin : {TEST_BASIN_ID}")
#==============================================================================
# Feature engineering
#==============================================================================
for df_ in [train_df, val_df, test_df]:
    doy = df_['date'].dt.dayofyear
    df_['doy_sin'] = np.sin(2 * np.pi * doy / 365.25)
    df_['doy_cos'] = np.cos(2 * np.pi * doy / 365.25)
# =============================================================================
# 6. SCALING  — fit ONLY on training data to prevent leakage
# =============================================================================
feature_scaler = MinMaxScaler()
target_scaler  = MinMaxScaler()

feature_scaler.fit(train_df[feature_cols])
target_scaler.fit(train_df[[TARGET_COL]])

for d in [train_df, val_df, test_df]:
    d[feature_cols] = feature_scaler.transform(d[feature_cols])
    d[TARGET_COL]   = target_scaler.transform(d[[TARGET_COL]])

joblib.dump(feature_scaler, 'feature_scaler.gz')
joblib.dump(target_scaler,  'target_scaler.gz')
print("\nScalers saved.")

# =============================================================================
# 7. SEQUENCE CREATION — kept within each basin so windows don't bleed across
# =============================================================================
def create_sequences(data, feature_cols, target_col, lookback):
    X, y = [], []
    for basin in data['gauge_id'].unique():
        bd = data[data['gauge_id'] == basin]
        feats  = bd[feature_cols].values
        target = bd[target_col].values
        for i in range(lookback, len(bd)):
            X.append(feats[i - lookback:i])
            y.append(target[i])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

X_train, y_train = create_sequences(train_df, feature_cols, TARGET_COL, LOOKBACK_DAYS)
X_val,   y_val   = create_sequences(val_df,   feature_cols, TARGET_COL, LOOKBACK_DAYS)
X_test,  y_test  = create_sequences(test_df,  feature_cols, TARGET_COL, LOOKBACK_DAYS)

print(f"\nX_train : {X_train.shape}  →  (samples, timesteps, features)")
print(f"X_val   : {X_val.shape}")
print(f"X_test  : {X_test.shape}")

# =============================================================================
# 8. PYTORCH DATASET & DATALOADERS
# =============================================================================
class StreamflowDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X)
        self.y = torch.tensor(y).unsqueeze(-1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

train_loader = DataLoader(StreamflowDataset(X_train, y_train),
                          batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(StreamflowDataset(X_val,   y_val),
                          batch_size=BATCH_SIZE, shuffle=False)
test_loader  = DataLoader(StreamflowDataset(X_test,  y_test),
                          batch_size=BATCH_SIZE, shuffle=False)

# =============================================================================
# 9. MODEL
# =============================================================================
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size=1, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True,
                            dropout=dropout if num_layers > 1 else 0.0)
        self.fc   = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])   # last time-step only

model     = LSTMModel(input_size=len(feature_cols),
                      hidden_size=64, num_layers=2).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

print(f"\nModel parameters: {sum(p.numel() for p in model.parameters()):,}")

# =============================================================================
# 10. EVALUATE HELPER  
# =============================================================================
def evaluate(model, criterion, device, loader):
    """
    Run model in eval mode over a DataLoader.
    Returns (avg_loss, y_true_numpy, y_pred_numpy) — all in scaled space.
    """
    model.eval()
    losses, preds, trues = [], [], []
    with torch.no_grad():
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            pred   = model(xb)
            losses.append(criterion(pred, yb).item())
            preds.append(pred.cpu().numpy())
            trues.append(yb.cpu().numpy())
    avg_loss = float(np.mean(losses))
    y_pred   = np.concatenate(preds).flatten()
    y_true   = np.concatenate(trues).flatten()
    return avg_loss, y_true, y_pred

# =============================================================================
# 11. TRAINING LOOP WITH EARLY STOPPING
# =============================================================================
best_val_loss    = np.inf
best_state       = None
patience_counter = 0
history          = {'train_loss': [], 'val_loss': []}

for epoch in range(1, EPOCHS + 1):
    # ── training pass ──────────────────────────────────────────────────────
    model.train()
    batch_losses = []
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        loss = criterion(model(xb), yb)
        loss.backward()
        optimizer.step()
        batch_losses.append(loss.item())

    train_loss           = float(np.mean(batch_losses))
    val_loss, _, _       = evaluate(model, criterion, device, val_loader)
    history['train_loss'].append(train_loss)
    history['val_loss'].append(val_loss)

    print(f"Epoch {epoch:03d} | train {train_loss:.5f} | val {val_loss:.5f}")

    # ── early stopping ─────────────────────────────────────────────────────
    if val_loss < best_val_loss:
        best_val_loss    = val_loss
        best_state       = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        patience_counter = 0
    else:
        patience_counter += 1
        if patience_counter >= PATIENCE:
            print(f"Early stopping at epoch {epoch}.")
            break

# Restore best weights
if best_state is not None:
    model.load_state_dict(best_state)
    print(f"Best val loss: {best_val_loss:.5f}")

torch.save(model.state_dict(), 'best_lstm.pt')
print("Model saved → best_lstm.pt")

# =============================================================================
# 12. TEST EVALUATION (held-out basin)
# =============================================================================
_, y_true_scaled, y_pred_scaled = evaluate(model, criterion, device, test_loader)

# Inverse-transform back to cms
y_true = target_scaler.inverse_transform(y_true_scaled.reshape(-1, 1)).flatten()
y_pred = target_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

mae  = mean_absolute_error(y_true, y_pred)
rmse = math.sqrt(mean_squared_error(y_true, y_pred))
r2   = r2_score(y_true, y_pred)

# Nash-Sutcliffe Efficiency
nse  = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2)

print(f"\n{'='*40}")
print(f"  TEST BASIN: {TEST_BASIN_ID}")
print(f"  MAE  = {mae:.4f} cms")
print(f"  RMSE = {rmse:.4f} cms")
print(f"  R²   = {r2:.4f}")
print(f"  NSE  = {nse:.4f}")
print(f"{'='*40}")

# =============================================================================
# 13. PLOTS
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# Training history
axes[0].plot(history['train_loss'], label='Train')
axes[0].plot(history['val_loss'],   label='Validation')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('MSE Loss')
axes[0].set_title('Training History')
axes[0].legend()

# Observed vs predicted (first 365 days for readability)
n_plot = min(365, len(y_true))
axes[1].plot(y_true[:n_plot], label='Observed',  alpha=0.8)
axes[1].plot(y_pred[:n_plot], label='Predicted', alpha=0.8, linestyle='--')
axes[1].set_xlabel('Day')
axes[1].set_ylabel('Streamflow (cms)')
axes[1].set_title(f'Test Basin {TEST_BASIN_ID} — first {n_plot} days')
axes[1].legend()

plt.tight_layout()
plt.savefig('lstm_results.png', dpi=150)
#plt.show()
#print("Plot saved → lstm_results.png")

# --- 13e. Performance summary (test basin only) ----------------------------
summary = pd.DataFrame([{
    'basin': TEST_BASIN_ID,
    'split': 'test',
    'MAE' : mae,
    'RMSE': rmse,
    'R2'  : r2,
    'NSE' : nse,
}]).set_index('basin')

print("\n" + "=" * 60)
print("  TEST BASIN PERFORMANCE SUMMARY")
print("=" * 60)
print(summary.round(3).to_string())
print("=" * 60)

# =============================================================================
# 14. SCATTER PLOT — Predicted vs. Observed with 1:1 line
# =============================================================================
fig, ax = plt.subplots(figsize=(6.5, 6.5))

ax.scatter(y_true, y_pred, s=14, alpha=0.4, color='#1f4e79',
           edgecolor='none', label='Daily predictions')

# 1:1 reference line
lim = max(y_true.max(), y_pred.max()) * 1.05
ax.plot([0, lim], [0, lim], 'k--', lw=1.2, alpha=0.7, label='1:1 line')

# linear regression fit
slope, intercept = np.polyfit(y_true, y_pred, 1)
xs = np.array([0, lim])
ax.plot(xs, slope * xs + intercept, color='#c0392b', lw=1.5,
        label=f'Fit: y = {slope:.2f}x + {intercept:.2f}')

ax.set_xlim(0, lim)
ax.set_ylim(0, lim)
ax.set_xlabel('Observed streamflow (cms)')
ax.set_ylabel('Predicted streamflow (cms)')
ax.set_title(f'Test Basin {TEST_BASIN_ID} — Predicted vs. Observed')
ax.legend(loc='lower right')
ax.set_aspect('equal', adjustable='box')
ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('scatter_1to1.png', dpi=200, bbox_inches='tight')
plt.show()
print("Saved → scatter_1to1.png")