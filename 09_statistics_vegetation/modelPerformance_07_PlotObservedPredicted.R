# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Plot observed vs mean predicted foliar cover per scale
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2021-04-18
# Usage: Script should be executed in R 4.0.0+.
# Description: "Plot observed vs mean predicted foliar cover per scale" creates a plot showing the observed vs mean predicted foliar cover values with theoretical 1:1 ratio line and loess smoothed conditional mean.
# ---------------------------------------------------------------------------

# Set map classes
map_classes = c('alnus', 'betshr_nojan', 'bettre', 'dectre', 'dryas_nojan_noprec',
                'empnig_nojan', 'erivag_noswi', 'picgla', 'picmar', 'rhoshr',
                'salshr', 'sphagn', 'vaculi_nojan', 'vacvit', 'wetsed')
upper_limits = c(80,
                 180,
                 50,
                 50,
                 40,
                 150,
                 50,
                 120,
                 120,
                 250,
                 180,
                 80,
                 200,
                 200,
                 80
                 )

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap',
                    'Data/Data_Output/model_results/round_20210402/final',
                    sep = '/')

# Import required libraries
library(dplyr)
library(ggplot2)
library(ggpmisc)
library(hexbin)
library(readxl)
library(tidyr)
library(gridExtra)
library(scales)

for (map_class in map_classes) {
  # Define file directory
  class_folder = paste(data_folder,
                       '/',
                       map_class,
                       sep = '')
  plots_folder = paste(class_folder,
                       'plots',
                       sep = '/')
  
  # Define input and output files
  native_file = paste(class_folder,
                      'NorthAmericanBeringia_Region.csv',
                      sep = '/')
  grid_file = paste(class_folder,
                    'ScaledData_grid.csv',
                    sep = '/')
  ecoregion_file = paste(class_folder,
                         'ScaledData_ecoregion.csv',
                         sep = '/')
  
  # Read statewide model results for native resolution into data frame
  native_results = read.csv(native_file)
  native_results = native_results %>%
    mutate(scale = '10 � 10 m Map Resolution') %>%
    select(scale, cover, prediction)
  
  # Read statewide model results for grid resolution into data frame
  grid_results = read.csv(grid_file)
  grid_results = grid_results %>%
    mutate(scale = 'Scaled by 10 � 10 km Grids') %>%
    select(scale, cover, prediction)
  
  # Read statewide model results for ecoregion scale into data frame
  ecoregion_results = read.csv(ecoregion_file)
  ecoregion_results = ecoregion_results %>%
    mutate(scale = 'Scaled by Unified Ecoregions') %>%
    select(scale, cover, prediction)
  
  # Bind rows
  scaled_results = rbind(grid_results, ecoregion_results)
  
  # Set plot theme
  font = theme(strip.text = element_text(size = 12, color = 'black'),
               strip.background = element_rect(color = 'black', fill = 'white'),
               axis.text = element_text(size = 10),
               axis.text.x = element_text(color = 'black'),
               axis.text.y = element_text(color = 'black'),
               axis.title = element_text(size = 12),
               axis.title.x = element_text(margin = margin(t = 10)),
               axis.title.y = element_text(margin = margin(r = 10))
  )
  
  # Retrieve plot upper count limit
  upper_limit = upper_limits[match(map_class, map_classes)]
  
  # Plot native resolution results
  map_plot = ggplot(data = native_results, aes(x = cover, y = prediction)) +
    theme_bw() +
    font +
    geom_bin2d(data = native_results,
               aes(x = cover, y = prediction,
                   fill = ..count..),
               inherit.aes = FALSE,
               bins = 21) +
    scale_fill_viridis_c(lim = c(0, upper_limit), na.value = '#f8eb20') +
    geom_segment(x = 0,
                 y = 0,
                 xend = 100,
                 yend = 100,
                 size = 0.5,
                 linetype = 1) +
    labs(x = 'Observed foliar cover (%)', y = 'Predicted foliar cover (%)') +
    coord_fixed(ratio = 1) +
    scale_x_continuous(breaks = seq(0, 100, by = 10), limits = c(-6, 100), expand = c(0.01, 0)) +
    scale_y_continuous(breaks = seq(0, 100, by = 10), limits = c(-6, 100), expand = c(0.02, 0))
  
  # Plot native resolution results
  scaled_plot = ggplot(data = scaled_results, aes(x = cover, y = prediction)) +
    theme_bw() +
    font +
    geom_point(alpha = 0.4,
               size = 2,
               color = '#005280') +
    geom_segment(x = 0,
                 y = 0,
                 xend = 60,
                 yend = 60,
                 size = 0.5,
                 linetype = 1) +
    facet_wrap(~scale, ncol = 2) +
    theme(panel.spacing = unit(2, 'lines')) +
    labs(x = 'Observed foliar cover (%)', y = 'Predicted foliar cover (%)') +
    coord_fixed(ratio = 1) +
    scale_x_continuous(breaks=seq(0, 60, by = 10), limits = c(0, 60), expand = c(0.01, 0)) +
    scale_y_continuous(breaks=seq(0, 60, by = 10), limits = c(0, 60), expand = c(0.02, 0))
  
  # Save jpgs at 600 dpi
  map_output = paste(plots_folder,
                     'Figure_ObservedPredicted_MapResolution.jpg',
                     sep = '/')
  scaled_output = paste(plots_folder,
                        'Figure_ObservedPredicted_Scaled.jpg',
                        sep = '/')
  ggsave(map_output,
         plot = map_plot,
         device = 'jpeg',
         path = NULL,
         scale = 1,
         width = 5,
         height = 5,
         units = 'in',
         dpi = 600,
         limitsize = TRUE)
  ggsave(scaled_output,
         plot = scaled_plot,
         device = 'jpeg',
         path = NULL,
         scale = 1,
         width = 7.4,
         height = 4,
         units = 'in',
         dpi = 600)
  print(map_class)
}