# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Masks for Glaciers and Lakes
# Author: Timm Nawrocki
# Last Updated: 2021-03-12
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

# Define work geodatabase
work_geodatabase = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/BeringiaVegetation.gdb')

# Define input datasets
glaciers = os.path.join(data_folder, 'geoscientific/GlobalLandIceMeasurements.shp')
waterbodies = os.path.join(data_folder, 'inlandwaters/NHD_H_02_GDB.gdb/Hydrography/NHDWaterbody')
study_area = os.path.join(work_geodatabase, 'NorthAmericanBeringia_ModelArea')

# Define output datasets
glacier_mask = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Glaciers')
lake_mask = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Lakes')

# Define input and output arrays for glaciers
glacier_inputs = [study_area, glaciers]
glacier_outputs = [glacier_mask]

# Create key word arguments
glacier_kwargs = {'input_projection': 4326,
                  'output_projection': 3338,
                  'geographic_transformation': 'WGS_1984_(ITRF00)_To_NAD_1983',
                  'selection_query': '',
                  'work_geodatabase': work_geodatabase,
                  'input_array': glacier_inputs,
                  'output_array': glacier_outputs
                  }

# Create glacier mask
print(f'Creating glacier mask...')
arcpy_geoprocessing(create_mask, **glacier_kwargs)
print('----------')

# Define input and output arrays for lakes
lake_inputs = [study_area, waterbodies]
lake_outputs = [lake_mask]

# Define selection query
selection_query = 'FType = 390'

# Create key word arguments
lake_kwargs = {'input_projection': 4269,
               'output_projection': 3338,
               'geographic_transformation': '',
               'selection_query': selection_query,
               'work_geodatabase': work_geodatabase,
               'input_array': lake_inputs,
               'output_array': lake_outputs
               }

# Create lake mask
print(f'Creating lake mask...')
arcpy_geoprocessing(create_mask, **lake_kwargs)
print('----------')
