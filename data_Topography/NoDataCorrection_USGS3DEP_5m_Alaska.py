# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Correct No Data Values in USGS 3DEP 5 m Alaska
# Author: Timm Nawrocki
# Last Updated: 2021-02-24
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Correct No Data Values in USGS 3DEP 5 m Alaska" changes values less than -20 to No Data.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import correct_no_data
import os

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS3DEP_5m_Alaska')

# Set arcpy working environment
work_geodatabase = os.path.join(drive, root_folder,
                                'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/BeringiaVegetation.gdb')

# Define input datasets
snap_raster = os.path.join(drive, root_folder,
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input/northAmericanBeringia_ModelArea.tif')
input_raster = os.path.join(data_folder, 'Elevation_USGS3DEP_5m_Alaska_AKALB.tif')

# Define output raster
output_raster = os.path.join(data_folder, 'Elevation_USGS3DEP_5m_Alaska_AKALB_Corrected.tif')

# Define input and output arrays
correction_inputs = [snap_raster, input_raster]
correction_outputs = [output_raster]

# Create key word arguments
correction_kwargs = {'value_threshold': -20,
                     'direction': 'below',
                     'work_geodatabase': work_geodatabase,
                     'input_array': correction_inputs,
                     'output_array': correction_outputs
                     }

# Merge source tiles
arcpy_geoprocessing(correct_no_data, **correction_kwargs)
