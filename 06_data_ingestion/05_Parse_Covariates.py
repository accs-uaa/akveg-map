# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse covariates to modeling grids
# Author: Timm Nawrocki
# Last Updated: 2024-09-18
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Parse covariates to modeling grids" parses the topographic, hydrographic, and climate variables to modeling grids for use in prediction.
# ---------------------------------------------------------------------------

# Import packages
import glob
import os
import time
from osgeo import gdal
from osgeo.gdalconst import GDT_Int16
from akutils import *

# Set nodata value
nodata = -32768

# Configure GDAL
gdal.UseExceptions()

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
grid_folder = os.path.join(drive, root_folder, 'Data_Input/grid_050')
covariate_folder = os.path.join(drive, root_folder, 'Data_Input/covariates_v20240711')
output_folder = os.path.join(drive, root_folder, 'Data_Input/covariates_050')

# Create list of grids and covariates
grid_list = glob.glob(f'{grid_folder}/*.tif')
covariate_list = glob.glob(f'{covariate_folder}/*.tif')

# Parse each covariate to grids
count = 1
grid_list = [os.path.join(grid_folder, 'AK050H057V019' + '_10m_3338.tif')]
for covariate in covariate_list:
    for grid in grid_list:
        # Define file names
        grid_name = os.path.split(grid)[1].replace('_10m_3338.tif', '')
        covariate_name = os.path.split(covariate)[1].replace('_10m_3338.tif', '')
        raster_output = os.path.join(output_folder, f'{covariate_name}_{grid_name}.tif')

        # Parse grid if raster does not already exist
        if os.path.exists(raster_output) == 0:
            print(f'Parsing covariate grid {count} of {len(grid_list) * len(covariate_list)}...')
            iteration_start = time.time()

            # Extract raster to grid
            area_bounds = raster_bounds(grid)
            gdal.Warp(raster_output,
                      covariate,
                      srcSRS='EPSG:3338',
                      dstSRS='EPSG:3338',
                      outputType=GDT_Int16,
                      workingType=GDT_Int16,
                      xRes=10,
                      yRes=-10,
                      srcNodata=nodata,
                      dstNodata=nodata,
                      outputBounds=area_bounds,
                      resampleAlg='bilinear',
                      targetAlignedPixels=False,
                      creationOptions=['TILED=YES',
                                       'BLOCKXSIZE=256',
                                       'BLOCKYSIZE=256',
                                       'COMPRESS=LZW',
                                       'BIGTIFF=YES'])
            end_timing(iteration_start)
        else:
            # If grid raster already exists, continue to next grid
            print(f'Covariate grid {count} of {len(grid_list) * len(covariate_list)} already exists.')
            print('----------')

        # Increase count
        count += 1
