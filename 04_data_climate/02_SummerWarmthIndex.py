# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate mean summer warmth index for 2006-2015
# Author: Timm Nawrocki
# Last Updated: 2024-06-30
# Usage: Must be executed in an ArcGIS Pro Python 3.9+ installation.
# Description: "Calculate mean summer warmth index for 2006-2015" calculates the mean annual summer warmth index from May-September for years 2000-2015. The primary data are the SNAP Alaska-Yukon 2km data with the included portion of the Northwest Territories interpolated by geographic nearest neighbors.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
from akutils import *
import arcpy
from arcpy.sa import CellStatistics
from arcpy.sa import Int
from arcpy.sa import ExtractByMask
from arcpy.sa import Nibble
from arcpy.sa import Raster

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
data_folder = os.path.join(drive, root_folder, 'Data/climatology/temperature')
unprocessed_folder = os.path.join(data_folder, 'unprocessed/2km')
processed_folder = os.path.join(data_folder, 'processed')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Workspace.gdb')

# Define input datasets
area_input = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')

# Define output datasets
summer_output = os.path.join(processed_folder, 'SummerWarmth_MeanAnnual_2006_2015_10m_3338.tif')

# Define month and property values
climate_property = 'tas_mean_C_CRU_TS40_historical'
months = ['05', '06', '07', '08', '09']
years = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']
denominator = len(years)

# Create a list of all climate raster data
raster_list = []
for year in years:
    for month in months:
        raster = os.path.join(unprocessed_folder, climate_property + '_' + month + '_' + year + '.tif')
        raster_list.append(raster)

# Set overwrite option
arcpy.env.overwriteOutput = True

# Specify core usage
arcpy.env.parallelProcessingFactor = "75%"

# Set snap raster and extent
area_raster = Raster(area_input)
arcpy.env.snapRaster = area_raster
arcpy.env.extent = area_raster.extent

# Set cell size environment
cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
arcpy.env.cellSize = int(cell_size)

# Set environment workspace
arcpy.env.workspace = work_geodatabase

# Calculate mean annual summer warmth index
print('Calculating mean annual summer warmth index...')
iteration_start = time.time()
sum_raster = CellStatistics(raster_list, 'SUM', 'NODATA', 'SINGLE_BAND', '', '')
mean_raster = sum_raster / 10
end_timing(iteration_start)

# Interpolate missing data
print('Interpolating missing data from geographic nearest neighbors...')
iteration_start = time.time()
nibble_raster = Nibble(mean_raster,
                       mean_raster,
                       'DATA_ONLY',
                       'PROCESS_NODATA')
end_timing(iteration_start)

# Convert to integer
print('Converting to integer...')
iteration_start = time.time()
integer_raster = Int((nibble_raster) + 0.5)
end_timing(iteration_start)

# Extract to area raster
print('Extracting raster to study area...')
iteration_start = time.time()
extract_integer = ExtractByMask(integer_raster, area_raster)
end_timing(iteration_start)

# Export raster
print('Exporting coast distance raster as 16-bit signed...')
iteration_start = time.time()
arcpy.management.CopyRaster(extract_integer,
                            summer_output,
                            '',
                            '',
                            '-32768',
                            'NONE',
                            'NONE',
                            '16_BIT_SIGNED',
                            'NONE',
                            'NONE',
                            'TIFF',
                            'NONE')
arcpy.management.BuildPyramids(summer_output,
                               '-1',
                               'NONE',
                               'BILINEAR',
                               'LZ77',
                               '',
                               'OVERWRITE')
arcpy.management.CalculateStatistics(summer_output)
end_timing(iteration_start)
