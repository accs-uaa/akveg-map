# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Remove August Erroneous Data
# Author: Timm Nawrocki
# Last Updated: 2020-01-16
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Remove August Erroneous Data" converts erroneous data in select August spectral tiles to no data to avoid contamination by sensor errors. Removed data is imputed from the mean of surrounding valid data in the "Create Spectral Composite" script.
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
corrected_folder = os.path.join(data_folder, 'corrected')

# Define input datasets
grid_major = os.path.join(drive, root_folder, 'Data/analyses/gridMajor')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define working geodatabase
geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')
# Set environment workspace
arcpy.env.workspace = geodatabase

# Set overwrite option
arcpy.env.overwriteOutput = True

months = '08August'
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

# Create a list of all month-property-range combinations
metrics_list = []
for month in months:
    for range in ranges:
        for property in properties:
            month_property = month + '_' + property
            metrics_list.append(month_property)