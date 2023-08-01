import pandas as pd
from stationary_test import test_stationarity_for_parameter
import statsmodels.api as sm
from statsmodels.formula.api import ols

daily_means_file = 'C:/Users/mcgr323/projects/ecotwin/daily_means.csv'
daily_means_df = pd.read_csv(daily_means_file)

# field yield data
yield_file = 'C:/Users/mcgr323/projects/ecotwin/yield_data.csv'
yield_df = pd.read_csv(yield_file)

metadata_file = 'C:/Users/mcgr323/projects/ecotwin/sensor_metadata.csv'
sensor_metadata_df = pd.read_csv(metadata_file)
# drop the 'logger' column from merged_df
sensor_metadata_df = sensor_metadata_df.drop('logger ID', axis=1)

# merge dataframes on the common columns 'logger', 'port_num', 'sensor_plot', 'sens_depth_cm', and 'month'
merged_df = pd.merge(daily_means_df, yield_df, on=['sensor_plot'])

# drop the 'logger' column from merged_df
merged_df = merged_df.drop('logger', axis=1)

merged_df = pd.merge(merged_df, sensor_metadata_df, left_on=['port_num', 'sensor_plot'],
                     right_on=['port', 'sensor_plot'])

# remove redundant columns
merged_df = merged_df.drop(['port', 'sensor name', 'sensor type', 'notes'], axis=1)

merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_df.set_index('date', inplace=True)

# find if the parameter is stationary or not
results_wcm3 = test_stationarity_for_parameter(merged_df, 'mean_wcm3')
results_stemp = test_stationarity_for_parameter(merged_df, 'mean_stemp')


# Change the datatype of the '% Irrigation' column to categorical
merged_df['irrigation_trt'] = merged_df['% Irrigation'].astype('category')


