# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert Abundance Predictions to Rasters
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2021-03-21
# Usage: Code chunks must be executed sequentially in R Studio or R Studio Server installation. Created using R Studio version 1.2.5042 and R 4.0.0.
# Description: "Convert Distribution-abundance Predictions to Raster" processes the composite distribution-adundance predictions in csv tables into rasters in img format. Raster outputs are in the same coordinate system that grids were exported in but will not be associated with that projection.
# ---------------------------------------------------------------------------

# Set root directory
root_folder = '/home/twn_rstudio'

# Set map class folder
map_class = 'alnus'

# Define input folder
prediction_folder = paste(root_folder,
                          'predicted_tables',
                          map_class,
                          sep = '/'
                          )
# Define output folder
raster_folder = paste(root_folder,
                      'predicted_rasters',
                      map_class,
                      sep = '/'
                      )

# Import required libraries for geospatial processing: sp, raster, rgdal, and stringr.
library(sp)
library(raster)
library(rgdal)
library(stringr)

# Generate a list of all predictions in the predictions directory
prediction_list = list.files(prediction_folder, pattern='csv$', full.names=TRUE)
prediction_length = length(prediction_list)

# Define a function to convert the prediction csv to a raster and export an img raster file
convertPredictions = function(input_data, output_raster) {
  prediction_data = input_data[,c('x', 'y', 'prediction')]
  prediction_raster = rasterFromXYZ(prediction_data, res=c(10,10), crs='+init=EPSG:3338', digits=5)
  writeRaster(prediction_raster, output_raster, format='HFA', overwrite=TRUE)
}

# Create img raster file for each prediction table in the predictions directory
count = 1
for (prediction in prediction_list) {
  # Define input and output data
  input_data = read.csv(prediction)
  output_raster = paste(raster_folder, '/', sub(pattern = "(.*)\\..*$", replacement = "\\1", basename(prediction)), '.img', sep='')
  
  # Create output raster if it does not already exist
  if (!file.exists(output_raster)) {
    # Convert table to raster
    convertPredictions(input_data, output_raster)
    print(paste('Conversion iteration ', toString(count), ' out of ', toString(prediction_length), ' completed...', sep=''))
    print('----------')
  } else {
    print(paste('Raster ', toString(count), ' out of ', toString(prediction_length), ' already exists.', sep = ''))
    print('----------')
  }
  count = count + 1
}