# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Sentinel-2 Composite
# Author: Timm Nawrocki
# Last Updated: 2020-12-12
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Sentinel-2 Composite" merges Sentinel-2 tiles by month and property per predefined grid.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import glob
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import merge_spectral_tiles
import time

# Set root directory
drive = 'K:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/imagery/sentinel-2')
processed_folder = os.path.join(data_folder, 'processed')
gridded_folder = os.path.join(data_folder, 'gridded')

# Define input datasets
grid_major = os.path.join(drive, root_folder, 'Data/analyses/gridMajor')
study_area = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input/northAmericanBeringia_ModelArea.tif')

# Define working geodatabase
geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/BeringiaVegetation.gdb')
# Set environment workspace
arcpy.env.workspace = geodatabase

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define month and property values
months = ['06',
          '07'
          ]
properties = ['2_blue',
              '3_green',
              '4_red',
              '5_redEdge1',
              '6_redEdge2',
              '7_redEdge3',
              '8_nearInfrared',
              '8a_redEdge4',
              '11_shortInfrared1',
              '12_shortInfrared2',
              'evi2',
              'nbr',
              'ndmi',
              'ndsi',
              'ndvi',
              'ndwi'
              ]

# Create a list of all month-property combinations
metrics_list = []
for month in months:
    for property in properties:
        month_property = month + '_' + property
        metrics_list.append(month_property)
metrics_length = len(metrics_list)

# List grid rasters
print('Searching for grid rasters...')
# Start timing function
iteration_start = time.time()
# Create a list of included grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E4', 'E5', 'E6']
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

# Iterate through each buffered grid and create spectral composite
for metric in metrics_list:
    # Create list of all metric tiles
    file_search = 'Sent2_' + metric + '*.tif'
    metric_tiles = glob.glob(os.path.join(processed_folder, file_search))

    # Set initial grid count
    grid_count = 1

    # For each grid, process the spectral metric
    for grid in grids:
        # Define folder structure
        grid_title = os.path.splitext(os.path.split(grid)[1])[0]
        grid_folder = os.path.join(gridded_folder, grid_title)

        # Make grid folder if it does not already exist
        if os.path.exists(grid_folder) == 0:
            os.mkdir(grid_folder)

        # Define processed grid raster
        spectral_grid = os.path.join(grid_folder, 'Sent2_' + metric + '_AKALB_' + grid_title + '.tif')

        # If spectral grid does not exist then create spectral grid
        if arcpy.Exists(spectral_grid) == 0:
            print(f'Processing {metric} grid {grid_count} of {grids_length}...')

            # Define input and output arrays
            merge_inputs = [grid, study_area] + metric_tiles
            merge_outputs = [spectral_grid]

            # Create key word arguments
            merge_kwargs = {'cell_size': 10,
                            'output_projection': 3338,
                            'input_array': merge_inputs,
                            'output_array': merge_outputs
                            }

            # Process the reproject integer function
            arcpy_geoprocessing(merge_spectral_tiles, **merge_kwargs)
            print('----------')

        else:
            print(f'Spectral grid {grid_count} of {grids_length} for {metric} already exists.')
            print('----------')

        # Increase counter
        grid_count += 1
