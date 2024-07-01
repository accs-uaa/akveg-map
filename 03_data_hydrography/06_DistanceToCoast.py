# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate distance to coast
# Author: Timm Nawrocki
# Last Updated: 2024-06-30
# Usage: Execute in Python 3.9+.
# Description: "Calculate distance to coast" calculates the distance from the coastline and marine waters.
# ---------------------------------------------------------------------------

# Import packages
import os
import arcpy
from arcpy.sa import Con
from arcpy.sa import DistanceAccumulation
from arcpy.sa import ExtractByMask
from arcpy.sa import Int
from arcpy.sa import IsNull
from arcpy.sa import Raster
from arcpy.sa import SetNull
from akutils import *

# Set nodata value
nodata = -32768

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
hydrography_folder = os.path.join(drive, root_folder, 'Data/hydrography')
output_folder = os.path.join(hydrography_folder, 'processed')

# Define geodatabases
region_geodatabase = os.path.join(project_folder, 'AKVEG_Regions.gdb')
work_geodatabase = os.path.join(project_folder, 'AKVEG_Workspace.gdb')

# Define input files
area_input = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')
coast_input = os.path.join(region_geodatabase, 'AlaskaYukon_Coast_3338')

# Define output files
coast_output = os.path.join(output_folder, 'CoastDist_10m_3338.tif')

# Define output projection
output_system = arcpy.SpatialReference(3338)

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

# Calculate distance to coast
print('Calculating distance to coast...')
coast_distance = DistanceAccumulation(coast_input)

# Convert to integer
print('Converting to integer...')
integer_raster = Int((coast_distance) + 0.5)
corrected_raster = Con(integer_raster > 32767, 32767, integer_raster)

# Extract to area raster
print('Extracting raster to study area...')
extract_integer = ExtractByMask(corrected_raster, area_raster)

# Export raster
print('Exporting coast distance raster as 16-bit signed...')
arcpy.management.CopyRaster(extract_integer,
                            coast_output,
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
arcpy.management.BuildPyramids(coast_output,
                               '-1',
                               'NONE',
                               'BILINEAR',
                               'LZ77',
                               '',
                               'OVERWRITE')
arcpy.management.CalculateStatistics(coast_output)
