# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create analysis grids
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in an ArcGIS Pro Python 3.11+ installation.
# Description: "Create analysis grids" creates major and minor grid indices and overlapping grid tiles from a manually-generated study area polygon.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_grid_tiles
from package_GeospatialProcessing import select_location
import os

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'N:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Set data folder
project_folder = os.path.join(root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')

# Define geodatabases
main_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')
regions_geodatabase = os.path.join(project_folder, 'AKVEG_Regions.gdb')
work_geodatabase = os.path.join(project_folder, 'AKVEG_Workspace.gdb')

# Define input raster datasets
akyuk_feature = os.path.join(regions_geodatabase, 'AlaskaYukon_MapDomain_3338')
akyuk_raster = os.path.join(project_folder, 'Data_Input/AlaskaYukon_MapDomain.tif')
nab_feature = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_ModelArea_3338')
tnp_feature = os.path.join(regions_geodatabase, 'TemperateNorthPacific_ModelArea_3338')

# Define output grid datasets
full_400 = os.path.join(work_geodatabase, 'Full_400_Tiles_3338')
full_100 = os.path.join(work_geodatabase, 'Full_100_Tiles_3338')
full_050 = os.path.join(work_geodatabase, 'Full_050_Tiles_3338')
full_010 = os.path.join(work_geodatabase, 'Full_010_Tiles_3338')
akyuk_400 = os.path.join(regions_geodatabase, 'AlaskaYukon_400_Tiles_3338')
akyuk_100 = os.path.join(regions_geodatabase, 'AlaskaYukon_100_Tiles_3338')
akyuk_050 = os.path.join(regions_geodatabase, 'AlaskaYukon_050_Tiles_3338')
akyuk_010 = os.path.join(regions_geodatabase, 'AlaskaYukon_010_Tiles_3338')
nab_400 = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_400_Tiles_3338')
nab_100 = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_100_Tiles_3338')
nab_050 = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_050_Tiles_3338')
nab_010 = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_010_Tiles_3338')
tnp_400 = os.path.join(regions_geodatabase, 'TemperateNorthPacific_400_Tiles_3338')
tnp_100 = os.path.join(regions_geodatabase, 'TemperateNorthPacific_100_Tiles_3338')
tnp_050 = os.path.join(regions_geodatabase, 'TemperateNorthPacific_050_Tiles_3338')
tnp_010 = os.path.join(regions_geodatabase, 'TemperateNorthPacific_010_Tiles_3338')

#### GENERATE 400 KM GRIDS
####____________________________________________________

# Create the 400 km grid tiles
full_400_kwargs = {'distance_km': 400,
                   'origin_coordinate': '-2199995 5',
                   'height': 2400,
                   'length': 4000,
                   'work_geodatabase': work_geodatabase,
                   'input_array': [akyuk_feature],
                   'output_array': [full_400]
                   }
if arcpy.Exists(full_400) == 0:
    print('Creating 400 km grid tiles...')
    arcpy_geoprocessing(create_grid_tiles, **full_400_kwargs)
    print('----------')
else:
    print('400 km tiles already exist.')
    print('----------')

# Select the 400 km tiles for Alaska-Yukon
akyuk_400_kwargs = {'work_geodatabase': work_geodatabase,
                    'input_array': [akyuk_feature, full_400],
                    'output_array': [akyuk_400]}
if arcpy.Exists(akyuk_400) == 0:
    print('Selecting 400 km grid tiles for Alaska-Yukon...')
    arcpy_geoprocessing(select_location, **akyuk_400_kwargs)
    print('----------')
else:
    print('400 km grid tiles for Alaska-Yukon already exist.')
    print('----------')

# Select the 400 km tiles for North American Beringia
nab_400_kwargs = {'work_geodatabase': work_geodatabase,
                  'input_array': [nab_feature, full_400],
                  'output_array': [nab_400]}
if arcpy.Exists(nab_400) == 0:
    print('Selecting 400 km grid tiles for North American Beringia...')
    arcpy_geoprocessing(select_location, **nab_400_kwargs)
    print('----------')
else:
    print('400 km grid tiles for North American Beringia already exist.')
    print('----------')

# Select the 400 km tiles for Temperate North Pacific
tnp_400_kwargs = {'work_geodatabase': work_geodatabase,
                  'input_array': [tnp_feature, full_400],
                  'output_array': [tnp_400]}
if arcpy.Exists(tnp_400) == 0:
    print('Selecting 400 km grid tiles for Temperate North Pacific...')
    arcpy_geoprocessing(select_location, **tnp_400_kwargs)
    print('----------')
else:
    print('400 km grid tiles for Temperate North Pacific already exist.')
    print('----------')

#### GENERATE 100 KM GRIDS
####____________________________________________________

# Create the 100 km grid tiles
full_100_kwargs = {'distance_km': 100,
                   'origin_coordinate': '-2199995 5',
                   'height': 2400,
                   'length': 4000,
                   'work_geodatabase': work_geodatabase,
                   'input_array': [akyuk_feature],
                   'output_array': [full_100]
                   }
if arcpy.Exists(full_100) == 0:
    print('Creating 100 km grid tiles...')
    arcpy_geoprocessing(create_grid_tiles, **full_100_kwargs)
    print('----------')
else:
    print('100 km tiles already exist.')
    print('----------')

# Select the 100 km tiles for Alaska-Yukon
akyuk_100_kwargs = {'work_geodatabase': work_geodatabase,
                    'input_array': [akyuk_feature, full_100],
                    'output_array': [akyuk_100]}
if arcpy.Exists(akyuk_100) == 0:
    print('Selecting 100 km grid tiles for Alaska-Yukon...')
    arcpy_geoprocessing(select_location, **akyuk_100_kwargs)
    print('----------')
else:
    print('100 km grid tiles for Alaska-Yukon already exist.')
    print('----------')

# Select the 100 km tiles for North American Beringia
nab_100_kwargs = {'work_geodatabase': work_geodatabase,
                  'input_array': [nab_feature, full_100],
                  'output_array': [nab_100]}
if arcpy.Exists(nab_100) == 0:
    print('Selecting 100 km grid tiles for North American Beringia...')
    arcpy_geoprocessing(select_location, **nab_100_kwargs)
    print('----------')
else:
    print('100 km grid tiles for North American Beringia already exist.')
    print('----------')

# Select the 100 km tiles for Temperate North Pacific
tnp_100_kwargs = {'work_geodatabase': work_geodatabase,
                  'input_array': [tnp_feature, full_100],
                  'output_array': [tnp_100]}
if arcpy.Exists(tnp_100) == 0:
    print('Selecting 100 km grid tiles for Temperate North Pacific...')
    arcpy_geoprocessing(select_location, **tnp_100_kwargs)
    print('----------')
else:
    print('100 km grid tiles for Temperate North Pacific already exist.')
    print('----------')

#### GENERATE 50 KM GRIDS
####____________________________________________________

# Create the 50 km grid tiles
full_050_kwargs = {'distance_km': 50,
                   'origin_coordinate': '-2199995 5',
                   'height': 2400,
                   'length': 4000,
                   'work_geodatabase': work_geodatabase,
                   'input_array': [akyuk_feature],
                   'output_array': [full_050]
                   }
if arcpy.Exists(full_050) == 0:
    print('Creating 50 km grid tiles...')
    arcpy_geoprocessing(create_grid_tiles, **full_050_kwargs)
    print('----------')
else:
    print('50 km tiles already exist.')
    print('----------')

# Select the 50 km tiles for Alaska-Yukon
akyuk_050_kwargs = {'work_geodatabase': work_geodatabase,
                    'input_array': [akyuk_feature, full_050],
                    'output_array': [akyuk_050]}
if arcpy.Exists(akyuk_050) == 0:
    print('Selecting 50 km grid tiles for Alaska-Yukon...')
    arcpy_geoprocessing(select_location, **akyuk_050_kwargs)
    print('----------')
else:
    print('50 km grid tiles for Alaska-Yukon already exist.')
    print('----------')

# Select the 50 km tiles for North American Beringia
nab_050_kwargs = {'work_geodatabase': work_geodatabase,
                  'input_array': [nab_feature, full_050],
                  'output_array': [nab_050]}
if arcpy.Exists(nab_050) == 0:
    print('Selecting 50 km grid tiles for North American Beringia...')
    arcpy_geoprocessing(select_location, **nab_050_kwargs)
    print('----------')
else:
    print('50 km grid tiles for North American Beringia already exist.')
    print('----------')

# Select the 50 km tiles for Temperate North Pacific
tnp_050_kwargs = {'work_geodatabase': work_geodatabase,
                  'input_array': [tnp_feature, full_050],
                  'output_array': [tnp_050]}
if arcpy.Exists(tnp_050) == 0:
    print('Selecting 50 km grid tiles for Temperate North Pacific...')
    arcpy_geoprocessing(select_location, **tnp_050_kwargs)
    print('----------')
else:
    print('50 km grid tiles for Temperate North Pacific already exist.')
    print('----------')

#### GENERATE 10 KM GRIDS
####____________________________________________________

# Create the 100 km grid tiles
full_010_kwargs = {'distance_km': 10,
                   'origin_coordinate': '-2199995 5',
                   'height': 2400,
                   'length': 4000,
                   'work_geodatabase': work_geodatabase,
                   'input_array': [akyuk_feature],
                   'output_array': [full_010]
                   }
if arcpy.Exists(full_010) == 0:
    print('Creating 10 km grid tiles...')
    arcpy_geoprocessing(create_grid_tiles, **full_010_kwargs)
    print('----------')
else:
    print('10 km tiles already exist.')
    print('----------')

# Select the 10 km tiles for Alaska-Yukon
akyuk_010_kwargs = {'work_geodatabase': work_geodatabase,
                    'input_array': [akyuk_feature, full_010],
                    'output_array': [akyuk_010]}
if arcpy.Exists(akyuk_010) == 0:
    print('Selecting 10 km grid tiles for Alaska-Yukon...')
    arcpy_geoprocessing(select_location, **akyuk_010_kwargs)
    print('----------')
else:
    print('10 km grid tiles for Alaska-Yukon already exist.')
    print('----------')

# Select the 10 km tiles for North American Beringia
nab_010_kwargs = {'work_geodatabase': work_geodatabase,
                  'input_array': [nab_feature, full_010],
                  'output_array': [nab_010]}
if arcpy.Exists(nab_010) == 0:
    print('Selecting 10 km grid tiles for North American Beringia...')
    arcpy_geoprocessing(select_location, **nab_010_kwargs)
    print('----------')
else:
    print('10 km grid tiles for North American Beringia already exist.')
    print('----------')

# Select the 10 km tiles for Temperate North Pacific
tnp_010_kwargs = {'work_geodatabase': work_geodatabase,
                  'input_array': [tnp_feature, full_010],
                  'output_array': [tnp_010]}
if arcpy.Exists(tnp_010) == 0:
    print('Selecting 10 km grid tiles for Temperate North Pacific...')
    arcpy_geoprocessing(select_location, **tnp_010_kwargs)
    print('----------')
else:
    print('10 km grid tiles for Temperate North Pacific already exist.')
    print('----------')
