# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse Sentinel-2 median to modeling grids
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Parse Sentinel-2 median to modeling grids" parses the Sentinel-2 growing season median variables to modeling grids for use in prediction.
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

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = '/home'
root_folder = 'twnawrocki'

# Define folder structure
grid_folder = os.path.join(drive, root_folder, 'data_input/grid_050')
covariate_folder = os.path.join(drive, root_folder, 'data_input/s2_median_v20240724')
intermediate_folder = os.path.join(drive, root_folder, 'data_input/s2_intermediate')
output_folder = os.path.join(drive, root_folder, 'data_input/s2_050')

# Create list of grids and covariates
grid_list = glob.glob(f'{grid_folder}/*.tif')
s2_list = glob.glob(f'{covariate_folder}/*.tif')

# Define output files
s2_vrt = os.path.join(intermediate_folder, 's2_median.vrt')

#### PARSE DATA TO GRIDS
####____________________________________________________

# Build virtual raster
if os.path.exists(s2_vrt) == 0:
    print('Building vrt...')
    iteration_start = time.time()
    gdal.BuildVRT(s2_vrt,
                  s2_list,
                  outputSRS='EPSG:3338',
                  xRes=10,
                  yRes=10,
                  srcNodata=nodata,
                  VRTNodata=nodata)
    end_timing(iteration_start)
else:
    print(f'VRT already exists.')
    print('----------')

# Parse each covariate to grids
count = 1
for grid in grid_list:
    # Define file names
    grid_name = os.path.split(grid)[1].replace('_10m_3338.tif', '')
    raster_output = os.path.join(output_folder, f's2_median_{grid_name}.tif')

    # Parse grid if raster does not already exist
    if os.path.exists(raster_output) == 0:
        print(f'Parsing covariate grid {count} of {len(grid_list)}...')
        iteration_start = time.time()

        # Extract raster to grid
        area_bounds = raster_bounds(grid)
        gdal.Warp(raster_output,
                  s2_vrt,
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
    # If grid raster already exists, continue to next grid
    else:
        print(f'Covariate grid {count} of {len(grid_list)} already exists.')
        print('----------')

    # Increase count
    count += 1
