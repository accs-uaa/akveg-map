# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compile Selected Sites (General)
# Author: Timm Nawrocki
# Last Updated: 2021-04-02
# Usage: Must be executed in R 4.0.0+.
# Description: "Compile Selected Sites (General)" generates a table of unique sites used in modeling of all species (or, in the case of aerial data, selected into at least one model)
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input',
                    sep = '/')
cover_folder = paste(data_folder,
                     'species_data',
                     sep ='/')
sites_folder = paste(data_folder,
                     'sites',
                     sep ='/')

# Define output file
output_file = paste(sites_folder,
                    'sites_selected.csv',
                    sep = '/')

# Define mapped groups
map_groups = c('alnus',
               'betshr',
               'bettre',
               'dectre',
               'empnig',
               'erivag',
               'picgla',
               'picmar',
               'rhoshr',
               'salshr',
               'sphagn',
               'vaculi',
               'vacvit',
               'wetsed')

# Import required libraries for geospatial processing: dplyr, readxl, stringr, and tidyr.
library(dplyr)
library(lubridate)
library(readxl)
library(stringr)
library(tidyr)

# Create empty list to store cover files
cover_files = list()

# Iterate through target paths and create file list
for (group in map_groups) {
  
  # Designate input cover file
  cover_file = paste(cover_folder,
                     '/',
                     'mapClass_',
                     group,
                     '.csv',
                     sep = '')
  
  # If cover file exists, add it to file list
  if (file.exists(cover_file)) {
    cover_files = append(cover_files, list(cover_file))
  }
}

# Read cover files into list
cover_list = lapply(cover_files, read.csv, fileEncoding = 'UTF-8')

# Combine cover list into dataframe
cover_data = do.call(rbind, cover_list)

# Generate table of unique sites
sites_selected = cover_data %>%
  select(site_code, project, year, day, perspective, cover_method, POINT_X, POINT_Y) %>%
  mutate(cover_method = ifelse(perspective == 'aerial',
                               'semi-quantitative visual estimate (aerial)',
                               cover_method)) %>%
  mutate(cover_method = ifelse(project == 'NPS ARCN I&M' | project == 'NPS CAKN I&M',
                               'line-point intercept (spruce only)',
                               cover_method)) %>%
  distinct()

# Save output file
write.csv(sites_selected, file = output_file, fileEncoding = 'UTF-8', row.names=FALSE)