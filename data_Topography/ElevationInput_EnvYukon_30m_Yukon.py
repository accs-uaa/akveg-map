# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Reproject EnvYukon 30 m Yukon DEM
# Author: Timm Nawrocki
# Last Updated: 2019-12-03
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Reproject EnvYukon 30 m Yukon DEM" reprojects to NAD 1983 Alaska Albers and resamples to 10 m.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import reproject_integer
import os

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/EnvYukon_30m_Yukon')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
input_raster = os.path.join(data_folder, 'original/yt_30m_dem.tif')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define output raster
output_raster = os.path.join(data_folder, 'Elevation_EnvYukon_30m_Yukon_AKALB.tif')

# Define input and output arrays
reproject_integer_inputs = [input_raster, snap_raster]
reproject_integer_outputs = [output_raster]

# Create key word arguments
reproject_integer_kwargs = {'cell_size': 10,
                            'input_projection': 3578,
                            'output_projection': 3338,
                            'geographic_transformation': '',
                            'conversion_factor': 1,
                            'input_array': reproject_integer_inputs,
                            'output_array': reproject_integer_outputs
                            }

# Process the reproject integer function
arcpy_geoprocessing(reproject_integer, **reproject_integer_kwargs)
