# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create composite USGS 3DEP 10m Alaska
# Author: Timm Nawrocki
# Last Updated: 2021-11-22
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create composite USGS 3DEP 10m Alaska" combines individual DEM tiles, reprojects to NAD 1983 Alaska Albers, and resamples to 10 m.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import merge_elevation_tiles
import os

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS_3DEP_10m')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data')
tile_folder = os.path.join(data_folder, 'tiles')
projected_folder = os.path.join(data_folder, 'tiles_projected')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')

# Define input datasets
alaska_raster = os.path.join(project_folder, 'Data_Input/AlaskaCombined_TotalArea.tif')

# Define output datasets
output_raster = os.path.join(data_folder, 'Elevation_10m_Alaska_AKALB.tif')

#### CREATE COMPOSITE DEM

# Create key word arguments
kwargs_merge = {'tile_folder': tile_folder,
                'projected_folder': projected_folder,
                'workspace': work_geodatabase,
                'cell_size': 10,
                'input_projection': 4269,
                'output_projection': 3338,
                'geographic_transformation': '',
                'input_array': [alaska_raster],
                'output_array': [output_raster]
                }

# Merge source tiles
arcpy_geoprocessing(merge_elevation_tiles, **kwargs_merge)
