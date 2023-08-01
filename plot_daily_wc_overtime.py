import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Get daily and hourly soil water deficit
# monthly_soil_water_deficit, daily_soil_water_deficit, hourly_soil_water_deficit = process_data(data_directory='Y:\\data_ZentraCloud\\', metadata_file='Y:\\metadata.csv')

df = daily_soil_water_deficit

# Ensure your 'datetime' column is indeed datetime type
df['datetime'] = pd.to_datetime(df['datetime'])

# Create new column 'year'
df['year'] = df['datetime'].dt.year

# Convert 'sensor depth (cm)' to integer
df['sensor depth (cm)'] = df['sensor depth (cm)'].astype(int)

# Remove outliers
df = df.loc[(df['value'] >= 0) & (df['value'] <= 1)]

# Sort values by datetime
df = df.sort_values('datetime')

# Get the unique sensor plots across the entire dataset
sensor_plots_all = sorted(df['sensor plot'].unique())

def plot_by_sensor(df, irrigation_level):
    # Subset dataframe by irrigation level
    subset_irrigation = df[df['% Irrigation'] == irrigation_level]

    # Get the unique years and sensor depths for the subset
    years = sorted(subset_irrigation['year'].unique())
    sensor_depths = sorted(subset_irrigation['sensor depth (cm)'].unique())

    # Create subplots for each sensor depth
    fig, axs = plt.subplots(len(sensor_depths), 1, figsize=(10, 5*len(sensor_depths)))

    for i, depth in enumerate(sensor_depths):
        for year in years:
            for plot in sensor_plots_all:
                subset = subset_irrigation[
                    (subset_irrigation['year'] == year) &
                    (subset_irrigation['sensor plot'] == plot) &
                    (subset_irrigation['sensor depth (cm)'] == depth)]  # subset dataframe by specified criteria
                if not subset.empty:  # check if subset is not empty
                    axs[i].plot(subset['datetime'], subset['value'], color=colors[sensor_plots_all.index(plot) % len(colors)], label='{} - {}'.format(plot, year))  # plot the values over time

            axs[i].set_title('Irrigation Level: {} - Sensor Depth: {}'.format(irrigation_level, depth))  # set the title
            axs[i].legend()  # add a legend
            axs[i].set_xlabel('Date')  # set x-axis label
            axs[i].set_ylabel('Daily Mean Water Content (cm3/cm3)')  # set y-axis label

    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig('Irrigation_Level_{}_plot.png'.format(irrigation_level))

    plt.show()

# Call the function with an irrigation level
plot_by_sensor(df, 25.0)  # example value