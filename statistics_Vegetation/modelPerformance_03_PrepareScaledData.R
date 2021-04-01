# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Scaled Data for Accuracy Assessment
# Author: Timm Nawrocki
# Last Updated: 2021-04-01
# Usage: Should be executed in R 4.0.0+.
# Description: "Prepare Scaled Data for Accuracy Assessment" calculates the mean observed and predicted foliar cover grouped by the minor grid units and ecoregions for input into an accuracy assessment script.
# ---------------------------------------------------------------------------

# Set map classes
map_classes = c('alnus', 'betshr', 'bettre', 'dectre', 'dryas',
                'empnig', 'erivag', 'picgla', 'picmar', 'rhoshr',
                'salshr', 'sphagn', 'vaculi', 'vacvit', 'wetsed')

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap',
                    'Data/Data_Output/model_results/round_20210316/final',
                    sep = '/')

# Install required libraries if they are not already installed.
Required_Packages <- c("dplyr", "readxl", "writexl", "tidyr")
New_Packages <- Required_Packages[!(Required_Packages %in% installed.packages()[,"Package"])]
if (length(New_Packages) > 0) {
  install.packages(New_Packages)
}
# Import required libraries.
library(dplyr)
library(readxl)
library(writexl)
library(tidyr)

# Loop through all map classes and prepare scaled data
for (map_class in map_classes) {
  # Define file directory
  class_folder = paste(data_folder,
                       '/',
                       map_class,
                       sep = '')
  
  # Define input and output files
  input_file = paste(class_folder,
                     'NorthAmericanBeringia_Region.csv',
                     sep = '/')
  grid_file = paste(class_folder,
                    'ScaledData_grid.csv',
                    sep = '/')
  ecoregion_file = paste(class_folder,
                         'ScaledData_ecoregion.csv',
                         sep = '/')
  
  # Read statewide model results into data frame
  model_results = read.csv(input_file)
  
  # Summarize model results by minor grid
  grid_results = model_results %>%
    group_by(minor) %>%
    summarize(cover = mean(cover),
              prediction = mean(prediction),
              num_sites = n()) %>%
    filter(num_sites >= 3)
  
  # Summarize model results by ecoregion
  ecoregion_results = model_results %>%
    group_by(ecoregion) %>%
    summarize(cover = mean(cover),
              prediction = mean(prediction),
              num_sites = n()) %>%
    filter(num_sites >= 15)
  
  # Save output files
  write.csv(grid_results, file = grid_file, fileEncoding = 'UTF-8')
  write.csv(ecoregion_results, file = ecoregion_file, fileEncoding = 'UTF-8')
}