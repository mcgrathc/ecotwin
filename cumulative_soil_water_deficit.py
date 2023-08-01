import pandas as pd

daily_soil_water_deficit, hourly_soil_water_deficit, monthly_soil_water_deficit= process_data(data_directory='Y:\\data_ZentraCloud\\', metadata_file='Y:\\metadata.csv')
df = daily_soil_water_deficit


def process_df_and_save(df):
    # Ensure 'datetime' column is in datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Create masks for your date ranges
    mask1 = (df['datetime'] <= '2022-07-11')
    mask2 = (df['datetime'] >= '2022-07-26') & (df['datetime'] <= '2022-09-26')
    mask3 = (df['datetime'] <= '2022-09-26')

    # Subset the dataframes
    df1 = df.loc[mask1]
    df2 = df.loc[mask2]
    df3 = df.loc[mask3]

    # Ensure that each dataframe is sorted by 'datetime'
    df1 = df1.sort_values('datetime')
    df2 = df2.sort_values('datetime')
    df3 = df3.sort_values('datetime')

    # Calculate cumulative 'soil_water_deficit' for each 'sensor plot' and 'sensor depth (cm)'
    df1['soil_water_deficit_cumulative'] = df1.groupby(['sensor plot', 'sensor depth (cm)'])['soil_water_deficit'].cumsum()
    df2['soil_water_deficit_cumulative'] = df2.groupby(['sensor plot', 'sensor depth (cm)'])['soil_water_deficit'].cumsum()
    df3['soil_water_deficit_cumulative'] = df3.groupby(['sensor plot', 'sensor depth (cm)'])['soil_water_deficit'].cumsum()

    # Generate filenames with start and end dates
    filename1 = f"cumulative_swd_{df1['datetime'].min().strftime('%Y%m%d')}_to_{df1['datetime'].max().strftime('%Y%m%d')}.csv"
    filename2 = f"cumulative_swd_{df2['datetime'].min().strftime('%Y%m%d')}_to_{df2['datetime'].max().strftime('%Y%m%d')}.csv"
    filename3 = f"cumulative_swd_{df3['datetime'].min().strftime('%Y%m%d')}_to_{df3['datetime'].max().strftime('%Y%m%d')}.csv"

    # Save each dataframe as a CSV with dates in filename
    df1.to_csv(filename1, index=False)
    df2.to_csv(filename2, index=False)
    df3.to_csv(filename3, index=False)

process_df_and_save(df)