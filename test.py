import pandas as pd

# Assuming you have your data stored in a DataFrame called daily_soil_water_deficit

# Make a copy of the original DataFrame
df_copy = daily_soil_water_deficit.copy()

# Convert the 'datetime' column to datetime type if it's not already in that format
df_copy['datetime'] = pd.to_datetime(df_copy['datetime'])

# Extract the year and month from the 'datetime' column
df_copy['year'] = df_copy['datetime'].dt.year
df_copy['month'] = df_copy['datetime'].dt.month

# Filter the data for the year 2022 and 2023
df_2022_2023 = df_copy[df_copy['year'].isin([2022, 2023])]

# Create a new column combining year and month information
df_2022_2023['year_month'] = df_2022_2023['year'].astype(str) + '_' + df_2022_2023['month'].apply(lambda x: '{:02d}'.format(x))

# Pivot the data to have columns for each year_month combination and calculate the mean for the specified column
pivot_df = df_2022_2023.pivot_table(index=['sensor plot', 'sensor depth (cm)'], columns='year_month', values='diff_from_irr_trt', aggfunc='mean')

# Rename the columns to include the 'diff_from_irr_trt_' prefix
pivot_df.columns = 'diff_from_irr_trt_' + pivot_df.columns

# Save the pivoted data as a CSV file
pivot_df.to_csv('monthly_diff_from_irr_trt.csv')

print("CSV file saved successfully.")
