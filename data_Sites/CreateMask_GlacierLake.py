# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Mask for Glaciers and Lakes
# Author: Timm Nawrocki
# Last Updated: 2021-03-09
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Mask for Glaciers and Lakes" selects lakes from the NHD Waterbodies and merges them with glaciers.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import merge_glaciers_lakes

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

# Define output dataset
lake_glacier = os.path.join(work_geodatabase, 'NorthAmericanBeringia_LakeGlacier')

# Define input and output arrays
mask_inputs = [study_area, waterbodies, glaciers]
mask_outputs = [lake_glacier]

# Create key word arguments
merge_kwargs = {'work_geodatabase': work_geodatabase,
                'input_array': mask_inputs,
                'output_array': mask_outputs
                }

# Extract raster to study area
print(f'Merging lakes and glaciers to form mask dataset...')
arcpy_geoprocessing(merge_glaciers_lakes, **merge_kwargs)
print('----------')
