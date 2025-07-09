# ---------------------------------------------------------------------------
# Plot foliar cover performance
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-06-19
# Usage: Script should be executed in R 4.1.0+.
# Description: "Plot foliar cover performance" plots the performance of all foliar cover models.
# ---------------------------------------------------------------------------

# Import libraries
library(dplyr)
library(fs)
library(ggplot2)
library(ggtext)
library(plotly)
library(RColorBrewer)
library(readr)
library(tibble)
library(tidyr)
library(htmlwidgets)

# Set root directory
drive = 'C:'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
performance_file = path(drive, root_folder, 'Data_Output/model_results/round_20241124/performance_table.csv')

# Process performance data
performance_data = read_csv(performance_file) %>%
  mutate(inv_rmse_site = round((100 - (rmse_site/cover_mean) * 100), digits=0)) %>%
  mutate(inv_rmse_scaled = round((100 - (rmse_scaled/cover_mean) * 100), digits=0))

# Identify margin specifications
margin_specs = list(l = 50, r = 50,
                    b = 50, t = 100,
                    pad = 20)

# Combine plots
comparison_plot = make_subplots(rows=1, cols=2, width=800, height=400)

# Create site plot
site_plot = performance_data %>%
  plot_ly(hoverinfo = 'text',
          text = ~paste('</br>', indicator_name,
                        '</br> R squared:', r2_site,
                        '</br> RMSE: ', rmse_site,
                        '</br> Mean Cover (>3%): ', cover_mean,
                        '</br> Number > 3%: ', n_presence)) %>%
  layout(title = 'Comparison of site-scale R squared and inverse standardized RMSE',
         shapes = list(list(
           type = "line", 
           x0 = 0, 
           x1 = 1, 
           xref = "x",
           y0 = 0, 
           y1 = 100,
           yref = "y",
           line = list(width=0.5, color = "black")))) %>%
  add_trace(type = 'scatter', 
            mode = 'markers',
            x = ~r2_site,
            y = ~inv_rmse_site,
            color = ~life_form,
            marker = list(size = 8,
                          line = list(color = 'black',
                                      width = 0.5))) %>%
  layout(margin = margin_specs)

# Create scaled plot
scaled_plot = performance_data %>%
  plot_ly(hoverinfo = 'text',
          text = ~paste('</br>', indicator_name,
                        '</br> R squared:', r2_scaled,
                        '</br> RMSE: ', rmse_scaled,
                        '</br> Mean Cover (>3%): ', cover_mean,
                        '</br> Number > 3%: ', n_presence)) %>%
  layout(title = 'Comparison of landscape-scale R squared and inverse standardized RMSE',
         shapes = list(list(
           type = "line", 
           x0 = 0, 
           x1 = 1, 
           xref = "x",
           y0 = 0, 
           y1 = 100,
           yref = "y",
           line = list(width=0.5, color = "black")))) %>%
  add_trace(type = 'scatter', 
            mode = 'markers',
            x = ~r2_scaled,
            y = ~inv_rmse_scaled,
            color = ~life_form,
            showlegend=FALSE,
            marker = list(size = 8,
                          line = list(color = 'black',
                                      width = 0.5))) %>%
  layout(margin = margin_specs)

# Save plot
output_plot = 'C:/Users/timmn/Documents/export/performance_plot.html'
saveWidget(as_widget(comparison_plot), output_plot)
