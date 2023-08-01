import pandas as pd

# Get daily and hourly soil water deficit
monthly_soil_water_deficit, daily_soil_water_deficit, hourly_soil_water_deficit = process_data(data_directory='Y:\\data_ZentraCloud\\', metadata_file='Y:\\metadata.csv')

def transform_data(df, year, depth):
    # Convert 'sensor depth (cm)' column to numeric
    df['sensor depth (cm)'] = pd.to_numeric(df['sensor depth (cm)'], errors='coerce')

    # Subset the data based on the specified year and depth
    subset_df = df[(df['year'] == year) & (df['sensor depth (cm)'] == depth)]

    # Pivot the data to create columns for each month
    pivot_df = subset_df.pivot_table(index=['sensor plot'],
                                     columns='month', values='soil_water_deficit').reset_index()

    # Rename the columns to include the 'sensor_plot' column
    pivot_df.columns.name = None

    return pivot_df

# Assuming your original DataFrame is named 'monthly_soil_water_deficit'
year = 2022
depth = 41  # Example depth value

transformed_df = transform_data(monthly_soil_water_deficit, year, depth)

monthly_csv_file_path = "C:/Users/mcgr323/projects/ecotwin/monthly_soil_water_deficit_2022_plots.csv"

# Write the DataFrame to a CSV file
transformed_df.to_csv(monthly_csv_file_path, index=False)