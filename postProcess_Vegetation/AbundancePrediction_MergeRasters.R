# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge Predicted Rasters
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2021-04-01
# Usage: Code chunks must be executed sequentially in R Studio or R Studio Server installation.
# Description: "Merge Predicted Rasters" merges the predicted grid rasters into a single output raster.
# ---------------------------------------------------------------------------

# Set root directory
root_folder = '/home/twn_rstudio'

# Set map class folder
map_class = 'alnus'

# Define input folder
input_folder = paste(root_folder,
                      'predicted_rasters',
                      map_class,
                      sep = '/'
                      )

# Define output folder
output_folder = paste(root_folder,
                      'rasters_final',
                      map_class,
                      sep = '/'
)

# Create output directory if it does not exist
if (!file.exists(output_folder)) {
  dir.create(output_folder)
}

# Import required libraries for geospatial processing: sp, raster, rgdal, and stringr.
library(sp)
library(raster)
library(rgdal)

# Define major grids
major_grids = c('A5', 'A6', 'A7', 'A8',
                'B4', 'B5', 'B6', 'B7', 'B8',
                'C4', 'C5', 'C6', 'C7', 'C8',
                'D4', 'D5', 'D6',
                'E4', 'E5', 'E6')

# Iterate through major grids and merge raster tiles
for (major_grid in major_grids) {
  
  # Define output file
  output_raster = paste(output_folder, 
                        '/',
                        'NorthAmericanBeringia_',
                        map_class,
                        '_',
                        major_grid,
                        '.tif',
                        sep = '')
  
  # Generate output raster if it does not already exist
  if (!file.exists(output_raster)) {
    
    # Generate list of raster img files from input folder
    raster_files = list.files(path = input_folder,
                              pattern = paste('.*', major_grid, '.*.img$', sep = ''),
                              full.names = TRUE)
    count = length(raster_files)
    
    # Convert list of files into list of raster objects
    start = proc.time()
    print(paste('Compiling ', toString(count), ' rasters for grid ', major_grid, '...'))
    raster_objects = lapply(raster_files, raster)
    # Add function and filename attributes to list
    raster_objects$fun = max
    raster_objects$filename = output_raster
    raster_objects$overwrite = TRUE
    raster_objects$datatype = 'INT1U'
    raster_objects$progress = 'text'
    raster_objects$format = 'GTiff'
    raster_objects$options = c('TFW=YES')
    end = proc.time() - start
    print(paste('Completed in ', end[3], ' seconds.', sep = ''))
    
    # Merge rasters
    start = proc.time()
    print(paste('Merging ', toString(count), ' rasters for grid ', major_grid, '...'))
    merged_raster = do.call(mosaic, raster_objects)
    end = proc.time() - start
    print(paste('Completed in ', end[3], ' seconds.', sep = ''))
  } else {
    print(paste('Raster ', major_grid, ' already exists.'))
  }
}