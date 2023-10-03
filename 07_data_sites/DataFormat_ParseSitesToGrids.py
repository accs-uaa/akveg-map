# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse Sites to Grids
# Author: Timm Nawrocki
# Last Updated: 2021-11-20
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Parse Sites to Grids" prepares a table of point data for feature extraction by selecting appropriate raster cells based on cell size and splits raster points by major grids.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import format_site_data
from package_GeospatialProcessing import merge_sites
from package_GeospatialProcessing import parse_site_data
from package_GeospatialProcessing import table_to_feature_projected

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
sites_folder = os.path.join(project_folder, 'Data_Input/sites')
parsed_folder = os.path.join(project_folder, 'Data_Input/sites/parsed')
if os.path.exists(parsed_folder) == 0:
    os.mkdir(parsed_folder)

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')
regions_geodatabase = os.path.join(project_folder, 'Alaska_Regions.gdb')
occurrence_geodatabase = os.path.join(project_folder, 'Occurrences.gdb')

# Define input datasets
nab_raster = os.path.join(project_folder, 'Data_Input/NorthAmericanBeringia_ModelArea.tif')
nab_feature = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_ModelArea')
nab_gridmajor = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_GridIndex_Major_400km')
sites_file = os.path.join(sites_folder, 'sites_all.csv')
absences_glacier = os.path.join(occurrence_geodatabase, 'Absences_Glacier')
absences_lake = os.path.join(occurrence_geodatabase, 'Absences_Lake')
absences_picea = os.path.join(occurrence_geodatabase, 'Absences_Picea')
absences_betula = os.path.join(occurrence_geodatabase, 'Absences_BetulaTrees')

# Define output point feature class
sites_feature = os.path.join(work_geodatabase, 'Sites_Databases_AKALB')
merged_feature = os.path.join(work_geodatabase, 'Sites_Merged_AKALB')
merged_file = os.path.join(project_folder, 'Data_Input/sites/sites_merged.csv')
sites_formatted = os.path.join(work_geodatabase, 'Sites_Formatted_AKALB')

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

# Merge site data with synthetic absences if merged data does not already exist
if arcpy.Exists(merged_feature) == 0:

    # Define output fields
    output_fields = ['site_code',
                     'initial_project',
                     'perspective',
                     'cover_method',
                     'scope_vascular',
                     'scope_bryophyte',
                     'scope_lichen',
                     'plot_dimensions',
                     'POINT_X',
                     'POINT_Y']

    # Create key word arguments
    kwargs_merge = {'output_fields': output_fields,
                    'work_geodatabase': work_geodatabase,
                    'input_array': [sites_feature, absences_glacier, absences_lake, absences_picea, absences_betula],
                    'output_array': [merged_feature, merged_file]
                    }

    # Merge site and synthetic absence points
    print(f'Merging site points with synthetic absence points...')
    arcpy_geoprocessing(merge_sites, **kwargs_merge)
    print('----------')

else:
    print('Merged sites feature class already exists.')
    print('----------')

# Format site data if it does not already exist
if arcpy.Exists(sites_formatted) == 0:

    # Create key word arguments
    kwargs_format = {'work_geodatabase': work_geodatabase,
                     'input_array': [merged_feature, nab_raster],
                     'output_array': [sites_formatted]
                     }

    # Format site data
    print(f'Formatting site data...')
    arcpy_geoprocessing(format_site_data, **kwargs_format)
    print('----------')

else:
    print('Formatted data already exists.')
    print('----------')

# Parse site data to grids with a search cursor
with arcpy.da.SearchCursor(nab_gridmajor, ['grid_major']) as cursor:
    # Iterate through each grid in major grid
    for row in cursor:
        # Identify grid name
        grid_name = row[0]

        # Create key word arguments
        kwargs_parsed = {'work_geodatabase': work_geodatabase,
                         'grid_name': grid_name,
                         'input_array': [sites_formatted, nab_gridmajor],
                         'output_array': [os.path.join(parsed_folder, grid_name + '.shp')]
                         }

        # Parse site data
        print(f'Parsing site data for grid {grid_name}...')
        arcpy_geoprocessing(parse_site_data, **kwargs_parsed)
        print('----------')
