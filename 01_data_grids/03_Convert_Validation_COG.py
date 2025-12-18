# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create cloud-optimized geotiff for validation raster
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Create cloud-optimized geotiff for validation raster" creates a cloud-optimized geotiff version of the validation grid raster for use as COG-backed assets in Google Earth Engine.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
from osgeo import gdal
from akutils import *

# Configure GDAL
gdal.UseExceptions()

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'D:'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive,
                              root_folder,
                              'Projects/VegetationEcology/AKVEG_Map/Data/Data_Input')
input_folder = os.path.join(project_folder, 'validation_grid')
output_folder = os.path.join(project_folder, 'cog_data')

# Define input file
validation_input = os.path.join(input_folder, 'AlaskaYukon_100_Tiles_3338.tif')

# Define output file
validation_output = os.path.join(output_folder, 'AlaskaYukon_100_Tiles_3338.tif')

#### PROCESS CLOUD-OPTIMIZED GEOTIFFS
####____________________________________________________

# Convert raster to cloud-optimized geotiff
print(f'Creating cloud-optimized raster...')
iteration_start = time.time()
# Execute GDAL translate
gdal.Translate(validation_output,
               validation_input,
               format='COG',
               creationOptions=['BLOCKSIZE=256',
                                'COMPRESS=DEFLATE',
                                'LEVEL=9',
                                'PREDICTOR=STANDARD',
                                'BIGTIFF=YES'])
end_timing(iteration_start)
