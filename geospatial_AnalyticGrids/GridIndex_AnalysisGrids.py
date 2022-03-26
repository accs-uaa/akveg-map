# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Analysis Grids
# Author: Timm Nawrocki
# Last Updated: 2021-11-20
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Analysis Grids" creates major and minor grid indices and overlapping grid tiles from a manually-generated study area polygon.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_buffered_tiles
from package_GeospatialProcessing import create_grid_index
from package_GeospatialProcessing import convert_validation_grid
from package_GeospatialProcessing import select_location
import os

# Set root directory
drive = 'N:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Set data folder
data_folder = os.path.join(root_folder, 'Data/analyses')
project_folder = os.path.join(root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')
regions_geodatabase = os.path.join(project_folder, 'Alaska_Regions.gdb')

# Define input raster datasets
total_feature = os.path.join(regions_geodatabase, 'AlaskaCombined_TotalArea')
total_raster = os.path.join(project_folder, 'Data_Input/AlaskaCombined_TotalArea.tif')
nab_feature = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_ModelArea')
nab_raster = os.path.join(project_folder, 'Data_Input/NorthAmericanBeringia_ModelArea.tif')

# Define output grid datasets
major_grid = os.path.join(regions_geodatabase, 'AlaskaCombined_GridIndex_Major_400km')
major_nab = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_GridIndex_Major_400km')
minor_grid = os.path.join(regions_geodatabase, 'AlaskaCombined_GridIndex_Minor_10km')
minor_nab = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_GridIndex_Minor_10km')
validation_grid = os.path.join(regions_geodatabase, 'AlaskaCombined_GridIndex_Validation_100km')
validation_nab = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_GridIndex_Validation_100km')
validation_raster = os.path.join(data_folder, 'validation/NorthAmericanBeringia_ValidationGroups.tif')

#### GENERATE MAJOR GRID INDEX

# Create key word arguments for the major grid index
major_kwargs = {'distance': '400 Kilometers',
                'grid_field': 'grid_major',
                'work_geodatabase': work_geodatabase,
                'input_array': [total_feature],
                'output_array': [major_grid]
                }
major_nab_kwargs = {'work_geodatabase': work_geodatabase,
                    'input_array': [nab_feature, major_grid],
                    'output_array': [major_nab]
                    }

# Create the major grid index
if arcpy.Exists(major_grid) == 0:
    print('Creating major grid index...')
    arcpy_geoprocessing(create_grid_index, **major_kwargs)
    print('----------')
else:
    print('Major grid index already exists.')
    print('----------')

# Subset major grids for North American Beringia
if arcpy.Exists(major_nab) == 0:
    print('Subsetting major grids for North American Beringia...')
    arcpy_geoprocessing(select_location, **major_nab_kwargs)
    print('----------')
else:
    print('Major grids for North American Beringia already exist.')
    print('----------')

#### GENERATE MINOR GRID INDEX

# Create key word arguments for the minor grid index
minor_kwargs = {'distance': '10 Kilometers',
                'grid_field': 'grid_minor',
                'work_geodatabase': work_geodatabase,
                'input_array': [major_grid, major_grid],
                'output_array': [minor_grid]
                }
minor_nab_kwargs = {'work_geodatabase': work_geodatabase,
                    'input_array': [nab_feature, minor_grid],
                    'output_array': [minor_nab]
                    }

# Create the minor grid index
if arcpy.Exists(minor_grid) == 0:
    print('Creating minor grid index...')
    arcpy_geoprocessing(create_grid_index, **minor_kwargs)
    print('----------')
else:
    print('Minor grid index already exists.')
    print('----------')

# Subset minor grids for North American Beringia
if arcpy.Exists(minor_nab) == 0:
    print('Subsetting minor grids for North American Beringia...')
    arcpy_geoprocessing(select_location, **minor_nab_kwargs)
    print('----------')
else:
    print('Minor grids for North American Beringia already exist.')
    print('----------')

#### GENERATE VALIDATION GRID INDEX

# Create key word arguments for the validation grid index
validation_kwargs = {'distance': '100 Kilometers',
                     'grid_field': 'grid_validation',
                     'work_geodatabase': work_geodatabase,
                     'input_array': [major_grid, major_grid],
                     'output_array': [validation_grid]
                     }
validation_nab_kwargs = {'work_geodatabase': work_geodatabase,
                         'input_array': [nab_feature, validation_grid],
                         'output_array': [validation_nab]
                         }

# Create the validation grid index
if arcpy.Exists(validation_grid) == 0:
    print('Creating validation grid index...')
    arcpy_geoprocessing(create_grid_index, **validation_kwargs)
    print('----------')
else:
    print('Validation grid index already exists.')
    print('----------')

# Subset validation grids for North American Beringia
if arcpy.Exists(validation_nab) == 0:
    print('Subsetting validation grids for North American Beringia...')
    arcpy_geoprocessing(select_location, **validation_nab_kwargs)
    print('----------')
else:
    print('Validation grids for North American Beringia already exist.')
    print('----------')

#### CONVERT VALIDATION GRIDS TO RASTERS

# Create key word arguments for validation raster
raster_nab_kwargs = {'work_geodatabase': work_geodatabase,
                     'input_array': [validation_grid, nab_feature, nab_raster],
                     'output_array': [validation_raster]
                     }

# Generate validation group raster for North American Beringia
if arcpy.Exists(validation_raster) == 0:
    print('Converting validation grids to raster for North American Beringia...')
    arcpy_geoprocessing(convert_validation_grid, **raster_nab_kwargs)
    print('----------')
else:
    print('Validation raster already exists.')
    print('----------')

#### CREATE GRID BLOCKS FOR MAJOR GRIDS

block_kwargs = {'tile_name': 'grid_major',
                'distance': '5000 Meters',
                'work_geodatabase': work_geodatabase,
                'input_array': [major_nab, total_raster],
                'output_folder': os.path.join(data_folder, 'grid_major/full')
                }

# Create buffered tiles for the major grid
arcpy_geoprocessing(create_buffered_tiles, check_output=False, **block_kwargs)
print('----------')

#### CREATE GRID BLOCKS FOR MAJOR GRIDS IN NORTH AMERICAN BERINGIA

block_nab_kwargs = {'tile_name': 'grid_major',
                    'distance': '5000 Meters',
                    'work_geodatabase': work_geodatabase,
                    'input_array': [major_nab, nab_raster],
                    'output_folder': os.path.join(data_folder, 'grid_major/nab')
                    }

# Create buffered tiles for the major grid
arcpy_geoprocessing(create_buffered_tiles, check_output=False, **block_nab_kwargs)
print('----------')

#### CREATE GRID TILES FOR MINOR GRIDS IN NORTH AMERICAN BERINGIA

tile_nab_kwargs = {'tile_name': 'grid_minor',
                   'distance': '10 Meters',
                   'work_geodatabase': work_geodatabase,
                   'input_array': [minor_nab, nab_raster],
                   'output_folder': os.path.join(data_folder, 'grid_minor/nab')
                   }

# Create buffered tiles for the minor grid
arcpy_geoprocessing(create_buffered_tiles, check_output=False, **tile_nab_kwargs)
print('----------')
