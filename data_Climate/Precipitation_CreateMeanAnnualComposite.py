# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Mean Annual Total Precipitation Composite for 2000-2015
# Author: Timm Nawrocki
# Last Updated: 2020-05-28
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Mean Annual Total Precipitation Composite for 2000-2015" calculates the mean annual precipitation from all months for years 2000-2015. The primary data are the SNAP Alaska-Yukon 2km data. The SNAP Alaska-Canada 10 minute data fill in the included portion of Northwest Territories.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_climate_mean
from package_GeospatialProcessing import combine_climate_resolutions
from package_GeospatialProcessing import format_climate_grids
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/climatology')
data_2km = os.path.join(data_folder, 'SNAP_NorthwestNorthAmerica_2km/unprocessed')
data_15km = os.path.join(data_folder, 'SNAP_NorthwestNorthAmerica_15km/unprocessed')
processed_2km = os.path.join(data_folder, 'SNAP_NorthwestNorthAmerica_2km/processed')
processed_15km = os.path.join(data_folder, 'SNAP_NorthwestNorthAmerica_15km/processed')
data_10m = os.path.join(data_folder, 'SNAP_NorthwestNorthAmerica_10m')
gridded_folder = os.path.join(data_10m, 'gridded_full')

# Define input datasets
grid_major = os.path.join(drive, root_folder, 'Data/analyses/gridMajor')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/northAmericanBeringia_TotalArea.tif')

# Define output datasets
precipitation_2km = os.path.join(processed_2km, 'Precipitation_MeanAnnual_2km_2000-2015.tif')
precipitation_15km = os.path.join(processed_15km, 'Precipitation_MeanAnnual_15km_2000-2015.tif')
precipitation_combined = os.path.join(data_10m, 'unprocessed/Precipitation_MeanAnnual_2000-2015.tif')

# Define working geodatabase
geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')
# Set environment workspace
arcpy.env.workspace = geodatabase

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define month and property values
property_2km = 'pr_total_mm_CRU_TS40_historical'
property_15km = 'pr_total_mm_CRU-TS40_historical'
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
years = ['2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']
denominator = len(years)

# Create a list of all 2km raster data
rasters_2km = []
for year in years:
    for month in months:
        raster = os.path.join(data_2km, property_2km + '_' + month + '_' + year + '.tif')
        rasters_2km.append(raster)

# Create a list of all 15km raster data
rasters_15km = []
for year in years:
    for month in months:
        raster = os.path.join(data_15km, property_15km + '_' + month + '_' + year + '.tif')
        rasters_15km.append(raster)

# Define input and output arrays for the 2km data
inputs_2km = rasters_2km
outputs_2km = [precipitation_2km]

# Create key word arguments for the 2km data
kwargs_2km = {'input_array': inputs_2km,
              'output_array': outputs_2km,
              'denominator': denominator}

# Create a composite raster for the 2km data
if arcpy.Exists(precipitation_2km) == 0:
    print('Calculating 2km mean annual precipitation...')
    arcpy_geoprocessing(calculate_climate_mean, **kwargs_2km)
    print('----------')
else:
    print('Mean annual precipitation at 2 km resolution already exists...')
    print('----------')

# Define input and output arrays for the 15km data
inputs_15km = rasters_15km
outputs_15km = [precipitation_15km]

# Create key word arguments for the 15km data
kwargs_15km = {'input_array': inputs_15km,
              'output_array': outputs_15km,
              'denominator': denominator}

# Create a composite raster for the 15km data
if arcpy.Exists(precipitation_15km) == 0:
    print('Calculating 15km mean annual precipitation...')
    arcpy_geoprocessing(calculate_climate_mean, **kwargs_15km)
    print('----------')
else:
    print('Mean annual precipitation at 15 km resolution already exists...')
    print('----------')

# Define input and output arrays to combine climate resolutions
climate_resolution_inputs = [precipitation_2km, precipitation_15km]
climate_resolution_outputs = [precipitation_combined]

# Create key word arguments to combine climate scales
climate_resolution_kwargs = {'input_array': climate_resolution_inputs,
                             'output_array': climate_resolution_outputs}

# Combine climate resolutions
if arcpy.Exists(precipitation_combined) == 0:
    print('Combining climate resolutions into single representation...')
    arcpy_geoprocessing(combine_climate_resolutions, **climate_resolution_kwargs)
    print('----------')
else:
    print('Combined resolution mean annual precipitation already exists...')
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
print(f'Mean annual precipitation will be created for {grids_length} grids...')
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
    climate_grid = os.path.join(grid_folder, 'Precipitation_MeanAnnual' + '_AKALB_' + grid_title + '.tif')

    # If climate grid does not exist then create climate grid
    if arcpy.Exists(climate_grid) == 0:
        print(f'Processing {grid_count} of {grids_length}...')

        # Define input and output arrays
        climate_grid_inputs = [grid, precipitation_combined]
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