import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator
from scipy import stats
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings("ignore")

# Load the data and merged together
# Field soil moisture and soil temperature
daily_means_file = 'C:/Users/mcgr323/projects/ecotwin/daily_means.csv'
daily_means_df = pd.read_csv(daily_means_file)

# Field yield data
yield_file = 'C:/Users/mcgr323/projects/ecotwin/yield_data.csv'
yield_df = pd.read_csv(yield_file)

# Field Metadata
metadata_file = 'C:/Users/mcgr323/projects/ecotwin/sensor_metadata.csv'
sensor_metadata_df = pd.read_csv(metadata_file)

# Drop the 'logger' column from merged_df
sensor_metadata_df = sensor_metadata_df.drop('logger ID', axis=1)

# Merge dataframes on the common columns 'logger', 'port_num', 'sensor_plot', 'sens_depth_cm', and 'month'
merged_df = pd.merge(daily_means_df, yield_df, on=['sensor_plot'])

# Drop the 'logger' column from merged_df
merged_df = merged_df.drop('logger', axis=1)

# Merged soil temp, moisture and yield to metadata
merged_df = pd.merge(merged_df, sensor_metadata_df, left_on=['port_num', 'sensor_plot'],
                     right_on=['port', 'sensor_plot'])

# Remove redundant columns
merged_df = merged_df.drop(['port', 'sensor name', 'sensor type', 'notes'], axis=1)

# Set date as the index
merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_df.set_index('date', inplace=True)

# Change the datatype of the '% Irrigation' column to categorical
merged_df['irrigation_trt'] = merged_df['% Irrigation'].astype('category')

merged_df = merged_df[(merged_df['irrigation_trt'] == 100) & (merged_df['variety'] == 1)]


# Define a function to run the Dickey-Fuller test and return the results as a DataFrame
def test_stationarity(timeseries):
    # Perform Dickey-Fuller test:
    dftest = adfuller(timeseries, autolag='AIC')
    # Extract the test statistics and p-value:
    results = pd.Series([dftest[0], dftest[1], dftest[2]],
                        index=['Test Statistic', 'p-value', '#Lags Used'])
    # Extract and add the critical values for different significance levels:
    for key, value in dftest[4].items():
        results[f'Critical Value ({key})'] = value
    return results


def test_stationarity_for_parameter(data, parameter):
    # Group the data by irrigation treatment, plot id, and depth for the specified parameter
    grouped_data = data.groupby(['sens_depth_cm', '% Irrigation', 'sensor_plot'])[parameter]

    # Create an empty DataFrame to store the results
    results_df = pd.DataFrame(columns=['Depth', '% Irrigation', 'sensor_plot', 'p-value', 'stationary'])

    # Run the test on each group and store the results in the DataFrame
    for group, timeseries in grouped_data:
        print('Depth:', group[0], 'Group:', group[1:], end=' ')
        result = test_stationarity(timeseries)
        p_value = result[1]
        stationary = 'yes' if p_value < 0.05 else 'no'
        results_df = results_df.append(
            {'Depth': group[0], '% Irrigation': group[1], 'sensor_plot': group[2], 'p-value': p_value,
             'stationary': stationary},
            ignore_index=True)
        print('Stationary:', stationary)

    return results_df

# Find if soil moisture is stationary or not by sensor plot
results_wcm3 = test_stationarity_for_parameter(merged_df, 'mean_wcm3')

print(results_wcm3)

# Find if soil temperature is stationary or not by sensor plot
results_stemp = test_stationarity_for_parameter(merged_df, 'mean_stemp')

print(results_stemp)

# Load the EcoPod soil moisture, soil temperature and PAR data
daily_raw_file = 'C:/Users/mcgr323/projects/ecotwin/ecopod_soil_wcm_temp_and_par.csv'
daily_raw_df = pd.read_csv(daily_raw_file)


def test_stationarity(df, parameter):
    # Perform Dickey-Fuller test:
    dftest = adfuller(df[parameter], autolag='AIC')
    # Extract the test statistics and p-value:
    results = pd.Series([dftest[0], dftest[1], dftest[2]],
                        index=['Test Statistic', 'p-value', '#Lags Used'])
    # Extract and add the critical values for different significance levels:
    for key, value in dftest[4].items():
        results[f'Critical Value ({key})'] = value
    return results

result_lab_stemp = test_stationarity(daily_raw_df, 'Avg_SoilTemp')
print(result_lab_stemp)

result_lab_wcm3 = test_stationarity(daily_raw_df, 'Avg_SoilMoisture')
print(result_lab_wcm3)


# Function to get daily mean from hourly EcoPod Data
def get_daily_means(df):
    # convert "Date" column to datetime
    df["Date"] = pd.to_datetime(df["Date"])

    # group by date and calculate mean
    daily_means = df.groupby(pd.Grouper(key="Date", freq="D")).mean()

    return daily_means


# Run function
daily_means_lab = get_daily_means(daily_raw_df)

# Drop hour column
daily_means_lab = daily_means_lab.drop(['Hour'], axis=1)

# Group the measurements by date and depth, and calculate the mean temperature for each group
daily_means = daily_means_df.groupby(['date', 'sens_depth_cm'])['mean_stemp'].mean()

# Convert the resulting Series to a DataFrame
daily_means_all = pd.DataFrame({'mean_stemp': daily_means}).reset_index()

# Subset for depth = 18cm
depth_18_df = daily_means_all[daily_means_all['sens_depth_cm'] == 18]

# Create field df of daily mean soil temp
daily_field = depth_18_df[['date', 'mean_stemp']]

# Create lab df of daily mean soil temp
daily_lab = daily_means_lab[['Avg_SoilTemp']]
daily_lab = daily_lab.reset_index()
daily_lab = daily_lab.rename(columns={'Avg_SoilTemp': 'mean_stemp'})
daily_lab['Date'] = daily_lab['Date'].dt.strftime('%Y-%m-%d')
daily_lab = daily_lab.rename(columns={'Date': 'date'})


# Merge the two DataFrames on the 'date' column
merged_daily = daily_lab.merge(daily_field, on='date', suffixes=('_lab', '_field'))

# Calculate the difference in 'mean_stemp' between the two DataFrames
merged_daily['stemp_diff'] = merged_daily['mean_stemp_lab'] - merged_daily['mean_stemp_field']

# Drop rows with NaN in any of the 'mean_stemp' columns
merged_daily = merged_daily.dropna(subset=['mean_stemp_lab', 'mean_stemp_field'])

# Perform a paired t-test to check if the difference is significant
t_stat, p_val = stats.ttest_rel(merged_daily['mean_stemp_lab'], merged_daily['mean_stemp_field'])

# Print the results
print(f"T-statistic: {t_stat}")
print(f"P-value: {p_val}")

# Check if the difference is significant at the 0.05 significance level
if p_val < 0.05:
    print("The difference in mean_stemp between daily_lab and daily_field is significant.")
else:
    print("The difference in mean_stemp between daily_lab and daily_field is not significant.")



# Convert the 'date' column to a pandas datetime object
merged_daily['date'] = pd.to_datetime(merged_daily['date'])

# Set the 'date' column as the index
merged_daily.set_index('date', inplace=True)

# Calculate the standard deviation for each 'mean_stemp' column
lab_std = merged_daily['mean_stemp_lab'].std()
field_std = merged_daily['mean_stemp_field'].std()

# Set the figure size
fig, ax = plt.subplots(figsize=(7, 4))  # Adjust the width and height as desired

lab_color = '#172869'
field_color = '#2db11a'

merged_daily['mean_stemp_lab'].plot(ax=ax, label='Lab', color=lab_color)
merged_daily['mean_stemp_field'].plot(ax=ax, label='Field', color=field_color)

# Add shaded areas for the variance
ax.fill_between(merged_daily.index, merged_daily['mean_stemp_lab'] - lab_std, merged_daily['mean_stemp_lab'] + lab_std, alpha=0.2, color=lab_color)
ax.fill_between(merged_daily.index, merged_daily['mean_stemp_field'] - field_std, merged_daily['mean_stemp_field'] + field_std, alpha=0.2, color=field_color)

# Customize the plot
ax.set_xlabel('Date', fontsize=20)  # Adjust the font size as desired
ax.set_ylabel('Mean Soil Temperature (\u00b0C)', fontsize=20)  # Adjust the font size as desired
ax.set_title('Daily Lab and Field Soil Temperature with Variance', fontsize=24)  # Adjust the font size as desired

# Set the date format without the year
date_fmt = DateFormatter('%b')
ax.xaxis.set_major_formatter(date_fmt)

# Set the locator to show the month only once
ax.xaxis.set_major_locator(MonthLocator())

#ax.legend(fontsize=0)  # Adjust the font size as desired

# Set the font size for tick labels
ax.tick_params(axis='both', which='major', labelsize=20)

# Show the plot
plt.show()

# Soil moisture
# Group the measurements by date and depth, and calculate the mean temperature for each group
daily_means = daily_means_df.groupby(['date', 'sens_depth_cm'])['mean_wcm3'].mean()

# Convert the resulting Series to a DataFrame
daily_means_all = pd.DataFrame({'mean_wcm3': daily_means}).reset_index()

# Subset for depth = 18cm
depth_18_df = daily_means_all[daily_means_all['sens_depth_cm'] == 18]

# Create field df of daily mean soil temp
daily_field = depth_18_df[['date', 'mean_wcm3']]
daily_field['mean_wcm3'] = daily_field['mean_wcm3']*100

# Create lab df of daily mean soil temp
daily_lab = daily_means_lab[['Avg_SoilMoisture']]
daily_lab = daily_lab.reset_index()
daily_lab = daily_lab.rename(columns={'Avg_SoilMoisture': 'mean_wcm3'})
daily_lab['Date'] = daily_lab['Date'].dt.strftime('%Y-%m-%d')
daily_lab = daily_lab.rename(columns={'Date': 'date'})


# Merge the two DataFrames on the 'date' column
merged_daily = daily_lab.merge(daily_field, on='date', suffixes=('_lab', '_field'))

# Calculate the difference in 'mean_stemp' between the two DataFrames
merged_daily['wcm3_diff'] = merged_daily['mean_wcm3_lab'] - merged_daily['mean_wcm3_field']

# Drop rows with NaN in any of the 'mean_stemp' columns
merged_daily = merged_daily.dropna(subset=['mean_wcm3_lab', 'mean_wcm3_field'])

# Perform a paired t-test to check if the difference is significant
t_stat, p_val = stats.ttest_rel(merged_daily['mean_wcm3_lab'], merged_daily['mean_wcm3_field'])

# Print the results
print(f"T-statistic: {t_stat}")
print(f"P-value: {p_val}")

# Check if the difference is significant at the 0.05 significance level
if p_val < 0.05:
    print("The difference in mean_wcm3 between daily_lab and daily_field is significant.")
else:
    print("The difference in mean_wcm3 between daily_lab and daily_field is not significant.")



# Convert the 'date' column to a pandas datetime object
merged_daily['date'] = pd.to_datetime(merged_daily['date'])

# Set the 'date' column as the index
merged_daily.set_index('date', inplace=True)

# Calculate the standard deviation for each 'mean_stemp' column
lab_std = merged_daily['mean_wcm3_lab'].std()
field_std = merged_daily['mean_wcm3_field'].std()

# Set the figure size
fig, ax = plt.subplots(figsize=(7, 4))  # Adjust the width and height as desired

lab_color = '#172869'
field_color = '#2db11a'

merged_daily['mean_wcm3_lab'].plot(ax=ax, label='Lab', color=lab_color)
merged_daily['mean_wcm3_field'].plot(ax=ax, label='Field', color=field_color)

# Add shaded areas for the variance
ax.fill_between(merged_daily.index, merged_daily['mean_wcm3_lab'] - lab_std, merged_daily['mean_wcm3_lab'] + lab_std, alpha=0.2, color=lab_color)
ax.fill_between(merged_daily.index, merged_daily['mean_wcm3_field'] - field_std, merged_daily['mean_wcm3_field'] + field_std, alpha=0.2, color=field_color)

# Customize the plot
ax.set_xlabel('Date', fontsize=20)  # Adjust the font size as desired
ax.set_ylabel('Mean Soil Moisture (%)', fontsize=20)  # Adjust the font size as desired
ax.set_title('Daily Lab and Field Soil Moisture with Variance', fontsize=24)  # Adjust the font size as desired

# Set the date format without the year
date_fmt = DateFormatter('%b')
ax.xaxis.set_major_formatter(date_fmt)

# Set the locator to show the month only once
ax.xaxis.set_major_locator(MonthLocator())

#ax.legend(fontsize=0) # Adjust the font size as desired

# Set the font size for tick labels
ax.tick_params(axis='both', which='major', labelsize=20)  # Adjust the font size as desired

# Show the plot
plt.show()

#add PAR
par_field_file = 'C:/Users/mcgr323/projects/ecotwin/par_field.csv'
par_field_df = pd.read_csv(par_field_file)

daily_means_par_field = get_daily_means(par_field_df)
daily_means_par_field['date'] = daily_means_par_field.index
daily_means_par_field['date'] = daily_means_par_field['date'].dt.strftime('%Y-%m-%d')
daily_means_par_field.reset_index(drop=True, inplace=True)

# Create lab df of daily mean soil temp
daily_lab = daily_means_lab[['Average_PAR']]
daily_lab = daily_lab.reset_index()
daily_lab = daily_lab.rename(columns={'Average_PAR': 'PAR'})
daily_lab['Date'] = daily_lab['Date'].dt.strftime('%Y-%m-%d')
daily_lab = daily_lab.rename(columns={'Date': 'date'})


# Merge the two DataFrames on the 'date' column
merged_daily = daily_lab.merge(daily_means_par_field, on='date', suffixes=('_lab', '_field'))

# Calculate the difference in 'mean_stemp' between the two DataFrames
merged_daily['PAR_diff'] = merged_daily['PAR_lab'] - merged_daily['PAR_field']

# Drop rows with NaN in any of the 'mean_stemp' columns
merged_daily = merged_daily.dropna(subset=['PAR_lab', 'PAR_field'])

# Perform a paired t-test to check if the difference is significant
t_stat, p_val = stats.ttest_rel(merged_daily['PAR_lab'], merged_daily['PAR_field'])

# Print the results
print(f"T-statistic: {t_stat}")
print(f"P-value: {p_val}")

# Check if the difference is significant at the 0.05 significance level
if p_val < 0.05:
    print("The difference in PAR between daily_lab and daily_field is significant.")
else:
    print("The difference in PAR between daily_lab and daily_field is not significant.")


# Convert the 'date' column to a pandas datetime object
merged_daily['date'] = pd.to_datetime(merged_daily['date'])

# Set the 'date' column as the index
merged_daily.set_index('date', inplace=True)

# Calculate the standard deviation for each 'mean_stemp' column
lab_std = merged_daily['PAR_lab'].std()
field_std = merged_daily['PAR_field'].std()


# Set the figure size
fig, ax = plt.subplots(figsize=(7, 4))  # Adjust the width and height as desired

lab_color = '#172869'
field_color = '#2db11a'

merged_daily['PAR_lab'].plot(ax=ax, label='Lab', color=lab_color)
merged_daily['PAR_field'].plot(ax=ax, label='Field', color=field_color)

# Add shaded areas for the variance
ax.fill_between(merged_daily.index, merged_daily['PAR_lab'] - lab_std, merged_daily['PAR_lab'] + lab_std, alpha=0.2, color=lab_color)
ax.fill_between(merged_daily.index, merged_daily['PAR_field'] - field_std, merged_daily['PAR_field'] + field_std, alpha=0.2, color=field_color)

# Customize the plot
ax.set_xlabel('Date', fontsize=20)  # Adjust the font size as desired
ax.set_ylabel('Mean PPFD (µmol·m⁻²·s⁻¹)', fontsize=20)  # Adjust the font size as desired
ax.set_title('Daily Lab and Field PAR with Variance', fontsize=24)  # Adjust the font size as desired

# Set the date format without the year
date_fmt = DateFormatter('%b')
ax.xaxis.set_major_formatter(date_fmt)

# Set the locator to show the month only once
ax.xaxis.set_major_locator(MonthLocator())

#ax.legend(fontsize=0)  # Adjust the font size as desired

# Set the font size for tick labels
ax.tick_params(axis='both', which='major', labelsize=20)  # Adjust the font size as desired

# Show the plot
plt.show()


par_means_file = 'C:/Users/mcgr323/projects/ecotwin/par_means.csv'
par_means_df = pd.read_csv(par_means_file)

par_means_df['date'] = pd.to_datetime(par_means_df['date'])

# Set the figure size
fig, ax = plt.subplots(figsize=(7, 4))  # Adjust the width and height as desired

lab_color = '#172869'
field_color = '#2db11a'

par_means_df['Lab'].plot(ax=ax, label='Lab', color=lab_color)
par_means_df['Field'].plot(ax=ax, label='Field', color=field_color)

# Customize the plot
ax.set_xlabel('Date', fontsize=20)  # Adjust the font size as desired
ax.set_ylabel('Mean PPFD (µmol·m⁻²·s⁻¹)', fontsize=20)  # Adjust the font size as desired
ax.set_title('Daily Lab and Field PAR', fontsize=24)  # Adjust the font size as desired

# Set the date format without the year
date_fmt = DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(date_fmt)

# Set the locator to show the month only once
ax.xaxis.set_major_locator(MonthLocator())

#ax.legend(fontsize=0)  # Adjust the font size as desired

# Set the font size for tick labels
ax.tick_params(axis='both', which='major', labelsize=20)  # Adjust the font size as desired

# Show the plot
plt.show()
