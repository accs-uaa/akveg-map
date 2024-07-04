# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate distance to coast
# Author: Timm Nawrocki
# Last Updated: 2024-07-02
# Usage: Execute in Python 3.9+.
# Description: "Calculate distance to coast" calculates the distance from the coastline and marine waters.
# ---------------------------------------------------------------------------

# Import packages
import os
import glob
import time
import arcpy
from arcpy.sa import Con
from arcpy.sa import DistanceAccumulation
from arcpy.sa import ExtractByMask
from arcpy.sa import Int
from arcpy.sa import Raster
from akutils import *

# Set nodata value
nodata = -32768

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
hydrography_folder = os.path.join(drive, root_folder, 'Data/hydrography')
tile_folder = os.path.join(hydrography_folder, 'tiles_coast')
intermediate_folder = os.path.join(hydrography_folder, 'intermediate')
output_folder = os.path.join(hydrography_folder, 'processed')

# Define geodatabases
region_geodatabase = os.path.join(project_folder, 'AKVEG_Regions.gdb')
work_geodatabase = os.path.join(project_folder, 'AKVEG_Workspace.gdb')

# Define input files
area_input = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')
coast_input = os.path.join(region_geodatabase, 'AlaskaYukon_Coast_3338')
coast_tiles = glob.glob(f'{tile_folder}/*.shp')

# Define intermediate files
coast_raster = os.path.join(intermediate_folder, 'AlaskaYukon_Coast_10m_3338_Intermediate.tif')
fill_raster = os.path.join(intermediate_folder, 'AlaskaYukon_32767_10m_3338.tif')
mosaic_raster = os.path.join(intermediate_folder, 'AlaskaYukon_CoastDist_10m_3338_Intermediate.tif')

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

# Create coast raster if it does not already exist
if os.path.exists(coast_raster) == 0:
    print('Creating coast raster...')
    iteration_start = time.time()
    arcpy.conversion.PolygonToRaster(coast_input,
                                     'OBJECTID',
                                     coast_raster,
                                     'CELL_CENTER',
                                     '',
                                     cell_size,
                                     'BUILD')
    end_timing(iteration_start)

# Calculate distance to coast for each tile if it does not already exist
input_rasters = []
count = 1
for coast_tile in coast_tiles:
    # Set processing extent and mask
    arcpy.env.extent = coast_tile
    # Define file name
    file_name = os.path.splitext(os.path.split(coast_tile)[1])[0]
    # Define output dataset
    distance_tile = os.path.join(tile_folder,
                                 file_name.replace('coast', 'CoastDist')) + '.tif'
    input_rasters.append(distance_tile)

    # Calculate distance to coast if it does not already exist
    if os.path.exists(distance_tile) == 0:
        print(f'Calculating distance {count} of {len(coast_tiles)}...')
        iteration_start = time.time()
        print(f'\tCalculating distance...')
        coast_distance = DistanceAccumulation(coast_raster)
        print(f'\tScaling distance...')
        integer_raster = Int((coast_distance * 32767 / 100000) + 0.5)
        corrected_raster = Con(integer_raster > 32767, 32767, integer_raster)
        print(f'\tExporting raster...')
        arcpy.management.CopyRaster(corrected_raster,
                                    distance_tile,
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
        end_timing(iteration_start)
    else:
        print(f'Coast distance already exists for tile {count} of {len(coast_tiles)}.')
        print('----------')
    count += 1

# Set extent
arcpy.env.extent = area_raster.extent

# Create area fill if it does not already exist
if os.path.exists(fill_raster) == 0:
    print('Creating raster with fill value of 32767...')
    iteration_start = time.time()
    con_raster = Con(area_raster == 1, 32767, area_raster)
    arcpy.management.CopyRaster(con_raster,
                                fill_raster,
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
    end_timing(iteration_start)
input_rasters.append(fill_raster)

# Mosaic tiles to new raster
if os.path.exists(mosaic_raster) == 0:
    arcpy.management.MosaicToNewRaster(input_rasters,
                                       os.path.split(mosaic_raster)[0],
                                       os.path.split(mosaic_raster)[1],
                                       output_system,
                                       '16_BIT_SIGNED',
                                       cell_size,
                                       1,
                                       'MINIMUM',
                                       'FIRST')

# Extract to area raster
print('Extracting raster to study area...')
iteration_start = time.time()
extract_raster = ExtractByMask(mosaic_raster, area_raster)
end_timing(iteration_start)

# Export raster
print('Exporting coast distance raster as 16-bit signed...')
iteration_start = time.time()
arcpy.management.CopyRaster(extract_raster,
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
end_timing(iteration_start)
