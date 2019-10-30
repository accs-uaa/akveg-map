# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Major Grid Rasters
# Author: Timm Nawrocki
# Created on: 2019-10-29
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Major Grid Rasters" creates 10 m rasters for each major grid.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from arcpy.sa import ExtractByMask
import datetime
import pandas as pd
import os
import time
from beringianGeospatialProcessing import arcpy_geoprocessing

# Set root directory
drive = 'K:/'
root_directory = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
raster_csv = os.path.join(drive, 'ACCS_Work/Data/elevation/NorthAmericanBeringia_10m/Raster_Inputs.csv')
major_grids = os.path.join(root_directory, 'Analysis_GridMajor.gdb')
snap_raster = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Read raster file paths from csv
raster_df = pd.read_csv(raster_csv)
raster_paths = list(raster_df.file_path)
raster_names = list(raster_df.name)

# Define folder paths
major_folder = os.path.join(root_directory, 'Data_Input/majorGrid')

# Set overwrite option
arcpy.env.overwriteOutput = True

# Set snap raster
arcpy.env.snapRaster = snap_raster

# Convert grid tiles to rasters
grid_features = arcpy.ListFeatureClasses('*', 'Polygon')
# Set length and count
length = len(grid_features)
count = 1
# Print initial status
print(f'Converting {length} grids to raster...')
for grid in grid_features:
    # Define output grid raster
    grid_raster = os.path.join(major_folder, os.path.split(grid)[1] + '.tif')
    # If grid raster does not exist, then create grid raster
    if arcpy.Exists(grid_raster) == 0:
        # Start timing function
        iteration_start = time.time()
        # Print initial status
        print(f'\tConverting grid {count} of {length} to raster...')
        # Convert feature class to raster
        arcpy.FeatureToRaster(grid, 'OID', grid_raster, 10)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tOutput grid raster {count} of {length} completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tOutput grid {count} of {length} already exists...')
        print('\t----------')
    count += 1
