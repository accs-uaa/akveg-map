# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge ancillary data tiles
# Author: Timm Nawrocki
# Last Updated: 2024-08-22
# Usage: Execute in Python 3.9+.
# Description: "Merge ancillary data tiles" combines individual tiles into single rasters.
# ---------------------------------------------------------------------------

# Import packages
import os
import glob
import time
import numpy as np
import rasterio
from osgeo import gdal
from osgeo.gdalconst import GA_Update
from osgeo.gdalconst import GDT_Float32
from akutils import end_timing
from akutils import raster_block_progress
from akutils import raster_bounds

# Set nodata value
nodata = -32768

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
ancillary_folder = os.path.join(project_folder, 'Data/Data_Input/ancillary_data')
input_folder = os.path.join(ancillary_folder, 'unprocessed')
output_folder = os.path.join(ancillary_folder, 'processed')

# Define input files
area_input = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')
input_files = glob.glob(f'{input_folder}/AlaskaYukon_ESAWorldCover2*.tif')
print(input_files)

# Define output files
worldcover_output = os.path.join(output_folder, 'AlaskaYukon_ESAWorldCover2_10m_3338.tif')
fireyear_output = os.path.join(output_folder, 'AlaskaYukon_FireYear_10m_3338.tif')

# Merge tiles
print(f'Merging {len(input_files)} tiles...')
iteration_start = time.time()
# Resample and reproject
area_bounds = raster_bounds(area_input)
gdal.Warp(worldcover_output,
          input_files,
          srcSRS='EPSG:3338',
          dstSRS='EPSG:3338',
          outputType=GDT_Float32,
          workingType=GDT_Float32,
          xRes=10,
          yRes=-10,
          srcNodata=nodata,
          dstNodata=nodata,
          outputBounds=area_bounds,
          resampleAlg = 'bilinear',
          targetAlignedPixels=False,
          creationOptions = ['COMPRESS=LZW', 'BIGTIFF=YES'])
end_timing(iteration_start)