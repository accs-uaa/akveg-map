# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Composite USGS 3DEP 10 m Alaska
# Author: Timm Nawrocki
# Last Updated: 2021-02-23
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Composite USGS 3DEP 10 m Alaska" combines individual DEM tiles, reprojects to NAD 1983 Alaska Albers, and resamples to 10 m.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import merge_elevation_tiles
import os

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS3DEP_10m_Alaska')

# Set arcpy working environment
work_geodatabase = os.path.join(drive, root_folder,
                                   'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/BeringiaVegetation.gdb')

# Define input datasets
tile_folder = os.path.join(data_folder, 'tiles')
projected_folder = os.path.join(data_folder, 'tiles_projected')
snap_raster = os.path.join(drive, root_folder,
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input/northAmericanBeringia_ModelArea.tif')

# Define output raster
usgs10m_composite = os.path.join(data_folder, 'Elevation_USGS3DEP_10m_Alaska_AKALB.tif')

# Define input and output arrays
merge_tiles_inputs = [snap_raster]
merge_tiles_outputs = [usgs10m_composite]

# Create key word arguments
merge_tiles_kwargs = {'tile_folder': tile_folder,
                      'projected_folder': projected_folder,
                      'workspace': work_geodatabase,
                      'cell_size': 10,
                      'input_projection': 4269,
                      'output_projection': 3338,
                      'geographic_transformation': '',
                      'input_array': merge_tiles_inputs,
                      'output_array': merge_tiles_outputs
                      }

# Merge source tiles
arcpy_geoprocessing(merge_elevation_tiles, **merge_tiles_kwargs)