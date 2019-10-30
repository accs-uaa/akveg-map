# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Reproject 60 m USGS DEM
# Author: Timm Nawrocki
# Created on: 2019-10-25
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Reproject 60 m USGS DEM" reprojects to NAD 1983 Alaska Albers and resamples to 10 m.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from beringianGeospatialProcessing import arcpy_geoprocessing
from beringianGeospatialProcessing import reproject_integer

# Set root directory
drive = 'K:/'
root_directory = os.path.join(drive, 'ACCS_Work/Data/topography/USGS_60m')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
input_raster = os.path.join(root_directory, 'Alaska_USGS3DEP_Elevation_2ArcSecond_NAD83_20181106.tif')
snap_raster = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define output raster
output_raster = os.path.join(root_directory, 'Resample_10m/Alaska_USGS3DEP_Elevation_60m_AKALB_20191025.tif')

# Define input and output arrays
reproject_integer_inputs = [input_raster, snap_raster]
reproject_integer_outputs = [output_raster]

# Create key word arguments
reproject_integer_kwargs = {'cell_size': 10,
                            'input_projection': 4269,
                            'output_projection': 3338,
                            'geographic_transformation': '',
                            'input_array': reproject_integer_inputs,
                            'output_array': reproject_integer_outputs
                            }

# Process the create polygon function with the point array
arcpy_geoprocessing(reproject_integer, **reproject_integer_kwargs)
