# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Process Sentinel-2 Tiles
# Author: Timm Nawrocki
# Last Updated: 2019-12-30
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Process Sentinel-2 Tiles" reprojects tiles and converts to integer.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import reproject_integer
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/imagery/sentinel-2')
unprocessed_folder = os.path.join(data_folder, 'unprocessed/select')
processed_folder = os.path.join(data_folder, 'processed')

# Define input datasets
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/northAmericanBeringia_TotalArea.tif')

# Define working geodatabase
geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Set overwrite option
arcpy.env.overwriteOutput = True

# List imagery tiles
print('Searching for imagery tiles...')
# Start timing function
iteration_start = time.time()
# Set environment workspace to the folder containing the grid rasters
arcpy.env.workspace = unprocessed_folder
# Create a raster list using the Arcpy List Rasters function
unprocessed_list = arcpy.ListRasters('*', 'TIF')
# Append file names to rasters in list
unprocessed_tiles = []
for raster in unprocessed_list:
    raster_path = os.path.join(unprocessed_folder, raster)
    unprocessed_tiles.append(raster_path)
tiles_length = len(unprocessed_tiles)
print(f'Spectral composites will be created from {tiles_length} imagery tiles...')
# End timing
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
# Report success
print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Reset environment workspace
arcpy.env.workspace = geodatabase
# Set initial tile count
tile_count = 1

# Reproject all imagery tiles
for tile in unprocessed_tiles:
    # Define processed raster tile
    processed_tile = os.path.join(processed_folder, os.path.split(tile)[1])

    # Reproject and convert tile if processed tile does not already exist
    if arcpy.Exists(processed_tile) == 0:
        print(f'Processing tile {tile_count} of {tiles_length}...')

        # Define input and output arrays
        reproject_inputs = [tile, snap_raster]
        reproject_outputs = [processed_tile]

        # Create key word arguments
        reproject_kwargs = {'cell_size': 10,
                            'input_projection': 4326,
                            'output_projection': 3338,
                            'geographic_transformation': 'WGS_1984_(ITRF00)_To_NAD_1983',
                            'conversion_factor': 10000,
                            'input_array': reproject_inputs,
                            'output_array': reproject_outputs
                            }

        # Process the reproject integer function
        arcpy_geoprocessing(reproject_integer, **reproject_kwargs)
        print('----------')

    else:
        print(f'Tile {tile_count} of {tiles_length} already exists.')
        print('----------')

    # Increase counter
    tile_count += 1
