#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 09:56:16 2024

@author: johnfleck
Based on USBR Consumptive Uses and Losses data as released June 24, 2024: https://www.usbr.gov/uc/DocLibrary/reports.html
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns




# Load the expanded dataset
expanded_data_path = "CUvNF.csv"  
expanded_data = pd.read_csv(expanded_data_path)

# Clean and structure the data
expanded_data_cleaned = expanded_data[['Year', 'LFFlow', 'Colorado', 'Utah', 'Wyoming', 'New Mexico']].copy()

# Remove commas and convert numeric columns to float
expanded_data_cleaned['LFFlow'] = expanded_data_cleaned['LFFlow'].str.replace(',', '').astype(float)
states = ['Colorado', 'Utah', 'Wyoming', 'New Mexico']
for state in states:
    expanded_data_cleaned[state] = (
        expanded_data_cleaned[state]
        .astype(str)  # Convert to string if not already
        .str.replace(',', '')  # Remove commas
        .replace('nan', '0')  # Handle NaN values (replace with '0' or appropriate value)
        .astype(float)  # Convert back to float
    )

# Filter for post-1991 data
expanded_data_post_1991 = expanded_data_cleaned[expanded_data_cleaned['Year'] >= 1991]

# Create flow categories (low, medium, high) based on LFFlow
expanded_data_post_1991['FlowCategory'] = pd.qcut(
    expanded_data_post_1991['LFFlow'], q=3, labels=['Low', 'Medium', 'High'])

# Reshape the data for tiny multiples plot
melted_data = expanded_data_post_1991.melt(
    id_vars=['Year', 'LFFlow', 'FlowCategory'],
    value_vars=states, var_name='State', value_name='CU'
)

# Calculate mean CU for each state and flow category
mean_lines = melted_data.groupby(['State', 'FlowCategory'])['CU'].mean().reset_index()

# Function to plot scatter points and mean lines
def plot_state(data, **kwargs):
    # Plot scatter points
    sns.scatterplot(
        data=data, x='LFFlow', y='CU', hue='FlowCategory',
        palette=kwargs['palette'], alpha=0.7, ax=plt.gca()
    )
    # Add mean lines for the relevant flow category ranges
    state = data['State'].iloc[0]
    for _, row in mean_lines[mean_lines['State'] == state].iterrows():
        subset = data[data['FlowCategory'] == row['FlowCategory']]
        plt.hlines(
            y=row['CU'], xmin=subset['LFFlow'].min(), xmax=subset['LFFlow'].max(),
            color=kwargs['palette'][row['FlowCategory']], linestyle='--', linewidth=2
        )
        # Add labels with the mean above the line
        plt.text(
            subset['LFFlow'].min(), row['CU'] + 1500, f'{row["CU"]:.3g}',
            color='black', fontsize=9
        )

# Create tiny multiples with FacetGrid
g = sns.FacetGrid(melted_data, col='State', col_wrap=2, height=4, sharey=False, sharex=True)

# Map the plotting function to each facet
color_palette = {'Low': 'red', 'Medium': 'blue', 'High': 'green'}
g.map_dataframe(plot_state, palette=color_palette)

# Adjust layout and titles
g.add_legend(title='Flow Category')
g.set_axis_labels('Flow at Lee\'s Ferry (LFFlow)', 'Consumptive Use (CU)')
g.set_titles('{col_name}')

# Adjust space and add main title
plt.subplots_adjust(top=0.9)
g.fig.suptitle('Consumptive Use vs. Flow at Lee\'s Ferry (Post-1991)\nby State and Flow Category with Mean Lines', fontsize=16)

# Show the plot
plt.show()