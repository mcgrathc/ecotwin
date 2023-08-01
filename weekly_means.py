import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List


def plot_soil_data(root_dir: str):
    loggers = os.listdir(root_dir)
    markers = ['o', 's', 'v', '^', '>', '<', 'p', '*', 'h', 'H', '+', 'x', 'D', '|', '_']

    for logger in loggers:
        logger_dir = os.path.join(root_dir, logger)

        if os.path.isdir(logger_dir):
            port_files = os.listdir(logger_dir)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            ax1.set_title(f"{logger} - Weekly Soil Moisture")
            ax2.set_title(f"{logger} - Weekly Soil Temperature")

            for i, port_file in enumerate(port_files):
                if port_file.endswith(".csv"):
                    port_path = os.path.join(logger_dir, port_file)
                    df = pd.read_csv(port_path)
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.set_index('Date')
                    df = df.resample('W').mean()

                    # Get depth index for assigning marker style
                    depth_idx = int(df['sens_depth_cm'].mean()) % len(markers)

                    # Plot soil moisture and temperature
                    ax1.plot(df.index, df['mean_wcm3'], label=f"Port {i+1}", linestyle='-', marker=markers[depth_idx])
                    ax2.plot(df.index, df['mean_stemp'], label=f"Port {i+1}", linestyle='-', marker=markers[depth_idx])

            ax1.set_ylabel('Soil Moisture (m³/m³)')
            ax1.legend(loc='best')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            ax1.tick_params(axis='x', labelsize=8)

            ax2.set_ylabel('Soil Temperature (°C)')
            ax2.legend(loc='best')
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            ax2.tick_params(axis='x', labelsize=8)

            plt.tight_layout()
            plt.savefig(f"{logger}_soil_data.png", dpi=300)
            plt.show()

root_dir = "Z:/Data/SoilMoisture/Full_Summer_Data/2022_Soil_Data/"
plot_soil_data(root_dir)

def merge_csv_files(sensor_metadata_file: str, soil_moisture_file: str):
    # Read the CSV files into pandas DataFrames
    sensor_metadata_df = pd.read_csv(sensor_metadata_file)
    soil_moisture_df = pd.read_csv(soil_moisture_file)

    # Merge the DataFrames on the 'sensor_plot' column
    merged_df = pd.merge(soil_moisture_df, sensor_metadata_df, on='sensor plot')
    merged_df['diff_core_sat_pct_irrigation'] = merged_df['core sat_%'] - merged_df['% Irrigation']
    selected_columns = ['core sat_%', 'logger ID', 'port', 'sensor depth (cm)', '% Irrigation',
                        'diff_core_sat_pct_irrigation']
    subset_df = merged_df[selected_columns]

    return subset_df

sensor_metadata_file = "sensor_metadata.csv"
soil_moisture_file = "soil_moisture_depth.csv"

merged_df = merge_csv_files(sensor_metadata_file, soil_moisture_file)

import seaborn as sns
import matplotlib.pyplot as plt

sns.pairplot(merged_df)
plt.show()

correlations = merged_df.corr()


# Create the scatterplot
plt.scatter(merged_df['mean_wcm3'], merged_df['yield_Mg_ha'])
plt.xlabel('Soil Moisture (mean_wcm3)')
plt.ylabel('Yield (yield_Mg_ha)')
plt.title('Relationship between Soil Moisture and Yield')
plt.show()

import statsmodels.api as sm

# Add a constant to the DataFrame for the regression model
data = sm.add_constant(merged_df)

# Define your independent (X) and dependent (y) variables
X = data[['const', 'mean_wcm3', 'mean_stemp']]
y = data['yield_Mg_ha']

# Fit the regression model
model = sm.OLS(y, X).fit()

# Print the model summary
print(model.summary())

# Filter the data for depth = 18
merged_df = merged_df[merged_df['sens_depth_cm'] == 18]

# Group the data by irrigation treatment and month, and calculate the mean for soil moisture
grouped_data = merged_df.groupby(['% Irrigation', 'month']).mean()

# Extract the mean soil moisture columns as separate variables for each irrigation treatment
irrig_trt_25 = grouped_data.loc[25, 'mean_wcm3']
irrig_trt_50 = grouped_data.loc[50, 'mean_wcm3']
irrig_trt_75 = grouped_data.loc[75, 'mean_wcm3']
irrig_trt_100 = grouped_data.loc[100, 'mean_wcm3']

# Create the line plot for each irrigation treatment
plt.plot(irrig_trt_25.index, irrig_trt_25, label='25% Irrigation')
plt.plot(irrig_trt_50.index, irrig_trt_50, label='50% Irrigation')
plt.plot(irrig_trt_75.index, irrig_trt_75, label='75% Irrigation')
plt.plot(irrig_trt_100.index, irrig_trt_100, label='100% Irrigation')
plt.xlabel('Month')
plt.ylabel('Mean Soil Moisture (cm^3/cm^3)')
plt.title('Mean Soil Moisture over Time, Depth = 18')
plt.legend()
plt.show()