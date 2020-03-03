# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Format MODIS Land Surface Temperature
# Author: Timm Nawrocki
# Last Updated: 2020-03-02
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Format MODIS Land Surface Temperature" reprojects the LST data and converts to integers per predefined grid.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import format_lst
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/imagery/modis')
unprocessed_folder = os.path.join(data_folder, 'unprocessed')
gridded_folder = os.path.join(data_folder, 'gridded')

# Define input datasets
grid_major = os.path.join(drive, root_folder, 'Data/analyses/gridMajor')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define working geodatabase
geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')
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

# Create a list of all month-property combinations
metrics_list = []
for month in months:
    month_property = month + '_' + property
    metrics_list.append(month_property)
metrics_length = len(metrics_list)

# List grid rasters
print('Searching for grid rasters...')
# Start timing function
iteration_start = time.time()
# Create a list of included grids
grid_list = ['A5', 'A6', 'A7', 'A8', 'A9',
             'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10',
             'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
             'D4', 'D5', 'D6',
             'E5']
# Append file names to rasters in list
grids = []
for grid in grid_list:
    raster_path = os.path.join(grid_major, 'Grid_' + grid + '.tif')
    grids.append(raster_path)
grids_length = len(grids)
print(f'Spectral composites will be created for {grids_length} grids and {metrics_length} metrics...')
# End timing
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
# Report success
print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Iterate through each buffered grid and create LST composite
for metric in metrics_list:
    # Define LST Raster
    lst_raster = os.path.join(unprocessed_folder, 'MODIS_' + metric + '.tif')

    # Set initial grid count
    grid_count = 1

    # For each grid, process the spectral metric
    for grid in grids:
        # Define folder structure
        grid_title = os.path.splitext(os.path.split(grid)[1])[0]
        grid_folder = os.path.join(gridded_folder, grid_title)

        # Define processed grid raster
        lst_grid = os.path.join(grid_folder, 'MODIS_' + metric + '_AKALB_' + grid_title + '.tif')

        # If LST grid does not exist then create LST grid
        if arcpy.Exists(lst_grid) == 0:
            print(f'Processing {metric} grid {grid_count} of {grids_length}...')

            # Define input and output arrays
            lst_inputs = [grid, lst_raster]
            lst_outputs = [lst_grid]

            # Create key word arguments
            lst_kwargs = {'cell_size': 10,
                          'input_projection': 4326,
                          'output_projection': 3338,
                          'geographic_transform': 'WGS_1984_(ITRF00)_To_NAD_1983',
                          'input_array': lst_inputs,
                          'output_array': lst_outputs
                          }

            # Process the reproject integer function
            arcpy_geoprocessing(format_lst, **lst_kwargs)
            print('----------')

        else:
            print(f'LST grid {grid_count} of {grids_length} for {metric} already exists.')
            print('----------')

        # Increase counter
        grid_count += 1