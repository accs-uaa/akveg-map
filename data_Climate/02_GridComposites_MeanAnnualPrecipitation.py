# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create mean annual total precipitation composite for 2000-2015
# Author: Timm Nawrocki
# Last Updated: 2021-11-20
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create mean annual total precipitation composite for 2000-2015" calculates the mean annual precipitation from all months for years 2000-2015. The primary data are the SNAP Alaska-Yukon 2km data with the included portion of the Northwest Territories interpolated by geographic nearest neighbors.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_climate_mean
from package_GeospatialProcessing import format_climate_grids
from package_GeospatialProcessing import interpolate_raster

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/climatology/precipitation')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
grid_folder = os.path.join(drive, root_folder, 'Data/analyses/grid_major/nab')
unprocessed_folder = os.path.join(data_folder, 'unprocessed/2km')
processed_folder = os.path.join(data_folder, 'processed')
output_folder = os.path.join(data_folder, 'gridded/nab')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')

# Define input datasets
nab_raster = os.path.join(project_folder, 'Data_Input/NorthAmericanBeringia_ModelArea.tif')

# Define output datasets
mean_raw = os.path.join(processed_folder, 'full/Precipitation_MeanAnnual_Raw_2km_2000-2015.tif')
mean_interpolated = os.path.join(processed_folder, 'nab/Precipitation_MeanAnnual_Interpolated_2km_2000-2015.tif')

# Define grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E4', 'E5', 'E6']

# Define month and property values
climate_property = 'pr_total_mm_CRU_TS40_historical'
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
years = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007',
         '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']
denominator = len(years)

# Create a list of all climate raster data
raster_list = []
for year in years:
    for month in months:
        raster = os.path.join(unprocessed_folder, climate_property + '_' + month + '_' + year + '.tif')
        raster_list.append(raster)

#### CALCULATE CLIMATE MEAN

# Create key word arguments for the climate mean
kwargs_mean = {'denominator': denominator,
               'input_array': raster_list,
               'output_array': [mean_raw]
               }

# Create a composite raster of the climate mean
if arcpy.Exists(mean_raw) == 0:
    print('Calculating mean annual precipitation...')
    arcpy_geoprocessing(calculate_climate_mean, **kwargs_mean)
    print('----------')
else:
    print('Mean annual precipitation already exists.')
    print('----------')

#### FILL MISSING DATA

# Create key word arguments to interpolate raster
kwargs_interpolate = {'input_array': [nab_raster, mean_raw],
                      'output_array': [mean_interpolated]
                      }

# Interpolate climate raster
if arcpy.Exists(mean_interpolated) == 0:
    print('Filling missing data...')
    arcpy_geoprocessing(interpolate_raster, **kwargs_interpolate)
    print('----------')
else:
    print('Filled data already exists.')
    print('----------')

#### PARSE DATA TO GRIDS

# Set initial count
count = 1

# For each grid, process the climate metric
for grid in grid_list:
    # Define folder structure
    output_path = os.path.join(output_folder, grid)
    output_raster = os.path.join(output_path, 'Precipitation_MeanAnnual_AKALB_' + grid + '.tif')

    # Make grid folder if it does not already exist
    if os.path.exists(output_path) == 0:
        os.mkdir(output_path)

    # Define the grid raster
    grid_raster = os.path.join(grid_folder, grid + '.tif')

    # If output raster does not exist then create output raster
    if arcpy.Exists(output_raster) == 0:
        # Create key word arguments
        kwargs_grid = {'input_array': [nab_raster, grid_raster, mean_interpolated],
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
