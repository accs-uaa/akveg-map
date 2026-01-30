# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Rescale data for landscape scale accuracy assessment
# Author: Timm Nawrocki
# Last Updated: 2025-07-24
# Usage: Should be executed in R 4.5.0+.
# Description: "Rescale data for landscape scale accuracy assessment" assigns all site visits from the cross-validation results per indicator to a predefined 10 km grid, removes grids that contain less than 3 points, and calculates mean observed and predicted cover values.
# ---------------------------------------------------------------------------

# Import required libraries.
library(dplyr)
library(fs)
library(readr)
library(sf)
library(tibble)

# Set round date
round_date = 'round_20241124'

# Define indicators
indicators = c('alnus', 'betshr', 'bettre', 'brotre', 'dryas', 'dsalix', 'empnig', 'erivag', 'mwcalama',
                'ndsalix', 'nerishr', 'picgla', 'picmar', 'picsit', 'poptre', 'populbt', 'rhoshr', 'rubspe',
                'sphagn', 'tsumer', 'vaculi', 'vacvit', 'wetsed')

# Set root directory
drive = 'C:'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = path(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map')
input_folder = path(project_folder, 'Data/Data_Output/model_results', round_date)
region_folder = path(project_folder, 'Data/Data_Input/region_data')
input_geodatabase = path(project_folder, 'Data/AKVEG_Regions.gdb')

# Define input files
region_input = path(region_folder, 'AlaskaYukon_Regions_v2.0_3338.shp')

# Read input grid
input_grid = st_read(dsn = input_geodatabase, layer = 'AlaskaYukon_010_Tiles_3338') %>%
  # Create id
  rowid_to_column('grid_id') %>%
  # Select fields
  select(grid_id, Shape)

# Read input regions
region_data = st_read(region_input) %>%
  select(region)

# Loop through all map classes and prepare scaled data
for (indicator in indicators) {
  
  # Define indicator folder
  indicator_folder = path(input_folder, indicator)
  
  # Define input and output files
  indicator_input = path(indicator_folder, paste(indicator, '_results.csv', sep = ''))
  
  # Define output file
  scaled_output = path(indicator_folder, paste(indicator, '_scaled.csv', sep = ''))
  region_output = path(indicator_folder, paste(indicator, '_region.csv', sep = ''))
  
  # Read input data and extract grid and region
  input_data = read_csv(indicator_input) %>%
    # Select fields
    select(st_vst, cvr_pct, prediction, cent_x, cent_y) %>%
    # Convert geometries to points with EPSG 4269
    st_as_sf(x = ., coords = c('cent_x', 'cent_y'), crs = 3338, remove = FALSE) %>%
    # Join grid data
    st_join(x = ., input_grid, join = st_within) %>%
    # Join region data
    st_join(x = ., region_data, join = st_within) %>%
    # Drop geometry
    st_drop_geometry()
  
  # Summarize data by grid
  grid_summary = input_data %>%
    group_by(grid_id) %>%
    summarize(n_stvst = n(),
              mean_cvr_pct = mean(cvr_pct),
              mean_prediction = mean(prediction)) %>%
    # Remove grids with less than 3 sites
    filter(n_stvst >= 3)
  
  # Summarize data by region
  region_summary = input_data %>%
    group_by(region) %>%
    summarize(n_stvst = n(),
              mean_cvr_pct = mean(cvr_pct),
              mean_prediction = mean(prediction)) %>%
    # Remove regions with less than 50 sites
    filter(n_stvst >= 50)
  
  # Export data
  write.csv(grid_summary, file = scaled_output, fileEncoding = 'UTF-8')
  write.csv(region_summary, file = region_output, fileEncoding = 'UTF-8')
}