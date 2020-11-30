# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Elevation Composite
# Author: Timm Nawrocki
# Last Updated: 2020-11-30
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Elevation Composite" creates a composite from multiple source DEMs based on order of priority. All sources must be in the same projection with the same cell size and grid. The grid tiles must be predefined as rasters.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_composite_dem
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography')

# Define input datasets
grid_major = os.path.join(drive, root_folder, 'Data/analyses/gridMajor')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input/northAmericanBeringia_TotalArea.tif')

# Define source_rasters
source_USGS_5m = os.path.join(data_folder, 'USGS3DEP_5m_Alaska/Elevation_USGS3DEP_5m_Alaska_AKALB.tif')
source_USGS_30m = os.path.join(data_folder, 'USGS3DEP_30m_Canada/Elevation_USGS3DEP_30m_Canada_AKALB.tif')
source_USGS_60m = os.path.join(data_folder, 'USGS3DEP_60m_Alaska/Elevation_USGS3DEP_60m_Alaska_AKALB.tif')
source_Alaska_10m = os.path.join(data_folder, 'ArcticDEM_10m_Alaska/Elevation_ArcticDEM_10m_Alaska_AKALB.tif')
source_Canada_10m = os.path.join(data_folder, 'ArcticDEM_10m_Canada/Elevation_ArcticDEM_10m_Canada_AKALB.tif')
source_Yukon_30m = os.path.join(data_folder, 'EnvYukon_30m_Yukon/Elevation_EnvYukon_30m_Yukon_AKALB.tif')

# Define prioritized list of elevation inputs
elevation_inputs = [source_USGS_5m, source_Alaska_10m, source_Canada_10m, source_USGS_30m, source_Yukon_30m, source_USGS_60m]

# Define root output name
mosaic_name_root = 'Elevation_Composite_10m_Beringia_AKALB_'

# Set overwrite option
arcpy.env.overwriteOutput = True

# List grid rasters
print('Searching for grid rasters...')
# Start timing function
iteration_start = time.time()
# Set environment workspace to the folder containing the grid rasters
arcpy.env.workspace = grid_major
# Create a raster list using the Arcpy List Rasters function
raster_list = arcpy.ListRasters('*', 'TIF')
# Append file names to rasters in list
grids = []
for raster in raster_list:
    raster_path = os.path.join(grid_major, raster)
    grids.append(raster_path)
grids_length = len(grids)
print(f'Elevation composites will be created for {grids_length} grids...')
# End timing
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
# Report success
print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Iterate through each buffered grid and create elevation composite
for grid in grids:
    # Define composite raster name
    grid_title = os.path.splitext(os.path.split(grid)[1])[0]

    # Define mosaic name and location
    mosaic_location = os.path.join(data_folder, 'Composite_10m_Beringia', grid_title + '_full')
    mosaic_name = mosaic_name_root + grid_title + '.tif'
    output_mosaic = os.path.join(mosaic_location, mosaic_name)

    # Create elevation composite for grid if one does not already exist
    if os.path.exists(output_mosaic) == 0:
        print(f'Creating elevation composite for {grid_title}...')

        # Define input and output arrays
        elevation_composite_inputs = [grid] + elevation_inputs
        elevation_composite_outputs = [output_mosaic]

        # Create key word arguments
        elevation_composite_kwargs = {'cell_size': 10,
                                      'output_projection': 3338,
                                      'input_array': elevation_composite_inputs,
                                      'output_array': elevation_composite_outputs
                                      }

        # Process the elevation composite
        arcpy_geoprocessing(create_composite_dem, **elevation_composite_kwargs, check_output=False)
        print('----------')

    else:
        print(f'Elevation composite already exists for {grid_title}...')
        print('----------')
