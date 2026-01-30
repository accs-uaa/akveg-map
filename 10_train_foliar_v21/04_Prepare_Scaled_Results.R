# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Rescale data for landscape scale accuracy assessment
# Author: Timm Nawrocki
# Last Updated: 2025-06-18
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
round_date = 'round_20251003_lgbm_embRand_s1_s2_topo'

# Define indicators
indicators = c('alnus', 'bderishr', 'betshr', 'bettre', 'brotre', 'chaang', 'dryas', 'dsalix', 'empnig', 'erivag', 
              'fesalt', 'leymol',  'mwcalama', 'ndsalix', 'nerishr', 'picgla', 'picmar', 'picsit', 'poptre', 'populbt',
              'rhoshr', 'rubcha', 'rubspe', 'senpse', 'sphagn', 'tsumer', 'vaculi', 'vacvit', 'wetsed')

# Set root directory
drive = '/data/gis'
root_folder = 'raster_base/Alaska/AKVegMap/akveg-working'

# Define input folders
project_folder = path(drive, root_folder) #, 'Projects/VegetationEcology/AKVEG_Map/Data')
species_input_folder = path(project_folder, 'Data_Input/species_data')
input_folder = path(project_folder, 'Data_Output/model_results', round_date)
# input_geodatabase = path(project_folder, 'AKVEG_Regions.gdb')
input_geodatabase = path('/data/gis', 'raster_base/Alaska/AKVegMap/gdrive_akveg/AKVEG ABR/gis/akveg_areas', 'AKVEG_Regions.gdb')

# Read input grid
input_grid = st_read(dsn = input_geodatabase, layer = 'AlaskaYukon_010_Tiles_3338') %>%
  # Create id
  rowid_to_column('grid_id') %>%
  # Select fields
  select(grid_id, Shape)

# Loop through all map classes and prepare scaled data
for (indicator in indicators) {
  
  # Define indicator folder
  indicator_folder = path(input_folder, indicator)
  
  # Define input and output files
  species_input_file = path(species_input_folder, paste('cover_', indicator, '_3338.csv', sep=''))
  input_file = path(indicator_folder, paste(indicator, '_results.csv', sep = ''))
  
  # Define output file
  output_file = path(indicator_folder, paste(indicator, '_scaled.csv', sep = ''))
  species_input = read_csv(species_input_file) %>%
    select(st_vst, cent_x, cent_y)
  # Read input data and extract grid
  scaled_data = read_csv(input_file) %>%
    left_join(species_input) %>%
    # Select fields
    select(st_vst, cvr_pct, prediction, cent_x, cent_y) %>%
    # Convert geometries to points with EPSG 4269
    st_as_sf(x = ., coords = c('cent_x', 'cent_y'), crs = 3338, remove = FALSE) %>%
    # Join grid data
    st_join(x = ., input_grid, join = st_within) %>%
    # Drop geometry
    st_drop_geometry() %>%
    # Summarize data by grid
    group_by(grid_id) %>%
    summarize(n_stvst = n(),
              mean_cvr_pct = mean(cvr_pct),
              mean_prediction = mean(prediction)) %>%
    # Remove grids with less than 3 sites
    filter(n_stvst >= 3)
  
  # Export data
  write.csv(scaled_data, file = output_file, fileEncoding = 'UTF-8')
}
