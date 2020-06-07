# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert Abundance Predictions to Rasters
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2020-06-07
# Usage: Code chunks must be executed sequentially in R Studio or R Studio Server installation. Created using R Studio version 1.2.5042 and R 4.0.0.
# Description: "Convert Distribution-abundance Predictions to Raster" processes the composite distribution-adundance predictions in csv tables into rasters in img format. Raster outputs are in the same coordinate system that grids were exported in but will not be associated with that projection.
# ---------------------------------------------------------------------------

# Set root directory
root_folder = '/home/twnawrocki_rstudio'

# Set map class folder
map_class = 'alnus'

# Define input folder
prediction_folder = paste(root_folder,
                          'predicted_grids',
                          map_class,
                          sep = '/'
                          )
# Define output folder
raster_folder = paste(root_folder,
                      'predicted_rasters',
                      map_class,
                      sep = '/'
                      )

# Install required libraries if they are not already installed.
Required_Packages <- c('sp', 'raster', 'rgdal', 'stringr')
New_Packages <- Required_Packages[!(Required_Packages %in% installed.packages()[,"Package"])]
if (length(New_Packages) > 0) {
  install.packages(New_Packages)
}
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
  input_data = read.csv(prediction)
  output_raster = paste(raster_folder, '/', sub(pattern = "(.*)\\..*$", replacement = "\\1", basename(prediction)), '.img', sep='')
  convertPredictions(input_data, output_raster)
  print(paste('Conversion iteration ', toString(count), ' out of ', toString(prediction_length), ' completed...', sep=''))
  count = count + 1
}