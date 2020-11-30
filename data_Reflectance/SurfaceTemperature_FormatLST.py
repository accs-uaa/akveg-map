# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Format MODIS Land Surface Temperature Summer Warmth Index
# Author: Timm Nawrocki
# Last Updated: 2020-11-30
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Format MODIS Land Surface Temperature Summer Warmth Index" sums LST values from May-September, reprojects the LST data, and extracts to predefined grids.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_lst_warmth_index
from package_GeospatialProcessing import format_climate_grids
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/imagery/modis')
unprocessed_folder = os.path.join(data_folder, 'unprocessed')
processed_folder = os.path.join(data_folder, 'processed')
gridded_folder = os.path.join(data_folder, 'gridded')

# Define input datasets
grid_major = os.path.join(drive, root_folder, 'Data/analyses/gridMajor')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input/northAmericanBeringia_ModelArea.tif')

# Define output datasets
lst_warmthindex = os.path.join(processed_folder, 'MODIS_LSTWarmthIndex_2010s.tif')

# Define working geodatabase
geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/BeringiaVegetation.gdb')
# Set environment workspace
arcpy.env.workspace = geodatabase

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define month and property values
months = ['05May',
          '06June',
          '07July',
          '08August',
          '09September'
          ]
property = 'meanLST'

# Create a list of all month lst rasters
rasters_list = []
for month in months:
    month_property = os.path.join(unprocessed_folder, 'MODIS_' + month + '_' + property + '.tif')
    rasters_list.append(month_property)
rasters_length = len(rasters_list)

# Create LST format input and output arrays
lst_inputs = [snap_raster] + rasters_list
lst_outputs = [lst_warmthindex]

# Create LST format key word arguments
lst_kwargs = {'cell_size': 500,
              'input_projection': 4326,
              'output_projection': 3338,
              'geographic_transform': 'WGS_1984_(ITRF00)_To_NAD_1983',
              'input_array': lst_inputs,
              'output_array': lst_outputs
              }

# Format LST data
if arcpy.Exists(lst_warmthindex) == 0:
    print(f'Calculate MODIS Land Surface Temperature Summer Warmth Index...')
    arcpy_geoprocessing(calculate_lst_warmth_index, **lst_kwargs)
    print('----------')
else:
    print('MODIS Land Surface Temperature Summer Warmth Index already exists...')
    print('----------')

# List grid rasters
print('Searching for grid rasters...')
# Start timing function
iteration_start = time.time()
# Create a list of included grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E5', 'E6']
# Append file names to rasters in list
grids = []
for grid in grid_list:
    raster_path = os.path.join(grid_major, 'Grid_' + grid + '.tif')
    grids.append(raster_path)
grids_length = len(grids)
print(f'LST Index will be created for {grids_length} grids...')
# End timing
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
# Report success
print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Set initial grid count
grid_count = 1

# For each grid, process the climate metric
for grid in grids:
    # Define folder structure
    grid_title = os.path.splitext(os.path.split(grid)[1])[0]
    grid_folder = os.path.join(gridded_folder, grid_title)

    # Make grid folder if it does not already exist
    if os.path.exists(grid_folder) == 0:
        os.mkdir(grid_folder)

    # Define processed grid raster
    climate_grid = os.path.join(grid_folder, 'MODIS_LST_WarmthIndex' + '_AKALB_' + grid_title + '.tif')

    # If climate grid does not exist then create climate grid
    if arcpy.Exists(climate_grid) == 0:
        print(f'Processing {grid_count} of {grids_length}...')

        # Define input and output arrays
        climate_grid_inputs = [grid, lst_warmthindex]
        climate_grid_outputs = [climate_grid]

        # Create key word arguments
        climate_grid_kwargs = {'input_array': climate_grid_inputs,
                               'output_array': climate_grid_outputs
                               }

        # Process the reproject integer function
        arcpy_geoprocessing(format_climate_grids, **climate_grid_kwargs)
        print('----------')

    else:
        print(f'Climate grid {grid_count} of {grids_length} already exists.')
        print('----------')

    # Increase counter
    grid_count += 1