# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Composite Arctic DEM 10 m Canada
# Author: Timm Nawrocki
# Last Updated: 2019-12-03
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Composite Arctic DEM 10 m Canada" combines individual DEM tiles, reprojects to NAD 1983 Alaska Albers, and resamples to 10 m.
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
data_folder = os.path.join(drive, root_folder, 'Data/topography/ArcticDEM_10m_Canada')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
tile_folder = os.path.join(data_folder, 'tiles')
projected_folder = os.path.join(data_folder, 'tiles_projected')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define output raster
arctic10m_composite = os.path.join(data_folder, 'Elevation_ArcticDEM_10m_Canada_AKALB.tif')

# Define input and output arrays
merge_tiles_inputs = [snap_raster]
merge_tiles_outputs = [arctic10m_composite]

# Create key word arguments
merge_tiles_kwargs = {'tile_folder': tile_folder,
                     'projected_folder': projected_folder,
                     'workspace': arcpy.env.workspace,
                     'cell_size': 10,
                     'input_projection': 3413,
                     'output_projection': 3338,
                     'geographic_transformation': 'WGS_1984_(ITRF00)_To_NAD_1983',
                     'input_array': merge_tiles_inputs,
                     'output_array': merge_tiles_outputs
                     }

# Merge source tiles
arcpy_geoprocessing(merge_elevation_tiles, **merge_tiles_kwargs)
