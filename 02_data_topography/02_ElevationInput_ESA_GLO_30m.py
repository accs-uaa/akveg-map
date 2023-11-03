# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Process ESA GLO 30 m DEM
# Author: Timm Nawrocki
# Last Updated: 2023-10-10
# Usage: Execute in Python 3.9+.
# Description: "Process ESA GLO 30 m DEM" combines individual DEM tiles to a single raster, resamples to 10 m, and replaces erroneous values.
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
data_folder = os.path.join(drive, root_folder, 'Data/topography')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
input_folder = os.path.join(data_folder, 'ESA_GLO_30m', 'unprocessed')
output_folder = os.path.join(data_folder, 'ESA_GLO_30m', 'processed')
corrected_folder = os.path.join(input_folder, 'corrected')
# Make tiles folder if it does not already exist
if os.path.exists(corrected_folder) == 0:
    os.mkdir(corrected_folder)

# Define input files
os.chdir(input_folder)
input_files = glob.glob('*dem.tif')
#area_file = os.path.join(data_folder, 'area_test.tif')
area_file = os.path.join(data_folder, 'Canada_DEM_MapDomain_10m_3338.tif')

# Define output files
output_file = os.path.join(output_folder, 'ESA_GLO_30m_3338.tif')

# Define empty tile list
tile_list = []

# Correct erroneous and nodata values
tile_count = 1
# Iterate through all tiles
for input_file in input_files:
    print(f'Processing tile {tile_count} of {len(input_files)}...')
    iteration_start = time.time()
    input_raster = gdal.Open(input_file, GA_Update)
    # Update nodata value for each band in raster
    for i in range(1, input_raster.RasterCount + 1):
        input_raster.GetRasterBand(i).SetNoDataValue(nodata)
    # Save the results
    input_raster = None
    # Define corrected file
    corrected_file = os.path.join(corrected_folder, os.path.split(input_file)[1])
    tile_list.append(corrected_file)
    # Prepare raster file
    if os.path.exists(corrected_file) == 0:
        input_raster = rasterio.open(input_file)
        input_profile = input_raster.profile.copy()
        with rasterio.open(corrected_file, 'w', **input_profile) as dst:
            # Find number of raster blocks
            window_list = []
            for block_index, window in input_raster.block_windows(1):
                window_list.append(window)
            # Iterate processing through raster blocks
            count = 1
            progress = 0
            for block_index, window in input_raster.block_windows(1):
                raster_block = input_raster.read(window=window,
                                                 masked=True)
                # Replace erroneous values
                raster_block = np.where((raster_block < -20) | (raster_block > 6195), nodata, raster_block)
                # Write results
                dst.write(raster_block,
                          window=window)
                # Report progress
                count, progress = raster_block_progress(4, len(window_list), count, progress)
    tile_count += 1
    end_timing(iteration_start)

# Merge tiles
print(f'Merging {len(input_files)} tiles...')
iteration_start = time.time()
# Resample and reproject
area_bounds = raster_bounds(area_file)
gdal.Warp(output_file,
          tile_list,
          srcSRS='EPSG:4326',
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