# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create hydrography tiles
# Author: Timm Nawrocki
# Last Updated: 2024-05-04
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Create hydrography tiles" creates overlapping tiles from which to calculate stream network properties.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
import arcpy
from arcpy.sa import Raster
from akutils import *

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
hydrography_folder = os.path.join(drive, root_folder, 'Data/hydrography')
output_folder = os.path.join(hydrography_folder, 'tiles_elevation')
if os.path.exists(output_folder) == 0:
    os.mkdir(output_folder)

# Define input files
area_input = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_HydrographicArea_10m_3338.tif')
elevation_input = os.path.join(hydrography_folder, 'intermediate', 'Elevation_10m_3338.tif')

# Set overwrite option
arcpy.env.overwriteOutput = True

# Specify core usage
arcpy.env.parallelProcessingFactor = "75%"

# Set snap raster
area_raster = Raster(area_input)
arcpy.env.snapRaster = area_raster

# Set cell size environment
cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
arcpy.env.cellSize = int(cell_size)

# Split elevation raster
print('Splitting raster to tiles...')
iteration_start = time.time()
arcpy.management.SplitRaster(elevation_input,
                             output_folder,
                             'Elevation_10m_3338_',
                             'SIZE_OF_TILE',
                             'TIFF',
                             'BILINEAR',
                             '',
                             '200 200',
                             '50',
                             'KILOMETERS',
                             '',
                             '',
                             '',
                             'NONE',
                             '',
                             '-32768')
end_timing(iteration_start)
