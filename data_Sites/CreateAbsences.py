# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Absences
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Absences" generates random absence points for glaciers and lakes, Picea species, and Betula trees.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import table_to_feature_projected

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'DataProjects/VegetationEcology/AKVEG_QuantitativeMap/Data')

# Define work geodatabase
work_geodatabase = os.path.join(data_folder, 'BeringiaVegetation.gdb')

# Define input datasets
study_area = os.path.join(work_geodatabase, 'NorthAmericanBeringia_ModelArea')
lake_glacier = os.path.join(work_geodatabase, 'NorthAmericanBeringia_LakeGlacier')
subarctic_region = os.path.join(work_geodatabase, 'mapRegion_Subarctic')
spruce_range = os.path.join(work_geodatabase, 'range_PiceaGlauca')
betula_range = os.path.join(work_geodatabase, 'range_BetulaTrees')
sites_file = os.path.join(data_folder, 'Data_Input/sites/sites_all.csv')

# Define output datasets
sites_feature = os.path.join(work_geodatabase, 'sites_databases_AKALB')
absences_water = os.path.join(work_geodatabase, 'Absences_GlacierLake')
absences_picea = os.path.join(work_geodatabase, 'Absences_Picea')
absences_betula = os.path.join(work_geodatabase, 'Absences_BetulaTrees')

# Convert sites csv table to point feature class if it does not already exist
if arcpy.Exists(sites_feature) == 0:

    # Define input and output arrays for table conversion
    table_inputs = [study_area, sites_file]
    table_outputs = [sites_feature]

    # Create key word arguments
    table_kwargs = {'input_projection': 4269,
                    'output_projection': 3338,
                    'geographic_transformation': '',
                    'work_geodatabase': work_geodatabase,
                    'input_array': table_inputs,
                    'output_array': table_outputs
                    }

    # Convert table to points
    print(f'Converting table to projected points feature class for study area...')
    arcpy_geoprocessing(table_to_feature_projected, **table_kwargs)

else:
    print('Projected points feature class for study area already exists.')

# Generate random water absences feature class if it does not already exist
if arcpy.Exists(absences_water) == 0:

    # Define input and output arrays for water absences
    water_inputs = [lake_glacier, sites_feature]
    water_outputs = [absences_water]

    # Define a selection query for the water mask
    selection_query = 'Shape_Area > 500000'

    # Create key word arguments
    water_kwargs = {'number_points': 200,
                    'minimum_distance': '10 Kilometers',
                    'site_prefix': 'WATER',
                    'initial_project': 'Water Absences',
                    'selection_query': selection_query,
                    'work_geodatabase': work_geodatabase,
                    'input_array': water_inputs,
                    'output_array': water_outputs
                    }

    # Extract raster to study area
    print(f'Generating random absences for water mask...')
    arcpy_geoprocessing(generate_random_absences, **water_kwargs)
    print('----------')

# Generate random absences outside of the range of Picea glauca in the sub-Arctic map region
if arcpy.Exists(absences_picea) == 0:

    # Define input and output arrays for water absences
    picea_inputs = [subarctic_region, sites_feature, lake_glacier, spruce_range]
    picea_outputs = [absences_picea]

    # Define a selection query for the water mask
    selection_query = ''

    # Create key word arguments
    water_kwargs = {'number_points': 200,
                    'minimum_distance': '10 Kilometers',
                    'site_prefix': 'WATER',
                    'initial_project': 'Water Absences',
                    'selection_query': selection_query,
                    'work_geodatabase': work_geodatabase,
                    'input_array': water_inputs,
                    'output_array': water_outputs
                    }

    # Extract raster to study area
    print(f'Generating random absences for water mask...')
    arcpy_geoprocessing(generate_random_absences, **water_kwargs)
    print('----------')