# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create elevation composite
# Author: Timm Nawrocki
# Last Updated: 2023-10-21
# Usage: Execute in Python 3.9+.
# Description: "Create elevation composite" combines overlapping elevation input datasets into a single raster output.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
import numpy as np
import rasterio
from osgeo import gdal
from akutils import end_timing
from akutils import raster_bounds
from akutils import raster_block_progress

# Set nodata value
nodata = -32768

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/topography')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
output_folder = os.path.join(data_folder, 'Alaska_Composite_DTM_10m')

# Define input files
alaska_file = os.path.join(data_folder, 'Alaska_IFSAR_DTM_5m/processed', 'Alaska_IFSAR_DTM_5m_3338.tif')
canada_file = os.path.join(data_folder, 'Canada_Composite_DTM_10m/processed', 'Canada_Composite_10m_3338.tif')
#area_file = os.path.join(data_folder, 'area_test.tif')
area_file = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')

# Define output files
merge_vrt = os.path.join(output_folder, 'intermediate', 'Elevation_10m_3338_Merged.vrt')
merge_file = os.path.join(output_folder, 'intermediate', 'Elevation_10m_3338_Merged.tif')
output_file = os.path.join(output_folder, 'float', 'Elevation_10m_3338.tif')

# Merge input rasters
print(f'Merging input rasters...')
iteration_start = time.time()
# List input files with priority to last pixel
input_files = [canada_file, alaska_file]
# Build and translate virtual raster
area_bounds = raster_bounds(area_file)
gdal.BuildVRT(merge_vrt,
              input_files,
              outputSRS='EPSG:3338',
              xRes=10,
              yRes=10,
              srcNodata=nodata,
              VRTNodata=nodata,
              outputBounds=area_bounds)
gdal.Translate(merge_file,
               merge_vrt,
               creationOptions = ['COMPRESS=LZW', 'BIGTIFF=YES'])
end_timing(iteration_start)

# Update mask for output raster
print(f'Masking output raster...')
iteration_start = time.time()
input_raster = rasterio.open(merge_file)
input_profile = input_raster.profile.copy()
area_raster = rasterio.open(area_file)
with rasterio.open(output_file, 'w', **input_profile, BIGTIFF='YES') as dst:
    # Find number of raster blocks
    window_list = []
    for block_index, window in area_raster.block_windows(1):
        window_list.append(window)
    # Iterate processing through raster blocks
    count = 1
    progress = 0
    for block_index, window in area_raster.block_windows(1):
        area_block = area_raster.read(window=window,
                                      masked=False)
        raster_block = input_raster.read(window=window,
                                         masked=False)
        # Set no data values in input raster to 0
        raster_block = np.where(raster_block == nodata, 0, raster_block)
        # Set no data values from area raster to no data
        raster_block = np.where(area_block != 1, nodata, raster_block)
        # Write results
        dst.write(raster_block,
                  window=window)
        # Report progress
        count, progress = raster_block_progress(100, len(window_list), count, progress)
end_timing(iteration_start)
