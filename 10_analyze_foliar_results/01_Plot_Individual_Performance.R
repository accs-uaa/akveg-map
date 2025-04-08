# ---------------------------------------------------------------------------
# Plot foliar cover performance
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-02-20
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
library(readxl)
library(tibble)
library(tidyr)
library(htmlwidgets)

# Set root directory
drive = 'C:'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
results_file = path(drive, root_folder, 'Data_Output/model_results/AKVEG_Foliar_v2.0_20250103.xlsx')

# Process classifier importances
classifier_data = read_xlsx(results_file, sheet='comparison') %>%
  select(target_abbr, name, r2_score, rmse, mean_cvr, top_absence, model, n_presence)

# Create standardized RMSE
classifier_data = classifier_data %>%
  mutate(nrm_rmse = round(((rmse/mean_cvr) * 100), digits=0)) %>%
  mutate(inv_rmse = 100-nrm_rmse)

# Plot classifier importance
mrg <- list(l = 50, r = 50,
            b = 50, t = 100,
            pad = 20)

comparison_plot = classifier_data %>%
  plot_ly(width = 575,
          height = 490,
          hoverinfo = 'text',
          text = ~paste('</br>', name,
                        '</br> R squared:', r2_score,
                        '</br> RMSE: ', rmse,
                        '</br> Mean Cover (>3%): ', mean_cvr,
                        '</br> Number > 3%: ', n_presence)) %>%
  layout(title = 'Comparison of R squared and inverse standardized RMSE',
         xaxis = list(title = 'R squared'), 
         yaxis = list(title = 'Inverse Standardized RMSE'),
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
            x = ~r2_score,
            y = ~inv_rmse,
            color = ~model,
            marker = list(size = 8,
                          line = list(color = 'black',
                                      width = 0.5))) %>%
  layout(margin = mrg)

# Show plot
comparison_plot

# Save plot
output_plot = 'C:/Users/timmn/Documents/export/performance_plot.html'
saveWidget(as_widget(comparison_plot), output_plot)
