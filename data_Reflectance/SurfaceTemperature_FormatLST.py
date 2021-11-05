# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Format MODIS land surface temperature summer warmth index
# Author: Timm Nawrocki
# Last Updated: 2021-11-04
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Format MODIS land surface temperature summer warmth index" sums LST values from May-September, reprojects the LST data, and extracts to predefined grids.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_lst_warmth_index
from package_GeospatialProcessing import format_climate_grids

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/imagery/modis')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data')
grid_folder = os.path.join(drive, root_folder, 'Data/analyses/grid_major/nab')
unprocessed_folder = os.path.join(data_folder, 'unprocessed/nab')
processed_folder = os.path.join(data_folder, 'processed/nab')
output_folder = os.path.join(data_folder, 'gridded/nab')

# Define input datasets
study_area = os.path.join(project_folder, 'Data_Input/NorthAmericanBeringia_ModelArea.tif')

# Define output datasets
lst_warmthindex = os.path.join(processed_folder, 'MODIS_LSTWarmthIndex_2010s.tif')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'BeringiaVegetation.gdb')

# Define grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E4', 'E5', 'E6']

# Define month and property values
months = ['05May',
          '06June',
          '07July',
          '08August',
          '09September'
          ]
climate_property = 'meanLST'

# Create a list of all climate raster data
raster_list = []
for month in months:
    raster = os.path.join(unprocessed_folder, 'MODIS_' + month + '_' + climate_property + '.tif')
    raster_list.append(raster)

#### CALCULATE CLIMATE MEAN

# Create LST format key word arguments
kwargs_lst = {'cell_size': 500,
              'input_projection': 4326,
              'output_projection': 3338,
              'geographic_transform': 'WGS_1984_(ITRF00)_To_NAD_1983',
              'input_array': [study_area] + raster_list,
              'output_array': [lst_warmthindex]
              }

# Format LST data
if arcpy.Exists(lst_warmthindex) == 0:
    print(f'Calculate MODIS Land Surface Temperature Summer Warmth Index...')
    arcpy_geoprocessing(calculate_lst_warmth_index, **kwargs_lst)
    print('----------')
else:
    print('MODIS Land Surface Temperature Summer Warmth Index already exists.')
    print('----------')

#### PARSE DATA TO GRIDS

# Set initial grid count
grid_count = 1

# Set initial count
count = 1

# For each grid, process the climate metric
for grid in grid_list:
    # Define folder structure
    output_path = os.path.join(output_folder, grid)
    output_raster = os.path.join(output_path, 'MODIS_LST_WarmthIndex_AKALB_' + grid + '.tif')

    # Make grid folder if it does not already exist
    if os.path.exists(output_path) == 0:
        os.mkdir(output_path)

    # Define the grid raster
    grid_raster = os.path.join(grid_folder, grid + '.tif')

    # If output raster does not exist then create output raster
    if arcpy.Exists(output_raster) == 0:
        # Create key word arguments
        kwargs_grid = {'input_array': [study_area, grid_raster, lst_warmthindex],
                       'output_array': [output_raster]
                       }

        # Extract climate data to grid
        print(f'Processing grid {count} of {len(grid_list)}...')
        arcpy_geoprocessing(format_climate_grids, **kwargs_grid)
        print('----------')
    else:
        print(f'Grid {count} of {len(grid_list)} already exists.')
        print('----------')

    # Increase counter
    count += 1
