# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process Abundance Rasters
# Author: Timm Nawrocki
# Created on: 2020-06-04
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Post-process Abundance Rasters" merges raster tiles and controls for water.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import postprocess_abundance

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define species folder
species_folder = 'alnus'
output_name = 'Alnus'

# Define data folder
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Output')

# Define input and output raster folders
input_folder = os.path.join(data_folder, 'predicted_rasters', species_folder)
output_folder = os.path.join(data_folder, 'rasters_final', species_folder)

# Define work environment
work_geodatabase = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
snap_raster = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/northAmericanBeringia_ModelArea.tif')

# Add species tile rasters to list
tile_list = []
arcpy.env.workspace = input_folder
tile_rasters = arcpy.ListRasters('', 'IMG')
for raster in tile_rasters:
    tile_list.append(os.path.join(arcpy.env.workspace, raster))

# Set environment workspace
arcpy.env.workspace = work_geodatabase

# Make output directory if it does not already exist
if os.path.exists(output_folder) == 0:
    os.mkdir(output_folder)

# Define output raster
output_raster = os.path.join(output_folder, 'NorthAmericanBeringia_' + output_name + '.tif')

# Define input and output arrays
process_inputs = [snap_raster] + tile_list
process_outputs = [output_raster]

# Create key word arguments
process_kwargs = {'work_geodatabase': work_geodatabase,
                  'cell_size': 10,
                  'output_projection': 3338,
                  'input_array': process_inputs,
                  'output_array': process_outputs
                  }

# Extract raster to study area
print(f'Post-processing raster...')
arcpy_geoprocessing(postprocess_abundance, **process_kwargs)
print('----------')