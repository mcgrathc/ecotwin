import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import MonthLocator, DateFormatter

# from calculate_soil_deficit import process_data

# Get daily and hourly soil water deficit
# monthly_soil_water_deficit, daily_soil_water_deficit, hourly_soil_water_deficit = process_data(data_directory='Y:\\data_ZentraCloud\\', metadata_file='Y:\\metadata.csv')

# Set the style of the plot
sns.set(style="whitegrid")

# Define custom colors
viva_magenta = "#FF00FF"  # Hex color code for Viva Magenta
evergreen_fog = "#324856"  # Hex color code for Evergreen Fog

def plot_soil_water(soil_data, plot_name):
    # Identify unique depths for the selected plot
    unique_depths = soil_data[soil_data['sensor plot'] == plot_name]['sensor depth (cm)'].unique()

    # Create a 3x1 subplot
    fig, axs = plt.subplots(len(unique_depths), 1, figsize=(10, 15))  # Adjust figsize as needed

    fig.suptitle(f'Soil Deficit over Time for Plot {plot_name}', fontsize=20)

    # Find global min and max of 'soil_water_%' for selected plot
    global_min = soil_data[soil_data['sensor plot'] == plot_name]['diff_from_irr_trt'].min()
    global_max = soil_data[soil_data['sensor plot'] == plot_name]['diff_from_irr_trt'].max()

    # Add buffer to the y-axis limits
    buffer_percentage = 0.1  # Adjust this value as needed
    y_buffer = (global_max - global_min) * buffer_percentage
    global_min -= y_buffer
    global_max += y_buffer

    for i, depth in enumerate(unique_depths):
        # Subset the DataFrame for this plot and depth
        subset = soil_data[(soil_data['sensor plot'] == plot_name) &
                            (soil_data['sensor depth (cm)'] == depth)]
        # For each year, plot a line graph
        for year in subset['year'].unique():
            if year == 2022:
                color = evergreen_fog
            elif year == 2023:
                color = viva_magenta
            else:
                continue
            subset_year = subset[subset['year'] == year]
            # Reformat 'datetime' to only include month and day (so years can be overlaid)
            datetime_series = subset_year['datetime'].apply(lambda dt: dt.replace(year=2020))
            subset_year = subset_year.assign(datetime=datetime_series)
            axs[i].plot(subset_year['datetime'], subset_year['diff_from_irr_trt'], color=color, label=f'Year {year} Depth {depth}cm', linewidth=2)  # Increase line thickness

        # Add horizontal line at y=0
        axs[i].axhline(0, color='black', linewidth=1, linestyle='dotted')

        # axs[i].set_ylabel('Soil Water Deficit (cm³/cm³)', fontsize=16)
        axs[i].set_ylabel('Difference from Irrigation Treatment (%)', fontsize=20)
        axs[i].legend(loc='upper right', prop={'size': 20})

        # Set the x-axis to only include one tick per month
        axs[i].xaxis.set_major_locator(MonthLocator())
        axs[i].xaxis.set_major_formatter(DateFormatter('%b'))
        axs[i].xaxis.label.set_size(20)
        axs[i].yaxis.label.set_size(20)

        # Set y-axis limit to be the same for all subplots
        axs[i].set_ylim([global_min, global_max])

    # Add x-axis label only on the bottom plot
    axs[-1].set_xlabel('Date', fontsize=20)

    # Adjust space between subplots
    plt.tight_layout(rect=[0, 0, 1, 0.96], pad=2)  # Added padding
    plt.subplots_adjust(hspace=0.2)  # Adjust space between subplots

    # Save the plot
    plt.savefig(f'C:/Users/mcgr323/projects/ecotwin/soil_water_deficit/diff_from_irrigation_{plot_name}.png', dpi=300)

    plt.show()

# Call the function for each unique plot
unique_plots = daily_soil_water_deficit['sensor plot'].unique()
for plot in unique_plots:
    plot_soil_water(daily_soil_water_deficit, plot)
