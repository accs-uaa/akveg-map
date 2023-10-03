# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Absences
# Author: Timm Nawrocki
# Last Updated: 2021-11-20
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
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')
regions_geodatabase = os.path.join(project_folder, 'Alaska_Regions.gdb')
occurrence_geodatabase = os.path.join(project_folder, 'Occurrences.gdb')
range_geodatabase = os.path.join(project_folder, 'Ranges.gdb')

# Define input datasets
nab_feature = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_ModelArea')
glaciers = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Glaciers')
lakes = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Lakes')
western_feature = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_Subregion_Western')
spruce_range = os.path.join(range_geodatabase, 'Range_PiceaGlauca')
betula_range = os.path.join(range_geodatabase, 'Range_BetulaTrees')
sites_file = os.path.join(project_folder, 'Data_Input/sites/sites_all.csv')

# Define output datasets
sites_feature = os.path.join(work_geodatabase, 'Sites_Databases_AKALB')
absences_glacier = os.path.join(occurrence_geodatabase, 'Absences_Glacier')
absences_lake = os.path.join(occurrence_geodatabase, 'Absences_Lake')
absences_picea = os.path.join(occurrence_geodatabase, 'Absences_Picea')
absences_betula = os.path.join(occurrence_geodatabase, 'Absences_BetulaTrees')

# Define a selection query
selection_query = 'Shape_Area > 100000'

# Convert sites csv table to point feature class if it does not already exist
if arcpy.Exists(sites_feature) == 0:

    # Create key word arguments
    kwargs_table = {'input_projection': 4269,
                    'output_projection': 3338,
                    'geographic_transformation': '',
                    'work_geodatabase': work_geodatabase,
                    'input_array': [nab_feature, sites_file],
                    'output_array': [sites_feature]
                    }

    # Convert table to points
    print(f'Converting table to projected points feature class for study area...')
    arcpy_geoprocessing(table_to_feature_projected, **kwargs_table)
    print('----------')

else:
    print('Projected points feature class for study area already exists.')
    print('----------')

# Generate random glacier absences feature class if it does not already exist
if arcpy.Exists(absences_glacier) == 0:

    # Create key word arguments
    kwargs_glacier = {'number_points': 100,
                      'minimum_distance': '5 Kilometers',
                      'site_prefix': 'GLACIER',
                      'initial_project': 'Glacier Absences',
                      'selection_query': selection_query,
                      'work_geodatabase': work_geodatabase,
                      'input_array': [glaciers],
                      'output_array': [absences_glacier]
                      }

    # Generate random glacier absences
    print(f'Generating random absences for glacier mask...')
    arcpy_geoprocessing(generate_random_absences, **kwargs_glacier)
    print('----------')

else:
    print('Random points for glacier mask already exists.')
    print('----------')

# Generate random lake absences feature class if it does not already exist
if arcpy.Exists(absences_lake) == 0:

    # Create key word arguments
    kwargs_lake = {'number_points': 170,
                   'minimum_distance': '2 Kilometers',
                   'site_prefix': 'LAKES',
                   'initial_project': 'Lake Absences',
                   'selection_query': selection_query,
                   'work_geodatabase': work_geodatabase,
                   'input_array': [lakes],
                   'output_array': [absences_lake]
                   }

    # Generate random lake absences
    print(f'Generating random absences for lakes mask...')
    arcpy_geoprocessing(generate_random_absences, **kwargs_lake)
    print('----------')

else:
    print('Random points for lake mask already exists.')
    print('----------')

# Generate random absences outside of the range of Picea in the sub-Arctic map region
if arcpy.Exists(absences_picea) == 0:

    # Create key word arguments
    kwargs_picea = {'number_points': 150,
                    'minimum_distance': '5 Kilometers',
                    'site_prefix': 'PICEA',
                    'initial_project': 'Picea Absences',
                    'selection_query': '',
                    'work_geodatabase': work_geodatabase,
                    'input_array': [western_feature, sites_feature, lakes, glaciers, spruce_range],
                    'output_array': [absences_picea]
                    }

    # Generate Picea absences
    print(f'Generating random absences for Picea mask...')
    arcpy_geoprocessing(generate_random_absences, **kwargs_picea)
    print('----------')

else:
    print('Random points for Picea mask already exists.')
    print('----------')

# Generate random absences outside of the range of Betula trees in the sub-Arctic map region
if arcpy.Exists(absences_betula) == 0:

    # Create key word arguments
    kwargs_betula = {'number_points': 250,
                     'minimum_distance': '5 Kilometers',
                     'site_prefix': 'BETTRE',
                     'initial_project': 'Betula Tree Absences',
                     'selection_query': '',
                     'work_geodatabase': work_geodatabase,
                     'input_array': [western_feature, sites_feature, lakes, glaciers, betula_range],
                     'output_array': [absences_betula]
                     }

    # Generate Betula tree absences
    print(f'Generating random absences for Betula tree mask...')
    arcpy_geoprocessing(generate_random_absences, **kwargs_betula)
    print('----------')

else:
    print('Random points for Betula tree mask already exists.')
    print('----------')
