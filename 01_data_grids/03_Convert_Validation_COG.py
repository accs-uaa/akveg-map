# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create cloud-optimized geotiffs for validation raster
# Author: Timm Nawrocki
# Last Updated: 2024-07-29
# Usage: Must be executed in a Python 3.11+ installation with GDAL 3.9+.
# Description: "Create cloud-optimized geotiffs for validation raster" creates a cloud-optimized geotiff version of the validation grid raster for use as COG-backed assets in Google Earth Engine.
# ---------------------------------------------------------------------------

# Import packages
import glob
import os
import time
from osgeo import gdal

# Configure GDAL
gdal.UseExceptions()

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
input_files = [validation_input]

# Convert each raster to cloud-optimized geotiff
count = 1
for input_file in input_files[:]:
    # Define output file
    output_file = os.path.join(output_folder, os.path.split(input_file)[1])

    # Create cloud-optimized geotiff if it does not already exist
    if os.path.exists(output_file) == 0:
        print(f'Creating cloud-optimized raster {count} of {len(input_files)}...')
        fmt_start = time.gmtime()
        print(f'\t{time.strftime("%D %T", fmt_start)}')
        # Execute GDAL translate
        gdal.Translate(output_file,
                       input_file,
                       format='COG',
                       creationOptions=['BLOCKSIZE=256',
                                        'COMPRESS=DEFLATE',
                                        'LEVEL=9',
                                        'PREDICTOR=STANDARD',
                                        'BIGTIFF=YES'])
        print(f'\tFinished creating cloud-optimized raster {count} of {len(input_files)}.')
        fmt_end = time.gmtime()
        print(f'\t{time.strftime("%D %T", fmt_end)}')
        print('----------')
    else:
        print(f'Cloud-optimized raster {count} of {len(input_files)} already exists.')
        print('----------')
    count += 1
