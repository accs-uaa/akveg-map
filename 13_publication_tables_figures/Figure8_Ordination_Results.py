# ---------------------------------------------------------------------------
# Plot results of ordination performance assessment
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-07-09
# Usage: Script should be executed in R 4.1.0+.
# Description: "Plot results of ordination performance assessment" plots bar charts comparing the performance of three vegetation maps relative to the information preserved in clusters from 3-axis NMDS ordinations.
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

# Set round date
round_date = 'round_20241124'

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map'

# Define input file
ordination_input = os.path.join(drive, root_folder,
                                'Data/Data_Output/ordination_results', round_date,
                                '00_Subregion_Performance.xlsx')

# Define output files
html_output = os.path.join(drive, root_folder,
                           'Documents/Manuscript_FoliarCover_FloristicGradients/figures',
                           'Figure8_Ordination_Results.html')
plot_output = os.path.join(drive, root_folder,
                           'Documents/Manuscript_FoliarCover_FloristicGradients/figures',
                           'Figure8_Ordination_Results.svg')

# Assign treeless and treed systems
treeless_list = ['Arctic Coastal Plain', 'Arctic Foothills & Mountains',
                 'Seward Peninsula', 'Alaska Peninsula Mountains', 'Kodiak Southwest',
                 'Southwest Mountains', 'Bristol Bay', 'Eastern Interior', 'Denali North',
                 'Alaska Pacific Western']
tree_list = ['Bristol Bay', 'Alaska Western', 'Alaska-Yukon Northwest',
             'Yukon Flats', 'Eastern Interior', 'Wrangell-Tetlin',
             'Denali North', 'Wrangell-St. Elias', 'Denali South',
             'Nelchina Uplands', 'Susitna Valley', 'Alaska Pacific Western']

# Read ordination results
ordination_data = pd.read_excel(ordination_input, sheet_name='summary')
ordination_data['map1'] = ordination_data['scaled_ind'] * 100
ordination_data['map2'] = ordination_data['scaled_akvwc'] * 100
ordination_data['map3'] = ordination_data['scaled_lf'] * 100

# Select columns
ordination_data = ordination_data[['subregion', 'focal_unit', 'map1', 'map2', 'map3']]

# Add a row id column
ordination_data = ordination_data.reset_index().rename(columns={'index': 'id'})

# Pivot data to long form
ordination_long = pd.wide_to_long(ordination_data,
                                  ['map'],
                                  i='id',
                                  j='value',
                                  sep='').reset_index()

# Create function to assign vegetation map names
def assign_map(value):
    if value == 1:
        map_name = 'AKVEG foliar cover'
    elif value == 2:
        map_name = 'AKVWC (fine classes)'
    elif value == 3:
        map_name = 'LANDFIRE 2023 EVT'
    else:
        map_name = 'error'
    return map_name

# Apply function to create new column
ordination_long['map_name'] = ordination_long['value'].apply(assign_map)

# Rename performance value
ordination_long = ordination_long.rename(columns={'map': 'performance'})

# Round performance to nearest percentage
ordination_long['performance'] = ordination_long['performance'].round(0).astype(int)

# Split data into treeless and treed groups
treeless_data = ordination_long[(ordination_long['subregion'].isin(treeless_list)) &
                                (ordination_long['focal_unit'].isin(['all', 'non-forest']))]
tree_data = ordination_long[(ordination_long['subregion'].isin(tree_list)) &
                            (ordination_long['focal_unit'].isin(['all', 'forest']))]

# Define custom fill
map_colors = {
    'LANDFIRE 2023 EVT': '#000000',
    'AKVWC (fine classes)': '#000000',
    'AKVEG foliar cover': '#000000'
}
map_patterns = {
    'LANDFIRE 2023 EVT': '.',
    'AKVWC (fine classes)': '\\',
    'AKVEG foliar cover': 'x'
}

# Create treeless plot
treeless_plot = px.bar(treeless_data,
                       x='subregion',
                       y='performance',
                       color='map_name',
                       color_discrete_map=map_colors,
                       text='performance',
                       category_orders={'subregion': treeless_list})

# Replace colors with patterns
for trace in treeless_plot.data:
    map_name = trace.name
    pattern_shape = map_patterns.get(map_name, '')
    trace.marker.line.width = 1
    trace.marker.line.color = 'black'
    trace.marker.pattern.shape = pattern_shape
    trace.marker.pattern.fillmode = 'replace'
    trace.marker.pattern.fgcolor = 'black'
    trace.marker.pattern.size = 6
    trace.textposition = 'outside'
    trace.textfont = dict(size=14, color = 'black')

# Create tree plot
tree_plot = px.bar(tree_data,
                   x='subregion',
                   y='performance',
                   color='map_name',
                   color_discrete_map=map_colors,
                   text='performance',
                   category_orders={'subregion': tree_list})

# Replace colors with patterns
for trace in tree_plot.data:
    map_name = trace.name
    pattern_shape = map_patterns.get(map_name, '')
    trace.marker.line.width = 1
    trace.marker.line.color = 'black'
    trace.marker.pattern.shape = pattern_shape
    trace.marker.pattern.fillmode = 'replace'
    trace.marker.pattern.fgcolor = 'black'
    trace.marker.pattern.size = 6
    trace.textposition = 'outside'
    trace.textfont = dict(size=14, color='black')

# Create combined plot
combined_plot = make_subplots(rows=2, cols=1,
                              subplot_titles=('Treeless subregions and/or focal units',
                                              'Treed subregions and/or focal units'),
                              horizontal_spacing=0.1,
                              shared_yaxes=False)
for trace in treeless_plot.data:
    combined_plot.add_trace(trace, row=1, col=1)
for trace in tree_plot.data:
    trace.showlegend = False
    combined_plot.add_trace(trace, row=2, col=1)

# Style the plot
combined_plot.update_layout(
    barmode='group',
    template='plotly_white',
    title=None,
    width=1000,
    height=1200,
    showlegend=True,
    font=dict(size=18, color='black'),
    xaxis=dict(tickfont=dict(size=16, color='black')),
    yaxis=dict(range=[0, 102],
               tick0=0,
               dtick=20,
               tickfont=dict(size=16, color='black'),
               title=dict(text='Relative performance %')
               ),
    xaxis2=dict(tickfont=dict(size=16, color='black')),
    yaxis2=dict(range=[0, 102],
               tick0=0,
               dtick=20,
               tickfont=dict(size=16, color='black'),
               title=dict(text='Relative performance %'),
            ),
    legend=dict(orientation='h',
                yanchor='bottom',
                y=1.05,
                xanchor='center',
                x=0.5)
)

# Rotate the x-axis labels
combined_plot.update_xaxes(tickangle=45)

# Update the sort order of the x-axes
combined_plot.update_xaxes(
    categoryorder='array',
    categoryarray=treeless_list,
    row=1, col=1
)
combined_plot.update_xaxes(
    categoryorder='array',
    categoryarray=tree_list,
    row=2, col=1
)

# Increase the font size of the subplot titles
combined_plot.update_annotations(font=dict(size=20, color='black'))

# Export to HTML (interactive) and SVG (publication)
combined_plot.write_html(html_output)
pio.write_image(combined_plot, plot_output, format='svg', width=1000, height=1200, scale=1)
