# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate mean summer warmth index for 2006-2015
# Author: Timm Nawrocki
# Last Updated: 2026-01-18
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Calculate mean summer warmth index for 2006-2015" calculates the mean annual summer warmth index from May-September for years 2000-2015. The primary data are the SNAP Alaska-Yukon 2km data with the included portion of the Northwest Territories interpolated by geographic nearest neighbors.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import reproject, Resampling
from rasterio.fill import fillnodata
from akutils import *

# Set nodata value
nodata_value = -32768

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
data_folder = os.path.join(drive, root_folder, 'Data/climatology')
climate_folder = os.path.join(data_folder, 'unprocessed/tasmean_2km_TS408')
processed_folder = os.path.join(data_folder, 'processed')

# Define input datasets
area_input = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')

# Define intermediate datasets
summer_intermediate = os.path.join(processed_folder,
                                    'SummerWarmth_2006_2015_2km_3338.tif')
summer_filled = os.path.join(processed_folder,
                              'SummerWarmth_2006_2015_2km_3338_Filled.tif')

# Define output datasets
summer_output = os.path.join(processed_folder,
                              'SummerWarmth_2006_2015_10m_3338.tif')

# Define month and property values
climate_property = 'tas_mean_C_cru_ts408_historical'
months = ['05', '06', '07', '08', '09']
years = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']

# Create a list of all climate raster data
raster_list = []
for year in years:
    for month in months:
        raster_input = os.path.join(climate_folder,
                                    climate_property + '_' + month + '_' + year + '.tif')
        raster_list.append(raster_input)

#### CALCULATE CELL MEANS FOR NATIVE RESOLUTION
####____________________________________________________

# Read input rasters
area_raster = rasterio.open(raster_list[0])

# Prepare output profile
output_profile = area_raster.profile.copy()
output_profile.update({
    'height': area_raster.height,
    'width': area_raster.width,
    'transform': area_raster.transform,
    'crs': area_raster.crs,
    'nodata': nodata_value,
    'dtype': 'int16',
    'compress': 'lzw',
    'bigtiff': 'YES'
})

# Calculate cell mean
print(f'Calculating cell means...')
iteration_start = time.time()
with rasterio.open(summer_intermediate, 'w', **output_profile) as dst:
    # Find number of raster blocks
    window_list = []
    for block_index, window in dst.block_windows(1):
        window_list.append(window)

    # Iterate processing through raster blocks
    count = 1
    progress = 0
    for block_index, window in dst.block_windows(1):
        # Define out block
        out_block = None

        # Add rasters
        for climate_input in raster_list:
            # Open raster
            climate_raster = rasterio.open(climate_input)
            climate_block = climate_raster.read(1, window=window)

            # Update no data values for climate block
            climate_block = np.where(climate_block == climate_raster.nodata,
                                     nodata_value, (climate_block * 100))

            # Read raster block
            if out_block is None:
                out_block = climate_block
            else:
                out_block = out_block + climate_block

        # Divide by number of input rasters
        out_block = np.round((out_block/len(years)))

        # Update no data
        out_block = np.where(out_block < -10000, nodata_value, out_block)

        # Write results
        dst.write(out_block,
                  window=window,
                  indexes=1)
        # Report progress
        count, progress = raster_block_progress(100, len(window_list), count, progress)
end_timing(iteration_start)

#### FILL NODATA
####____________________________________________________

# Read intermediate climate data
print(f'Filling no data...')
iteration_start = time.time()
climate_raster = rasterio.open(summer_intermediate)
climate_data = climate_raster.read(1)

# Create a mask where valid data exists
climate_mask = climate_raster.read_masks(1)

with rasterio.open(summer_filled, 'w', **output_profile) as dst:
    # Fill no data
    climate_filled = fillnodata(climate_data,
                                mask=climate_mask,
                                max_search_distance=100.0,
                                smoothing_iterations=0)

    # Write the result
    dst.write(climate_filled, 1)
end_timing(iteration_start)

#### RESAMPLE TO OUTPUT RESOLUTION
####____________________________________________________

# Read input rasters
print(f'Resampling to output resolution...')
iteration_start = time.time()
area_raster = rasterio.open(area_input)
climate_raster = rasterio.open(summer_filled)

# Prepare output profile
output_profile = climate_raster.profile.copy()
output_profile.update({
    'height': area_raster.height,
    'width': area_raster.width,
    'transform': area_raster.transform,
    'crs': area_raster.crs,
    'nodata': nodata_value,
    'dtype': 'int16',
    'compress': 'lzw',
    'bigtiff': 'YES',
    'tiled': True,
    'blockxsize': 512,
    'blockysize': 512
})

# Reproject and extract raster to area
print(f'Source CRS: {climate_raster.crs}')
print(f'Target CRS: {area_raster.crs}')
with rasterio.open(summer_output, 'w', **output_profile) as dst:
    # Find number of raster blocks
    window_list = [window for ij, window in dst.block_windows(1)]

    # Iterate processing through raster blocks
    count = 1
    progress = 0
    for block_index, window in dst.block_windows(1):
        # Read area block
        area_block = area_raster.read(1, window=window)

        # Create array to store the input raster
        out_block = np.zeros(area_block.shape, dtype=output_profile['dtype'])

        # Calculate the transform for the area raster window
        dst_window_transform = rasterio.windows.transform(window, area_raster.transform)

        # Reproject input raster using warp
        reproject(
            source=rasterio.band(climate_raster, 1),
            destination=out_block,
            src_transform=climate_raster.transform,
            src_crs=climate_raster.crs,
            dst_transform=dst_window_transform,
            dst_crs=area_raster.crs,
            resampling=Resampling.bilinear,
            src_nodata=climate_raster.nodata,
            dst_nodata=nodata_value
        )

        # Set valid data for the area raster
        out_block = np.where((out_block == nodata_value) & (area_block == 1),
                             0, out_block)

        # Set no data values from area raster to no data
        out_block = np.where(area_block == 1, out_block, nodata_value)

        # Write results
        dst.write(out_block,
                  window=window,
                  indexes=1)
        # Report progress
        count, progress = raster_block_progress(100, len(window_list), count, progress)
end_timing(iteration_start)

# Delete intermediate datasets
os.remove(summer_intermediate)
os.remove(summer_filled)
