# ---------------------------------------------------------------------------
# Plot foliar cover performance combined
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-06-19
# Usage: Script should be executed in R 4.1.0+.
# Description: "Plot foliar cover performance combined" plots the performance of all foliar cover models in two panels for site scale and landscape scale results.
# ---------------------------------------------------------------------------

# Import libraries
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import os

# Set round date
round_date = 'round_20241124'

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map'

# Define input file
performance_file = os.path.join(drive, root_folder,
                                'Data/Data_Output/model_results', round_date,
                                'performance_table.csv')

# Define output files
html_output = os.path.join(drive, root_folder,
                           'Documents/Manuscript_FoliarCover_FloristicGradients/figures',
                           'figure4_performance.html')
plot_output = os.path.join(drive, root_folder,
                           'Documents/Manuscript_FoliarCover_FloristicGradients/figures',
                           'figure4_performance.svg')

# Process performance data
performance_data = pd.read_csv(performance_file)
performance_data['inv_rmse_site'] = round(
  1 - (performance_data['rmse_site']/performance_data['cover_mean']),
  2)
performance_data['inv_rmse_scaled'] = round(
  1 - (performance_data['rmse_scaled']/performance_data['cover_mean']),
  2)

# Create reference line shapes
shapes = [
    dict(type="line", x0=0.25, y0=0.4, x1=1, y1=0.4, xref="x", yref="y",
         line=dict(color="black", dash="dash", width=1)),
    dict(type="line", x0=0.25, y0=0.4, x1=0.25, y1=1, xref="x", yref="y",
         line=dict(color="black", dash="dash", width=1)),
    dict(type="line", x0=0.25, y0=0.4, x1=1, y1=0.4, xref="x2", yref="y2",
         line=dict(color="black", dash="dash", width=1)),
    dict(type="line", x0=0.25, y0=0.4, x1=0.25, y1=1, xref="x2", yref="y2",
         line=dict(color="black", dash="dash", width=1))
]

# Create axis label annotations
annotations = [
    # X-axis label (bottom center)
    dict(text='R squared',
         x=0.5, y=-0.2, xref="paper", yref="paper",
         showarrow=False, font=dict(size=16)
         ),
    # Y-axis label (left center, rotated)
    dict(text='Inverse standardized RMSE',
         x=-0.07, y=0.2, xref="paper", yref="paper",
         showarrow=False, textangle=-90, font=dict(size=16)
         )
]

# Create site plot
site_plot = px.scatter(performance_data,
                       x="r2_site",
                       y="inv_rmse_site",
                       custom_data=['indicator_name', 'rmse_site', 'cover_mean', 'n_presence'])
site_plot.update_traces(hovertemplate='%{customdata[0]}<br>' +
                                      'R squared: %{x}<br>' +
                                      'RMSE: %{customdata[1]}<br>' +
                                      'Mean Cover (>3%): %{customdata[2]}<br>' +
                                      'Sites > 3%: %{customdata[3]}')

# Create scaled plot
scaled_plot = px.scatter(performance_data,
                         x="r2_scaled",
                         y="inv_rmse_scaled",
                         custom_data=['indicator_name', 'rmse_scaled', 'cover_mean', 'n_grid'])
scaled_plot.update_traces(hovertemplate='%{customdata[0]}<br>' +
                                        'R squared: %{x}<br>' +
                                        'RMSE: %{customdata[1]}<br>' +
                                        'Mean Cover (>3%): %{customdata[2]}<br>' +
                                        'Grids > 1%: %{customdata[3]}')

# Create combined plot
combined_plot = make_subplots(rows=1, cols=2,
                              subplot_titles=('Site-scale', 'Landscape-scale'),
                              horizontal_spacing=0.1)
for trace in site_plot.data:
    trace.marker.update(size=10, color='rgba(0,132,168,0.4)', line=dict(color='black', width=1))
    combined_plot.add_trace(trace, row=1, col=1)
for trace in scaled_plot.data:
    trace.showlegend = False
    trace.marker.update(size=10, color='rgba(0,132,168,0.4)', line=dict(color='black', width=1))
    combined_plot.add_trace(trace, row=1, col=2)

# Style the plot
combined_plot.update_layout(
    template='plotly_white',
    title_text='Comparison of performance metrics calculated at site and landscape scales',
    legend_title_text='life form',
    width=1000,
    height=500,
    showlegend=True,
    font=dict(size=18),
    legend=dict(font=dict(size=16)),
    xaxis=dict(range=[0, 1], scaleanchor="y", tick0=0, dtick=0.2, tickfont=dict(size=15)),
    yaxis=dict(range=[0, 1], tick0=0, dtick=0.2, tickfont=dict(size=15)),
    xaxis2=dict(range=[0, 1], scaleanchor="y2", tick0=0, dtick=0.2, tickfont=dict(size=15)),
    yaxis2=dict(range=[0, 1], tick0=0, dtick=0.2, tickfont=dict(size=15)),
    shapes=shapes,
    annotations=annotations
)

# Export to HTML (interactive)
combined_plot.write_html(html_output)
combined_plot.write_image(plot_output, width=1000, height=500, scale=1)
