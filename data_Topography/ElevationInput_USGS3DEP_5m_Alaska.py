# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create composite USGS 3DEP 5 m Alaska
# Author: Timm Nawrocki
# Last Updated: 2021-11-20
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create composite USGS 3DEP 5 m Alaska" combines individual DEM tiles, reprojects to NAD 1983 Alaska Albers, and resamples to 10 m.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import correct_no_data
from package_GeospatialProcessing import merge_elevation_tiles
import os

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS_3DEP_5m')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
tile_folder = os.path.join(data_folder, 'tiles')
projected_folder = os.path.join(data_folder, 'tiles_projected')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')

# Define input datasets
alaska_raster = os.path.join(project_folder, 'Data_Input/AlaskaCombined_TotalArea.tif')

# Define output datasets
output_raster = os.path.join(data_folder, 'Elevation_5m_Alaska_AKALB.tif')
corrected_raster = os.path.join(data_folder, 'Elevation_5m_Alaska_AKALB_Corrected.tif')

#### CREATE COMPOSITE DEM

# Create key word arguments
kwargs_merge = {'tile_folder': tile_folder,
                'projected_folder': projected_folder,
                'workspace': work_geodatabase,
                'cell_size': 10,
                'input_projection': 3338,
                'output_projection': 3338,
                'geographic_transformation': '',
                'input_array': [alaska_raster],
                'output_array': [output_raster]
                }

# Merge source tiles
arcpy_geoprocessing(merge_elevation_tiles, **kwargs_merge)

#### CORRECT COMPOSITE DEM

# Create key word arguments
kwargs_correction = {'value_threshold': -20,
                     'direction': 'below',
                     'work_geodatabase': work_geodatabase,
                     'input_array': [alaska_raster, output_raster],
                     'output_array': [output_raster]
                     }

# Merge source tiles
arcpy_geoprocessing(correct_no_data, **kwargs_correction)
