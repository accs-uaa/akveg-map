# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Data To Study Area
# Author: Timm Nawrocki
# Created on: 2020-05-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Extract Data to Study Area" extracts a set of predictor raster datasets to a study area to enforce the same extent on all rasters.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import extract_to_study_area

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data')

# Create gridded_select folders in each data directory if they do not already exist
input_sentinel = os.path.join(data_folder, 'imagery/sentinel-2/gridded_full')
input_modis = os.path.join(data_folder, 'imagery/modis/gridded_full')
input_topography = os.path.join(data_folder, 'topography/Composite_10m_Beringia/gridded_full')
input_grids = os.path.join(data_folder, 'analyses/GridMajor')

# Define work environment
work_geodatabase = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Identify target major grids
#grid_list = ['A5', 'A6', 'A7', 'A8',
#             'B4', 'B5', 'B8',
#             'C4', 'C5', 'C6', 'C7', 'C8',
#             'D4', 'D5', 'D6']
grid_list = ['C4', 'D4']

# Define input datasets
study_area = os.path.join(drive,
                          root_folder,
                          'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/northAmericanBeringia_ModelArea.tif')

# Loop through each grid in list and extract all predictors to study area
for grid in grid_list:
    print(f'Extracting rasters for Grid {grid}...')

    # Define the grid raster
    grid_raster = os.path.join(input_grids, "Grid_" + grid + ".tif")

    # Generate a list of rasters
    raster_list = []
    # Add topographic rasters
    arcpy.env.workspace = os.path.join(input_topography, 'Grid_' + grid)
    topo_rasters = arcpy.ListRasters('', 'TIF')
    for raster in topo_rasters:
        raster_list.append(os.path.join(arcpy.env.workspace, raster))
    # Add Sentinel-2 rasters
    arcpy.env.workspace = os.path.join(input_sentinel, 'Grid_' + grid)
    sentinel_rasters = arcpy.ListRasters('', 'TIF')
    for raster in sentinel_rasters:
        raster_list.append(os.path.join(arcpy.env.workspace, raster))
    # Add MODIS rasters
    arcpy.env.workspace = os.path.join(input_modis, 'Grid_' + grid)
    modis_rasters = arcpy.ListRasters('', 'TIF')
    for raster in modis_rasters:
        raster_list.append(os.path.join(arcpy.env.workspace, raster))

    # Set arcpy.env.workspace
    arcpy.env.workspace = work_geodatabase

    # Define raster list count
    total = len(raster_list)

    for input_raster in raster_list:
        # Identify raster index
        count = raster_list.index(input_raster) + 1
        # Define output raster and path
        output_raster = input_raster.replace('gridded_full', 'gridded_select')
        output_path = os.path.split(output_raster)[0]
        # Make output directory if it does not already exist
        if os.path.exists(output_path) == 0:
            os.mkdir(output_path)

        # Check if output already exists
        if arcpy.Exists(output_raster) == 0:
            # Define input and output arrays
            extract_inputs = [input_raster, study_area, grid_raster]
            extract_outputs = [output_raster]

            # Create key word arguments
            extract_kwargs = {'work_geodatabase': work_geodatabase,
                              'input_array': extract_inputs,
                              'output_array': extract_outputs
                              }

            # Extract raster to study area
            print(f'\tExtracting raster {count} of {total} for Grid {grid}...')
            arcpy_geoprocessing(extract_to_study_area, **extract_kwargs)
            print('\t----------')
        else:
            print(f'\tRaster {count} of {total} for Grid {grid} already exists.')