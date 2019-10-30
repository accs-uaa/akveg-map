# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Composite 10 m USGS DEM
# Author: Timm Nawrocki
# Created on: 2019-10-19
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Composite 10 m USGS DEM" combines individual DEM tiles, reprojects to NAD 1983 Alaska Albers, and resamples to 10 m.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from beringianGeospatialProcessing import arcpy_geoprocessing
from beringianGeospatialProcessing import create_composite_dem

# Set root directory
drive = 'K:/'
root_directory = os.path.join(drive, 'ACCS_Work/Data/topography/USGS_10m')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
tile_folder = os.path.join(root_directory, 'tiles')
projected_folder = os.path.join(root_directory, 'tiles_projected')
snap_raster = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define output raster
usgs10m_composite = os.path.join(root_directory, 'Alaska_USGS3DEP_Elevation_10m_AKALB_20191019.tif')

# Define input and output arrays
create_dem_inputs = [snap_raster]
create_dem_outputs = [usgs10m_composite]

# Create key word arguments
create_dem_kwargs = {'tile_folder': tile_folder,
                     'projected_folder': projected_folder,
                     'cell_size': 10,
                     'input_projection': 4269,
                     'output_projection': 3338,
                     'geographic_transformation': '',
                     'input_array': create_dem_inputs,
                     'output_array': create_dem_outputs
                     }

# Process the create polygon function with the point array
arcpy_geoprocessing(create_composite_dem, **create_dem_kwargs)
