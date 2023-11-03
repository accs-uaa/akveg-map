# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create elevation composite for Canada
# Author: Timm Nawrocki
# Last Updated: 2023-10-21
# Usage: Execute in Python 3.9+.
# Description: "Create elevation composite for Canada" combines overlapping elevation input datasets for Canada into a single raster output by selecting either the mean of the datasets or the value of the Arctic DEM if it is lower than the mean.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
import numpy as np
import rasterio
from akutils import *

# Set nodata value
nodata = -32768

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/topography')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
output_folder = os.path.join(data_folder, 'Canada_Composite_DTM_10m', 'esa_glo')

# Define input files
#usgs_30m_file = os.path.join(data_folder, 'USGS_3DEP_30m/test_processed', 'USGS_3DEP_30m_3338.tif')
#usgs_60m_file = os.path.join(data_folder, 'USGS_3DEP_60m/test_processed', 'USGS_3DEP_60m_3338.tif')
#arctic_10m_file = os.path.join(data_folder, 'Arctic_DEM_10m/test_processed', 'Arctic_DEM_10m_3338.tif')
esa_glo_file = os.path.join(data_folder, 'ESA_GLO_30m/test_processed', 'ESA_GLO_30m_3338.tif')
area_file = os.path.join(data_folder, 'area_test.tif')
#area_file = os.path.join(data_folder, 'Canada_DEM_MapDomain_10m_3338.tif')

# Define output files
output_file = os.path.join(output_folder, 'Canada_Composite_10m_3338.tif')

# Calculate new raster
print(f'Calculating output raster...')
iteration_start = time.time()
#arctic_raster = rasterio.open(arctic_dem_file)
#usgs_30m_raster = rasterio.open(usgs_30m_file)
#usgs_60m_raster = rasterio.open(usgs_60m_file)
esa_glo_raster = rasterio.open(esa_glo_file)
input_profile = esa_glo_raster.profile.copy()
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
        #arctic_block = arctic_raster.read(window=window, masked=False)
        #usgs_30m_block = usgs_30m_raster.read(window=window, masked=False)
        #usgs_60m_block = usgs_60m_raster.read(window=window, masked=False)
        esa_glo_block = esa_glo_raster.read(window=window, masked=False)
        area_block = area_raster.read(window=window, masked=False)
        # Set values where usgs 30 m block is nodata
        raster_block = np.where((usgs_30m_block == nodata) & (usgs_60m_block != nodata) & (arctic_block != nodata),
                                (arctic_block + (usgs_60m_block * 3)) / 4, arctic_block)
        # Set values where usgs 60 m block is nodata
        raster_block = np.where((usgs_30m_block != nodata) & (arctic_block != nodata),
                                (arctic_block + (usgs_30m_block * 3)) / 4, raster_block)
        # Set minimum values to match Arctic DEM
        raster_block = np.where(np.less(arctic_block, raster_block), arctic_block, raster_block)
        # Set values where Arctic DEM is nodata
        raster_block = np.where((arctic_block == nodata) & (usgs_30m_block != nodata), usgs_30m_block, raster_block)
        raster_block = np.where((arctic_block == nodata) & (usgs_30m_block == nodata), usgs_60m_block, raster_block)
        # Set no data values from area raster to no data
        raster_block = np.where(area_block != 1, nodata, raster_block)
        # Write results
        dst.write(raster_block,
                  window=window)
        # Report progress
        count, progress = raster_block_progress(100, len(window_list), count, progress)
end_timing(iteration_start)
