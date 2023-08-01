import os
import pandas as pd
from joblib import Parallel, delayed, parallel_backend


def load_file(full_path):
    print(f"Attempting to read file: {full_path}")
    try:
        df = pd.read_csv(full_path, skiprows=8, parse_dates=['datetime'])
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
        df['datetime'] = df['datetime'].dt.tz_convert('America/Los_Angeles')
        logger_id = full_path.split('-')[1].split('.')[0][:5]
        df['logger'] = logger_id

        # Add a line to filter dates between March 1 and October 31
        df = df[(df['datetime'].dt.month >= 3) & (df['datetime'].dt.month <= 10)]

        return df
    except pd.errors.EmptyDataError:
        print(f"Skipping empty file: {full_path}")
    except Exception as e:
        print(f"Error reading file: {full_path}. Error was: {e}")


def get_all_data_files(data_directory):
    week_directories = [d for d in os.listdir(data_directory) if os.path.isdir(os.path.join(data_directory, d))]
    data_files = [os.path.join(data_directory, week_dir, f)
                  for week_dir in week_directories
                  for f in os.listdir(os.path.join(data_directory, week_dir)) if f.endswith('.csv')]
    return data_files


def load_all_data_in_parallel(data_files):
    with parallel_backend('threading', n_jobs=-1):
        dfs = Parallel()(delayed(load_file)(f) for f in data_files)
    all_data = pd.concat(dfs)
    all_data.set_index('datetime', inplace=True)
    return all_data


def filter_and_group_data(all_data, freq='D'):
    all_data = all_data[all_data['measurement'] == 'Water Content']
    mean_water_content = all_data.groupby(['logger', 'port_num', pd.Grouper(freq=freq)])[
        'value'].mean().reset_index()
    return mean_water_content


def merge_with_metadata(daily_mean_water_content, metadata_file):
    metadata = pd.read_csv(metadata_file)
    metadata['port_num'] = metadata['port'].astype(str)
    metadata['logger'] = metadata['logger ID'].astype(str)
    daily_mean_water_content['port_num'] = daily_mean_water_content['port_num'].astype(str)
    daily_mean_water_content['logger'] = daily_mean_water_content['logger'].astype(str)
    merged_data = daily_mean_water_content.merge(metadata, left_on=['port_num', 'logger'],
                                                 right_on=['port_num', 'logger'])
    merged_data.drop(['port', 'logger ID'], axis=1, inplace=True)
    return merged_data


def calculate_soil_water_deficit(merged_data):
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
    soil_water_deficit['soil_water_deficit'] = -1 * (soil_water_deficit['mean_field_capacity'] - soil_water_deficit['value'])

    soil_water_deficit['year'] = soil_water_deficit['datetime'].dt.year
    soil_water_deficit['month'] = soil_water_deficit['datetime'].dt.month

    soil_water_deficit['soil_water_%'] = 100 - (-1*(soil_water_deficit['soil_water_deficit']) / soil_water_deficit['mean_field_capacity']) * 100
    soil_water_deficit['diff_from_irr_trt'] = soil_water_deficit['soil_water_%'] - soil_water_deficit['% Irrigation']

    return soil_water_deficit


def process_data(data_directory='Y:\\data_ZentraCloud\\', metadata_file='Y:\\metadata.csv'):
    data_files = get_all_data_files(data_directory)
    all_data = load_all_data_in_parallel(data_files)

    daily_mean_water_content = filter_and_group_data(all_data, freq='D')
    hourly_mean_water_content = filter_and_group_data(all_data, freq='H')
    monthly_mean_water_content = filter_and_group_data(all_data, freq='M')

    daily_merged_data = merge_with_metadata(daily_mean_water_content, metadata_file)
    hourly_merged_data = merge_with_metadata(hourly_mean_water_content, metadata_file)
    monthly_merged_data = merge_with_metadata(monthly_mean_water_content, metadata_file)

    daily_soil_water_deficit = calculate_soil_water_deficit(daily_merged_data)
    hourly_soil_water_deficit = calculate_soil_water_deficit(hourly_merged_data)
    monthly_soil_water_deficit = calculate_soil_water_deficit(monthly_merged_data)

    return daily_soil_water_deficit, hourly_soil_water_deficit, monthly_soil_water_deficit


daily_soil_water_deficit, hourly_soil_water_deficit, monthly_soil_water_deficit= process_data(data_directory='Y:\\data_ZentraCloud\\', metadata_file='Y:\\metadata.csv')