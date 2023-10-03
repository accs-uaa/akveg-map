# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Masks for Glaciers and Lakes
# Author: Timm Nawrocki
# Last Updated: 2021-11-20
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Masks for Glaciers and Lakes" selects lakes from the NHD Waterbodies and clips lakes and glaciers to the study area.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_mask

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')

# Define input datasets
glaciers = os.path.join(data_folder, 'geoscientific/GlobalLandIceMeasurements.shp')
waterbodies = os.path.join(data_folder, 'inlandwaters/NHD_H_02_GDB.gdb/Hydrography/NHDWaterbody')
nab_feature = os.path.join(work_geodatabase, 'NorthAmericanBeringia_ModelArea')

# Define output datasets
glacier_mask = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Glaciers')
lake_mask = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Lakes')

# Create key word arguments
kwargs_glacier = {'input_projection': 4326,
                  'output_projection': 3338,
                  'geographic_transformation': 'WGS_1984_(ITRF00)_To_NAD_1983',
                  'selection_query': '',
                  'work_geodatabase': work_geodatabase,
                  'input_array': [nab_feature, glaciers],
                  'output_array': [glacier_mask]
                  }

# Create glacier mask
print(f'Creating glacier mask...')
arcpy_geoprocessing(create_mask, **kwargs_glacier)
print('----------')

# Define selection query
selection_query = 'FType = 390'

# Create key word arguments
kwargs_lake = {'input_projection': 4269,
               'output_projection': 3338,
               'geographic_transformation': '',
               'selection_query': selection_query,
               'work_geodatabase': work_geodatabase,
               'input_array': [nab_feature, waterbodies],
               'output_array': [lake_mask]
               }

# Create lake mask
print(f'Creating lake mask...')
arcpy_geoprocessing(create_mask, **kwargs_lake)
print('----------')
