# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Composite USGS 3DEP 60 m Alaska
# Author: Timm Nawrocki
# Last Updated: 2019-10-30
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Composite USGS 3DEP 60 m Alaska" combines individual DEM tiles, reprojects to NAD 1983 Alaska Albers, and resamples to 10 m.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_composite_dem
import os

# Set root directory
drive = 'K:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS3DEP_60m_Alaska')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
tile_folder = os.path.join(data_folder, 'tiles')
projected_folder = os.path.join(data_folder, 'tiles_projected')
snap_raster = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define output raster
alaska60m_composite = os.path.join(data_folder, 'Elevation_USGS3DEP_60m_Alaska_AKALB.tif')

# Define input and output arrays
create_dem_inputs = [snap_raster]
create_dem_outputs = [alaska60m_composite]

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
