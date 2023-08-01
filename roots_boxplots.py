import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set context to make fonts larger
sns.set_context("poster", font_scale=1.5)

# Load the data
df1 = pd.read_csv("roots_ecopod.csv")
df2 = pd.read_csv("root_prosser.csv")

# Strip potential whitespaces in column names
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

# Create a figure with two subplots side by side sharing the same y-axis
fig, axes = plt.subplots(1, 2, figsize=(20, 10), sharey=True)

# Create box plot for df1
ax1 = sns.boxplot(x='Replicate', y='Total_Root_Length', data=df1, ax=axes[0], color='#0176c0')
axes[0].set_title('Total Root Length Ecopod', fontsize=36, pad=20)  # Increase title padding
axes[0].set_xlabel('', fontsize=32)
axes[0].set_ylabel('Total Root Length (mm)', fontsize=32, labelpad=20)  # Increase label padding

# Calculate and add mean asterisk for df1
mean1_pre = df1[df1['Replicate'] == 'Pre']['Total_Root_Length'].mean()
mean1_post = df1[df1['Replicate'] == 'Post']['Total_Root_Length'].mean()
axes[0].annotate('x', xy=(0, mean1_pre), xytext=(0, 0), textcoords='offset points', color='#404040', ha='center', fontsize=24)
axes[0].annotate('x', xy=(1, mean1_post), xytext=(0, 0), textcoords='offset points', color='#404040', ha='center', fontsize=24)
axes[0].plot([0, 1], [mean1_pre, mean1_post], color='#404040', linestyle='--')

# Create box plot for df2
ax2 = sns.boxplot(x='Replicate', y='Total_Root_Length', data=df2, ax=axes[1], color='#95c65c')
axes[1].set_title('Total Root Length Fieldsite', fontsize=36, pad=20)  # Increase title padding
axes[1].set_xlabel('', fontsize=32)
axes[1].set_ylabel('Total Root Length (mm)', fontsize=32, labelpad=20)  # Increase label padding

# Calculate and add mean asterisk for df2
mean2_pre = df2[df2['Replicate'] == 'Pre']['Total_Root_Length'].mean()
mean2_post = df2[df2['Replicate'] == 'Post']['Total_Root_Length'].mean()
axes[1].annotate('x', xy=(0, mean2_pre), xytext=(0, 0), textcoords='offset points', color='#404040', ha='center', fontsize=24)
axes[1].annotate('x', xy=(1, mean2_post), xytext=(0, 0), textcoords='offset points', color='#404040', ha='center', fontsize=24)
axes[1].plot([0, 1], [mean2_pre, mean2_post], color='#404040', linestyle='--')

# Adjust spacing between subplots and figure top
plt.subplots_adjust(top=0.8)  # Increase top spacing value as needed

# Show the plots
plt.tight_layout()
plt.show()


# Create a figure with two subplots side by side sharing the same y-axis
fig, axes = plt.subplots(1, 2, figsize=(20, 10), sharey=True)

# Create box plot for df1
ax1 = sns.boxplot(x='Replicate', y='Total_Root_Volume', data=df1, ax=axes[0], color='#0176c0')
axes[0].set_title('Total Root Volume Ecopod', fontsize=36, pad=20)  # Increase title padding
axes[0].set_xlabel('', fontsize=32)
axes[0].set_ylabel('Total Root Volume (mm\u00B3)', fontsize=32, labelpad=20)  # Increase label padding

# Calculate and add mean asterisk for df1
mean1_pre = df1[df1['Replicate'] == 'Pre']['Total_Root_Volume'].mean()
mean1_post = df1[df1['Replicate'] == 'Post']['Total_Root_Volume'].mean()
axes[0].annotate('x', xy=(0, mean1_pre), xytext=(0, 0), textcoords='offset points', color='#404040', ha='center', fontsize=24)
axes[0].annotate('x', xy=(1, mean1_post), xytext=(0, 0), textcoords='offset points', color='#404040', ha='center', fontsize=24)
axes[0].plot([0, 1], [mean1_pre, mean1_post], color='#404040', linestyle='--')

# Create box plot for df2
ax2 = sns.boxplot(x='Replicate', y='Total_Root_Volume', data=df2, ax=axes[1], color='#95c65c')
axes[1].set_title('Total Root Volume Fieldsite', fontsize=36, pad=20)  # Increase title padding
axes[1].set_xlabel('', fontsize=32)
axes[1].set_ylabel('Total Root Volume (mm\u00B3)', fontsize=32, labelpad=20)  # Increase label padding

# Calculate and add mean asterisk for df2
mean2_pre = df2[df2['Replicate'] == 'Pre']['Total_Root_Volume'].mean()
mean2_post = df2[df2['Replicate'] == 'Post']['Total_Root_Volume'].mean()
axes[1].annotate('x', xy=(0, mean2_pre), xytext=(0, 0), textcoords='offset points', color='#404040', ha='center', fontsize=24)
axes[1].annotate('x', xy=(1, mean2_post), xytext=(0, 0), textcoords='offset points', color='#404040', ha='center', fontsize=24)
axes[1].plot([0, 1], [mean2_pre, mean2_post], color='#404040', linestyle='--')

# Adjust spacing between subplots and figure top
plt.subplots_adjust(top=0.8)  # Increase top spacing value as needed

# Show the plots
plt.tight_layout()
plt.show()

# Create a figure with one row and five columns
fig, axes = plt.subplots(1, 5, figsize=(25, 10), sharey=True)

# Define the bin ranges
bin_ranges = ['0-0.25mm', '0.25-0.5mm', '0.5-0.75mm', '0.75-1mm', '>1mm']

# Loop over each column (D1-D5) and create the box plot for Ecopod data
for i, col in enumerate(df1.columns[3:8]):
    sns.boxplot(x=df1['Replicate'], y=col, data=df1, ax=axes[i], palette=['#0176c0', '#0176c0'])
    axes[i].set_title(bin_ranges[i], fontsize=32)
    axes[i].set_xlabel('')
    axes[i].set_xticklabels(['Pre', 'Post'])
    axes[i].set_ylabel('')  # Remove y-axis label
    axes[i].tick_params(axis='y', labelsize=26)  # Set y-axis tick label size
    axes[i].yaxis.set_label_coords(-0.12, 0.5)  # Adjust y-axis title position

    # Calculate and add mean 'x' and line between 'Pre' and 'Post'
    mean_pre = df1[df1['Replicate'] == 'Pre'][col].mean()
    mean_post = df1[df1['Replicate'] == 'Post'][col].mean()
    axes[i].annotate('x', xy=(0, mean_pre), xytext=(0, 0), textcoords='offset points', color='black', ha='center', fontsize=16)
    axes[i].annotate('x', xy=(1, mean_post), xytext=(0, 0), textcoords='offset points', color='black', ha='center', fontsize=16)
    axes[i].plot([0, 1], [mean_pre, mean_post], color='black', linestyle='--')

# Set common y-axis label for the first subplot
axes[0].set_ylabel('', fontsize=32)

# Adjust spacing between subplots
plt.tight_layout()

# Create a new figure for Prosser data
fig, axes = plt.subplots(1, 5, figsize=(25, 10), sharey=True)

# Loop over each column (D1-D5) and create the box plot for Prosser data
for i, col in enumerate(df2.columns[3:8]):
    sns.boxplot(x=df2['Replicate'], y=col, data=df2, ax=axes[i], palette=['#95c65c', '#95c65c'])
    axes[i].set_title(bin_ranges[i], fontsize=32)
    axes[i].set_xlabel('')
    axes[i].set_xticklabels(['Pre', 'Post'])
    axes[i].set_ylabel('')  # Remove y-axis label
    axes[i].tick_params(axis='y', labelsize=26)

    # Calculate and add mean 'x' and line between 'Pre' and 'Post'
    mean_pre = df2[df2['Replicate'] == 'Pre'][col].mean()
    mean_post = df2[df2['Replicate'] == 'Post'][col].mean()
    axes[i].annotate('x', xy=(0, mean_pre), xytext=(0, 0), textcoords='offset points', color='black', ha='center', fontsize=16)
    axes[i].annotate('x', xy=(1, mean_post), xytext=(0, 0), textcoords='offset points', color='black', ha='center', fontsize=16)
    axes[i].plot([0, 1], [mean_pre, mean_post], color='black', linestyle='--')

# Set common y-axis label for the first subplot
axes[0].set_ylabel('Total Root Length (mm)', fontsize=32)

# Adjust spacing between subplots
plt.tight_layout()

# Show the plots
plt.show()