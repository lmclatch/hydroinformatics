
import pandas as pd
#Pull SNOTEL/Swe data
'''
Data pulled from: Gagliano, E. (2024). 
snotel_ccss_stations (Version v1.0) [Computer software]. https://github.com/egagli/snotel_ccss_stations
'''
url = 'https://github.com/egagli/snotel_ccss_stations/blob/main/data/1091_AK_SNTL.csv?raw=true'

try:
    # Read CSV directly into a DataFrame
    snotel_AK = pd.read_csv(url)
    print("CSV loaded successfully!")
    print(snotel_AK.head())  # Display first 5 rows
except Exception as e:
    print(f"Error loading CSV: {e}")


print(snotel_AK.head())
snotel_AK.to_csv('data/snotel_data.csv', index=False)