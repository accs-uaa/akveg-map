# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Null August Area
# Author: Timm Nawrocki
# Last Updated: 2020-01-18
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Null August Area" converts erroneous data in select August spectral tiles to a mask raster that can be used to uniformly remove erroneous data that follow the same spatial error pattern.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_mask_raster

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/imagery/sentinel-2')
processed_folder = os.path.join(data_folder, 'processed')
mask_folder = os.path.join(data_folder, 'mask')

# Define input dataset
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/northAmericanBeringia_TotalArea.tif')
extent_feature = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb/NorthAmericanBeringia_ModelArea')

# Define output dataset
mask_raster = os.path.join(mask_folder, 'Mask_08August.tif')

# Define mask threshold value
threshold = 200

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
    month_range = os.path.join(processed_folder, month + '-' + range + '.tif')
    metrics_list.append(month_range)

# Define input and output arrays
create_mask_inputs = [snap_raster, extent_feature] + metrics_list
create_mask_outputs = [mask_raster]

# Create key word arguments
create_mask_kwargs = {'threshold': threshold,
                      'input_array': create_mask_inputs,
                      'output_array': create_mask_outputs
                      }

# Process the reproject integer function
print('Creating mask raster...')
arcpy_geoprocessing(create_mask_raster, **create_mask_kwargs)
print('----------')
