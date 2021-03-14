# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse Sites to Grids
# Author: Timm Nawrocki
# Last Updated: 2021-03-12
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

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data')

# Create parsed folder within data folder if it does not already exist
parsed_folder = os.path.join(data_folder, 'Data_Input/sites/parsed')
if os.path.exists(parsed_folder) == 0:
    os.mkdir(parsed_folder)

# Define work environment
work_geodatabase = os.path.join(drive, root_folder,
                                'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/BeringiaVegetation.gdb')

# Define input datasets
sites_file = os.path.join(data_folder, 'Data_Input/sites/sites_all.csv')
absences_glacier = os.path.join(work_geodatabase, 'Absences_Glacier')
absences_lake = os.path.join(work_geodatabase, 'Absences_Lake')
absences_picea = os.path.join(work_geodatabase, 'Absences_Picea')
absences_betula = os.path.join(work_geodatabase, 'Absences_BetulaTrees')
study_area = os.path.join(work_geodatabase, 'NorthAmericanBeringia_ModelArea')
grid_major = os.path.join(work_geodatabase, 'NorthAmericanBeringia_GridIndex_Major_400km_Selected')
area_of_interest = os.path.join(data_folder, 'Data_Input/northAmericanBeringia_ModelArea.tif')

# Define output point feature class
sites_feature = os.path.join(work_geodatabase, 'Sites_Databases_AKALB')
merged_feature = os.path.join(work_geodatabase, 'Sites_Merged_AKALB')
merged_file = os.path.join(data_folder, 'Data_Input/sites/sites_merged.csv')
sites_formatted = os.path.join(work_geodatabase, 'Sites_Formatted_AKALB')

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

    # Define input and output arrays for site merge
    merge_inputs = [sites_feature, absences_glacier, absences_lake, absences_picea, absences_betula]
    merge_outputs = [merged_feature, merged_file]

    # Create key word arguments
    merge_kwargs = {'output_fields': output_fields,
                    'work_geodatabase': work_geodatabase,
                    'input_array': merge_inputs,
                    'output_array': merge_outputs
                    }

    # Merge site and synthetic absence points
    print(f'Merging site points with synthetic absence points...')
    arcpy_geoprocessing(merge_sites, **merge_kwargs)
    print('----------')

else:
    print('Merged sites feature class already exists.')
    print('----------')

# Format site data if it does not already exist
if arcpy.Exists(sites_formatted) == 0:
    # Define input and output arrays to format site data
    format_inputs = [merged_feature, area_of_interest]
    format_outputs = [sites_formatted]

    # Create key word arguments
    format_kwargs = {'work_geodatabase': work_geodatabase,
                     'input_array': format_inputs,
                     'output_array': format_outputs
                     }

    # Format site data
    print(f'Formatting site data...')
    arcpy_geoprocessing(format_site_data, **format_kwargs)
    print('----------')

else:
    print('Formatted data already exists.')
    print('----------')

# Parse site data to grids with a search cursor
parsed_inputs = [sites_formatted, grid_major]
with arcpy.da.SearchCursor(grid_major, ['Major']) as cursor:
    # Iterate through each grid in major grid
    for row in cursor:
        # Identify grid name
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
