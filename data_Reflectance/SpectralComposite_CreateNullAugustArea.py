# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Null August Area
# Author: Timm Nawrocki
# Last Updated: 2020-01-16
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Null August Area" converts erroneous data in select August spectral tiles to a mask raster that can be used to uniformly remove erroneous data that follow the same spatial error pattern.
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
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/imagery/sentinel-2')
processed_folder = os.path.join(data_folder, 'processed')
mask_folder = os.path.join(data_folder, 'mask')

# Define input dataset
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define output dataset
mask_raster = os.path.join(mask_folder, 'Mask_08August.tif')

# Define working geodatabase
geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')
# Set environment workspace
arcpy.env.workspace = geodatabase

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define month and range values
month = 'Sent2_08August_4_red'
ranges = ['0000098304-0000458752',
          '0000098304-0000425984',
          '0000098304-0000393216',
          '0000098304-0000360448',
          '0000065536-0000491520',
          '0000065536-0000458752',
          '0000065536-0000425984',
          '0000065536-0000393216',
          '0000032768-0000425984',
          '0000032768-0000393216']

# Create a list of all month-property-range combinations
metrics_list = []
    for range in ranges:
        raster_path = os.path.join(processed_folder, month + '-' + range + '.tif')
        metrics_list.append(month_range)

# Define input and output arrays
create_mask_inputs = [snap_raster] + metric_list
create_mask_outputs = [mask_raster]

# Create key word arguments
create_mask_kwargs = {'input_array': merge_inputs,
                      'output_array': merge_outputs
                      }

# Process the reproject integer function
arcpy_geoprocessing(merge_spectral_tiles, **merge_kwargs)
print('----------')
