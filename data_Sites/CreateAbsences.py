# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Absences
# Author: Timm Nawrocki
# Last Updated: 2021-03-12
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Absences" generates random absence points for glaciers and lakes, Picea species, and Betula trees.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import generate_random_absences
from package_GeospatialProcessing import table_to_feature_projected

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data')

# Define work geodatabase
work_geodatabase = os.path.join(data_folder, 'BeringiaVegetation.gdb')

# Define input datasets
study_area = os.path.join(work_geodatabase, 'NorthAmericanBeringia_ModelArea')
glaciers = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Glaciers')
lakes = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Lakes')
subarctic_region = os.path.join(work_geodatabase, 'mapRegion_Subarctic')
spruce_range = os.path.join(work_geodatabase, 'Range_PiceaGlauca')
betula_range = os.path.join(work_geodatabase, 'Range_BetulaTrees')
sites_file = os.path.join(data_folder, 'Data_Input/sites/sites_all.csv')

# Define output datasets
sites_feature = os.path.join(work_geodatabase, 'Sites_Databases_AKALB')
absences_glacier = os.path.join(work_geodatabase, 'Absences_Glacier')
absences_lake = os.path.join(work_geodatabase, 'Absences_Lake')
absences_picea = os.path.join(work_geodatabase, 'Absences_Picea')
absences_betula = os.path.join(work_geodatabase, 'Absences_BetulaTrees')

# Define a selection query
selection_query = 'Shape_Area > 100000'

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
    print('\t----------')

else:
    print('Projected points feature class for study area already exists.')
    print('\t----------')

# Generate random glacier absences feature class if it does not already exist
if arcpy.Exists(absences_glacier) == 0:
    # Define input and output arrays for water absences
    glacier_inputs = [glaciers]
    glacier_outputs = [absences_glacier]

    # Create key word arguments
    glacier_kwargs = {'number_points': 100,
                      'minimum_distance': '5 Kilometers',
                      'site_prefix': 'GLACIER',
                      'initial_project': 'Glacier Absences',
                      'selection_query': selection_query,
                      'work_geodatabase': work_geodatabase,
                      'input_array': glacier_inputs,
                      'output_array': glacier_outputs
                      }

    # Generate random glacier absences
    print(f'Generating random absences for glacier mask...')
    arcpy_geoprocessing(generate_random_absences, **glacier_kwargs)
    print('----------')

else:
    print('Random points for glacier mask already exists.')
    print('----------')

# Generate random lake absences feature class if it does not already exist
if arcpy.Exists(absences_lake) == 0:
    # Define input and output arrays for water absences
    lake_inputs = [lakes]
    lake_outputs = [absences_lake]

    # Create key word arguments
    lake_kwargs = {'number_points': 170,
                   'minimum_distance': '5 Kilometers',
                   'site_prefix': 'LAKES',
                   'initial_project': 'Lake Absences',
                   'selection_query': selection_query,
                   'work_geodatabase': work_geodatabase,
                   'input_array': lake_inputs,
                   'output_array': lake_outputs
                   }

    # Generate random lake absences
    print(f'Generating random absences for lakes mask...')
    arcpy_geoprocessing(generate_random_absences, **lake_kwargs)
    print('----------')

else:
    print('Random points for lake mask already exists.')
    print('----------')

# Generate random absences outside of the range of Picea in the sub-Arctic map region
if arcpy.Exists(absences_picea) == 0:
    # Define input and output arrays for Picea absences
    picea_inputs = [subarctic_region, sites_feature, lakes, glaciers, spruce_range]
    picea_outputs = [absences_picea]

    # Create key word arguments
    picea_kwargs = {'number_points': 150,
                    'minimum_distance': '10 Kilometers',
                    'site_prefix': 'PICEA',
                    'initial_project': 'Picea Absences',
                    'selection_query': '',
                    'work_geodatabase': work_geodatabase,
                    'input_array': picea_inputs,
                    'output_array': picea_outputs
                    }

    # Generate Picea absences
    print(f'Generating random absences for Picea mask...')
    arcpy_geoprocessing(generate_random_absences, **picea_kwargs)
    print('----------')

else:
    print('Random points for Picea mask already exists.')
    print('----------')

# Generate random absences outside of the range of Betula trees in the sub-Arctic map region
if arcpy.Exists(absences_betula) == 0:
    # Define input and output arrays for Betula tree absences
    betula_inputs = [subarctic_region, sites_feature, lakes, glaciers, betula_range]
    betula_outputs = [absences_betula]

    # Create key word arguments
    betula_kwargs = {'number_points': 250,
                     'minimum_distance': '10 Kilometers',
                     'site_prefix': 'BETTRE',
                     'initial_project': 'Betula Tree Absences',
                     'selection_query': '',
                     'work_geodatabase': work_geodatabase,
                     'input_array': betula_inputs,
                     'output_array': betula_outputs
                     }

    # Generate Betula tree absences
    print(f'Generating random absences for Betula tree mask...')
    arcpy_geoprocessing(generate_random_absences, **betula_kwargs)
    print('----------')

else:
    print('Random points for Betula tree mask already exists.')
    print('----------')
