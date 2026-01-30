# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge hydrography datasets
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in an ArcGIS Pro Python 3.11+ installation.
# Description: "Merge hydrography datasets" combines individual tiles into final rasters for each hydrography dataset.
# ---------------------------------------------------------------------------

# Import packages
import glob
import os
import time
import arcpy
from arcpy.sa import ExtractByMask
from arcpy.sa import Raster
from akutils import *

# Set nodata value
nodata = -32768

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
hydrography_folder = os.path.join(drive, root_folder, 'Data/hydrography')
tile_folder = os.path.join(hydrography_folder, 'tiles_hydrography')
intermediate_folder = os.path.join(hydrography_folder, 'intermediate')
output_folder = os.path.join(hydrography_folder, 'processed')

# Define input files
area_input = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')
wetness_files = glob.glob(f'{tile_folder}/Wetness*.tif')
stream_files = glob.glob(f'{tile_folder}/StreamDist*.tif')
river_files = glob.glob(f'{tile_folder}/RiverDist*.tif')

# Define output files
wetness_intermediate = 'Wetness_10m_3338_Merged.tif'
wetness_output = os.path.join(output_folder, 'Wetness_10m_3338.tif')
stream_intermediate = 'StreamDist_10m_3338_Merged.tif'
stream_output = os.path.join(output_folder, 'StreamDist_10m_3338.tif')
river_intermediate = 'RiverDist_10m_3338_Merged.tif'
river_output = os.path.join(output_folder, 'RiverDist_10m_3338.tif')

#### MERGE HYDROGRAPHIC RASTERS
####____________________________________________________

# Define output projection
output_system = arcpy.SpatialReference(3338)

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

# Merge wetness rasters
if os.path.exists(os.path.join(intermediate_folder, wetness_intermediate)) == 0:
    print(f'Merging wetness rasters...')
    iteration_start = time.time()
    # Mosaic rasters tiles
    arcpy.management.MosaicToNewRaster(wetness_files,
                                       intermediate_folder,
                                       wetness_intermediate,
                                       output_system,
                                       '16_BIT_SIGNED',
                                       cell_size,
                                       1,
                                       'MAXIMUM',
                                       'FIRST')
    end_timing(iteration_start)

# Create output wetness raster
if os.path.exists(wetness_output) == 0:
    print(f'Creating output wetness raster...')
    iteration_start = time.time()
    # Extract raster to mask
    extract_raster = ExtractByMask(os.path.join(intermediate_folder, wetness_intermediate), area_input)
    # Export raster
    print('\tExporting 16-bit signed raster...')
    arcpy.management.CopyRaster(extract_raster,
                                wetness_output,
                                '',
                                '',
                                nodata,
                                'NONE',
                                'NONE',
                                '16_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    print('\tBuilding pyramids...')
    arcpy.management.BuildPyramids(wetness_output,
                                   '-1',
                                   'NONE',
                                   'BILINEAR',
                                   'LZ77',
                                   '',
                                   'OVERWRITE')
    print('\tCalculating statistics...')
    arcpy.management.CalculateStatistics(wetness_output)
    end_timing(iteration_start)

# Merge stream distance rasters
if os.path.exists(os.path.join(intermediate_folder, stream_intermediate)) == 0:
    print(f'Merging stream distance rasters...')
    iteration_start = time.time()
    # Mosaic rasters tiles
    arcpy.management.MosaicToNewRaster(stream_files,
                                       intermediate_folder,
                                       stream_intermediate,
                                       output_system,
                                       '16_BIT_SIGNED',
                                       cell_size,
                                       1,
                                       'MINIMUM',
                                       'FIRST')
    end_timing(iteration_start)

# Create output stream distance raster
if os.path.exists(stream_output) == 0:
    print(f'Creating output stream distance raster...')
    iteration_start = time.time()
    # Extract raster to mask
    extract_raster = ExtractByMask(os.path.join(intermediate_folder, stream_intermediate), area_input)
    # Export raster
    print('\tExporting 16-bit signed raster...')
    arcpy.management.CopyRaster(extract_raster,
                                stream_output,
                                '',
                                '',
                                nodata,
                                'NONE',
                                'NONE',
                                '16_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    print('\tBuilding pyramids...')
    arcpy.management.BuildPyramids(stream_output,
                                   '-1',
                                   'NONE',
                                   'BILINEAR',
                                   'LZ77',
                                   '',
                                   'OVERWRITE')
    print('\tCalculating statistics...')
    arcpy.management.CalculateStatistics(stream_output)
    end_timing(iteration_start)

# Merge river distance rasters
if os.path.exists(os.path.join(intermediate_folder, river_intermediate)) == 0:
    print(f'Merging river distance rasters...')
    iteration_start = time.time()
    # Mosaic rasters tiles
    arcpy.management.MosaicToNewRaster(river_files,
                                       intermediate_folder,
                                       river_intermediate,
                                       output_system,
                                       '16_BIT_SIGNED',
                                       cell_size,
                                       1,
                                       'MINIMUM',
                                       'FIRST')
    end_timing(iteration_start)

# Create output river distance raster
if os.path.exists(river_output) == 0:
    print(f'Creating output river distance raster...')
    iteration_start = time.time()
    # Extract raster to mask
    extract_raster = ExtractByMask(os.path.join(intermediate_folder, river_intermediate), area_input)
    # Export raster
    print('\tExporting 16-bit signed raster...')
    arcpy.management.CopyRaster(extract_raster,
                                river_output,
                                '',
                                '',
                                nodata,
                                'NONE',
                                'NONE',
                                '16_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    print('\tBuilding pyramids...')
    arcpy.management.BuildPyramids(river_output,
                                   '-1',
                                   'NONE',
                                   'BILINEAR',
                                   'LZ77',
                                   '',
                                   'OVERWRITE')
    print('\tCalculating statistics...')
    arcpy.management.CalculateStatistics(river_output)
    end_timing(iteration_start)
