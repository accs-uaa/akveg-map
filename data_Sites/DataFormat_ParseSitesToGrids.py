# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse Sites to Grids
# Author: Timm Nawrocki
# Created on: 2020-05-06
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Parse Sites to Grids" prepares a table of point data for feature extraction by selecting appropriate raster cells based on cell size and splits raster points by major grids.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import format_site_data
from package_GeospatialProcessing import parse_site_data

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input')

# Create parsed folder within data folder if it does not already exist
parsed_folder = os.path.join(data_folder, 'sites/parsed')
if os.path.exists(parsed_folder) == 0:
    os.mkdir(parsed_folder)

# Define work environment
work_geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
site_table = os.path.join(data_folder, 'sites/sites_all.csv')
grid_major = os.path.join(drive, root_folder, 'Data/analyses/NorthAmericanBeringia_GridIndex_Major_400km_Selected.shp')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/northAmericanBeringia_TotalArea.tif')

# Define output point feature class
sites_formatted = os.path.join(work_geodatabase, 'sites_formatted')

# Set overwrite option
arcpy.env.overwriteOutput = True

# Define input and output arrays
sites_inputs = [site_table, snap_raster]
sites_outputs = [sites_formatted]

# Create key word arguments
sites_kwargs = {'work_geodatabase': work_geodatabase,
                'input_array': sites_inputs,
                'output_array': sites_outputs
                }

# Format site data
print(f'Formatting site data...')
arcpy_geoprocessing(format_site_data, **sites_kwargs)
print('----------')

# Define input array
parsed_inputs = [sites_formatted, grid_major]

# Initiate a search cursor to read the grid name for each grid
with arcpy.da.SearchCursor(grid_major, ['Major']) as cursor:
    for row in cursor:
        grid_name = row[0]

        # Define output array
        output_shapefile = os.path.join(parsed_folder, grid_name + '.shp')
        parsed_outputs = [output_shapefile]

        # Create key word arguments
        parsed_kwargs = {'work_geodatabase': work_geodatabase,
                         'grid_name': grid_name,
                         'input_array': parsed_inputs,
                         'output_array': parsed_outputs
                         }

        # Parse site data
        print(f'Parsing site data for grid {grid_name}...')
        arcpy_geoprocessing(parse_site_data, **parsed_kwargs)
        print('----------')
