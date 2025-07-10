# ---------------------------------------------------------------------------
# Plot characteristics of training and validation data
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-07-09
# Usage: Script should be executed in R 4.1.0+.
# Description: "Plot characteristics of training and validation data" plots stacked bar charts for the cover version and temporal range of data.
# ---------------------------------------------------------------------------

# Import libraries
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
import os
import kaleido

# Initialize kaleido
kaleido.get_chrome_sync()

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map'

# Define input file
training_input = os.path.join(drive, root_folder,
                              'Data/Data_Input/species_data',
                              '00_training_data_summary.xlsx')

# Define output files
html_output = os.path.join(drive, root_folder,
                           'Documents/Manuscript_FoliarCover_FloristicGradients/figures',
                           'Figure3b_Training_Validation_Data.html')
plot_output = os.path.join(drive, root_folder,
                           'Documents/Manuscript_FoliarCover_FloristicGradients/figures',
                           'Figure3b_Training_Validation_Data.svg')

# Read training data
training_data = pd.read_excel(training_input, sheet_name='training')

# Extract years from observation dates
training_data['obs_datetime'] = pd.to_datetime(training_data['observe_date'])
training_data['obs_year'] = training_data['obs_datetime'].dt.year
training_data['obs_year'] = pd.to_numeric(training_data['obs_year'], errors='coerce')

# Define a function to assign the year interval
def assign_year(obs_year):
    if (obs_year >= 2000) & (obs_year < 2005):
        return '2000-2004'
    elif (obs_year >= 2005) & (obs_year < 2010):
        return '2005-2009'
    elif (obs_year >= 2010) & (obs_year < 2015):
        return '2010-2014'
    elif (obs_year >= 2015) & (obs_year < 2020):
        return '2015-2019'
    elif (obs_year >= 2020) & (obs_year < 2025):
        return '2020-2024'
    else:
        return 'omit'

# Apply function to create new column
training_data['year_interval'] = training_data['obs_year'].apply(assign_year)

# Summarize data by cover version
cover_data = training_data.groupby(['cover_version', 'region']).size().reset_index(name='count')

# Summarize data by year interval
year_data = training_data.groupby(['year_interval', 'region']).size().reset_index(name='count')

# Define custom fill
cover_colors = {
    'absolute': '#000000',
    'top': '#000000'
}
cover_patterns = {
    'absolute': 'x',
    'top': '\\'
}
year_colors = {
    '2000-2004': '#E1E5EE',
    '2005-2009': '#B2B7C3',
    '2010-2014': '#838897',
    '2015-2019': '#535A6C',
    '2020-2024': '#242B40'
}

# Define x-axis ordering
category_order = ['Arctic Northern',
                  'Arctic Western',
                  'Aleutian-Kamchatka',
                  'Alaska Southwest',
                  'Alaska Western',
                  'Alaska-Yukon Northern',
                  'Alaska-Yukon Central',
                  'Alaska-Yukon Southern',
                  'Alaska Pacific']

# Create cover version plot
cover_plot = px.bar(cover_data,
                    x='region',
                    y='count',
                    color='cover_version',
                    color_discrete_map=cover_colors,
                    category_orders={'region': category_order})

# Replace colors with patterns
for trace in cover_plot.data:
    map_name = trace.name
    pattern_shape = cover_patterns.get(map_name, '')
    trace.marker.line.width = 1
    trace.marker.line.color = 'black'
    trace.marker.pattern.shape = pattern_shape
    trace.marker.pattern.fillmode = 'replace'
    trace.marker.pattern.fgcolor = 'black'
    trace.marker.pattern.size = 6

# Create year-range plot
year_plot = px.bar(year_data,
                   x='region',
                   y='count',
                   color='year_interval',
                   color_discrete_map=year_colors,
                   category_orders={'region': category_order})
year_plot.update_traces(marker_line_color='black', marker_line_width=1)

# Create combined plot
combined_plot = make_subplots(rows=1, cols=2,
                              subplot_titles=('Site visits by top or absolute cover', 'Site visits by year'),
                              horizontal_spacing=0.1,
                              shared_yaxes=True)
for trace in cover_plot.data:
    trace.name = f'cover: {trace.name}'
    trace.legendgroup = 'group1'
    combined_plot.add_trace(trace, row=1, col=1)
for trace in year_plot.data:
    trace.name = f'year: {trace.name}'
    trace.legendgroup = 'group2'
    combined_plot.add_trace(trace, row=1, col=2)

# Style the plot
combined_plot.update_layout(
    barmode='stack',
    template='plotly_white',
    title=None,
    width=1000,
    height=700,
    showlegend=True,
    font=dict(size=18, color='black'),
    xaxis=dict(tickfont=dict(size=16, color='black')),
    yaxis=dict(tickfont=dict(size=16, color='black')),
    xaxis2=dict(tickfont=dict(size=16, color='black')),
    yaxis2=dict(tickfont=dict(size=16, color='black'))
)

# Rotate the x-axis labels
combined_plot.update_xaxes(tickangle=45)

# Update the sort order of the x-axes
combined_plot.update_xaxes(
    categoryorder='array',
    categoryarray=category_order,
    row=1, col=1
)
combined_plot.update_xaxes(
    categoryorder='array',
    categoryarray=category_order,
    row=1, col=2
)

# Increase the font size of the subplot titles
combined_plot.update_annotations(font=dict(size=20, color='black'))

# Add annotations for x and y titles
combined_plot.add_annotation(
    xref='x domain',
    yref='y domain',
    x=0,
    y=-0.2,
    text='Region',
    showarrow=False,
    xanchor="center",
    yanchor="top",
    font=dict(size=20, color='black')
)

combined_plot.add_annotation(
    xref='x domain',
    yref='y domain',
    x=-0.18,
    y=0.5,
    text='Site visit count',
    showarrow=False,
    xanchor="right",
    yanchor="middle",
    textangle=-90,
    font=dict(size=20, color='black')
)

# Export to HTML (interactive) and SVG (publication)
combined_plot.write_html(html_output)
pio.write_image(combined_plot, plot_output, format='svg', width=1000, height=700, scale=1)
