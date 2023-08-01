import os
import pandas as pd
from joblib import Parallel, delayed, parallel_backend
import matplotlib.pyplot as plt


def load_file(full_path):
    print(f"Attempting to read file: {full_path}")
    try:
        df = pd.read_csv(full_path, skiprows=8, parse_dates=['datetime'])
        # Ensure 'datetime' is in the correct datetime format and set it as UTC
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True)

        # Convert to Pacific Time
        df['datetime'] = df['datetime'].dt.tz_convert('America/Los_Angeles')

        # Extract logger id from filename (assuming it's always in the same format)
        logger_id = full_path.split('-')[1].split('.')[0][:5]

        # Add 'logger' column
        df['logger'] = logger_id

        return df
    except pd.errors.EmptyDataError:
        print(f"Skipping empty file: {full_path}")
    except Exception as e:
        print(f"Error reading file: {full_path}. Error was: {e}")


# Set the data directory
data_directory = 'Y:\\data_ZentraCloud\\'

# Get all subdirectories in the data directory
week_directories = [d for d in os.listdir(data_directory) if os.path.isdir(os.path.join(data_directory, d))]

# Get all data files from the week directory
data_files = [os.path.join(data_directory, week_dir, f)
              for week_dir in week_directories
              for f in os.listdir(os.path.join(data_directory, week_dir)) if f.endswith('.csv')]

# Load files in parallel
with parallel_backend('threading', n_jobs=-1):
    dfs = Parallel()(delayed(load_file)(f) for f in data_files)

# Concatenate all data files into a single DataFrame
all_data = pd.concat(dfs)


# Create a copy of the DataFrame
all_data_copy = all_data.copy()

# Ensure 'datetime' is in the correct datetime format and set to UTC
all_data_copy['datetime'] = pd.to_datetime(all_data_copy['datetime'], utc=True)

# Set 'datetime' as the DataFrame's index
all_data_copy.set_index('datetime', inplace=True)

# Create a new DataFrame with datetime converted to Pacific Time
all_data_pacific = all_data_copy.copy()
all_data_pacific.index = all_data_pacific.index.tz_convert('America/Los_Angeles')

daily_means = all_data_pacific.pivot_table(index=all_data_pacific.index.date,
                                           columns=['measurement', 'precision', 'port_num', 'sub_sensor_index', 'logger'],
                                           values='value',
                                           aggfunc='mean')


# Filter the DataFrame to include only the "Water Content" measurement
water_content_df = all_data_pacific[all_data_pacific['measurement'] == 'Water Content']

# Group by logger, port_num, sensor_sub_index, and date, and calculate the daily mean
daily_mean_water_content = water_content_df.groupby(['logger', 'port_num', pd.Grouper(freq='D')])['value'].mean().reset_index()

# Read metadata from CSV file
metadata_file = 'Y:\\metadata.csv'
metadata = pd.read_csv(metadata_file)

# Merge data with metadata
metadata['port_num'] = metadata['port'].astype(str)
metadata['logger'] = metadata['logger ID'].astype(str)
daily_mean_water_content['port_num'] = daily_mean_water_content['port_num'].astype(str)
daily_mean_water_content['logger'] = daily_mean_water_content['logger'].astype(str)
merged_data = daily_mean_water_content.merge(metadata, left_on=['port_num', 'logger'], right_on=['port_num', 'logger'])

merged_data.drop(['port', 'logger ID'], axis=1, inplace=True)

# field capacity
data = {
    'Plot Number': [10, 10, 10, 42, 42, 42, 16, 16, 16, 25, 25, 25],
    'Irrig. Lvl': ['100%', '100%', '100%', '100%', '100%', '100%', '100%', '100%', '100%', '100%', '100%', '100%'],
    'Sensor Depth (cm)': [18, 41, 100, 18, 41, 100, 18, 41, 100, 18, 41, 100],
    'Estimated Field Capacity (cm/cm)': [0.33, 0.27, 0.23, 0.36, 0.32, 0.33, 0.31, 0.36, 0.36, 0.33, 0.33, 0.23]
}

df = pd.DataFrame(data)

mean_field_capacity = df.groupby('Sensor Depth (cm)')['Estimated Field Capacity (cm/cm)'].mean()
mean_field_capacity = mean_field_capacity.reset_index()
mean_field_capacity.columns = ['sensor depth (cm)', 'mean_field_capacity']
mean_field_capacity['sensor depth (cm)'] = mean_field_capacity['sensor depth (cm)'].astype(str)

soil_water_deficit = merged_data.copy()
soil_water_deficit = pd.merge(soil_water_deficit, mean_field_capacity, on='sensor depth (cm)')
soil_water_deficit['soil_water_deficit'] = soil_water_deficit['mean_field_capacity'] - soil_water_deficit['value']
soil_water_deficit.drop('mean_field_capacity', axis=1, inplace=True)

# Assuming you have a 'year' column in your soil_water_deficit DataFrame
soil_water_deficit['year'] = soil_water_deficit['datetime'].dt.year

# Group the data by 'sensor plot', 'sensor depth (cm)', and 'year' and calculate the sum
cum_grouped_data = soil_water_deficit.groupby(['sensor plot', 'sensor depth (cm)', 'year'])['soil_water_deficit'].sum().reset_index()

# Group the data by 'sensor plot', 'sensor depth (cm)', and 'year' and calculate the sum
mean_grouped_data = soil_water_deficit.groupby(['sensor plot', 'sensor depth (cm)', 'year'])['soil_water_deficit'].mean().reset_index()
mean_grouped_data['soil_water_%'] = 100 - (mean_grouped_data['soil_water_deficit']* 100)

mean_merged_data = metadata.merge(mean_grouped_data, left_on=['sensor plot', 'sensor depth (cm)'], right_on=['sensor plot', 'sensor depth (cm)'])

data = mean_merged_data[['sensor plot', 'sensor depth (cm)', 'year', 'soil_water_%']]
data['soil_water_diff'] = data.groupby(['sensor plot', 'sensor depth (cm)'])['soil_water_%'].diff()


# Iterate over each unique combination of sensor plot and depth
for (sensor_plot, depth), group in data.groupby(['sensor plot', 'sensor depth (cm)']):
    plt.plot(group['year'], group['soil_water_diff'], label=f"Plot {sensor_plot}, Depth {depth}")

plt.xlabel('Year')
plt.ylabel('Difference in Soil Water Percentage')
plt.title('Difference in Soil Water Percentage by Year for Each Sensor Plot and Depth')
plt.legend()
plt.show()
