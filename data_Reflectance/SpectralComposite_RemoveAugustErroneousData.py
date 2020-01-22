# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Remove August Erroneous Data
# Author: Timm Nawrocki
# Last Updated: 2020-01-18
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Remove August Erroneous Data" converts erroneous data in select August spectral tiles to no data to avoid contamination by sensor errors. Removed data is imputed from the mean of surrounding valid data in the "Create Spectral Composite" script.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import remove_erroneous_data

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/imagery/sentinel-2')
processed_folder = os.path.join(data_folder, 'processed')
corrected_folder = os.path.join(data_folder, 'corrected')

# Define input datasets
mask_raster = os.path.join(data_folder, 'mask/Mask_08August.tif')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Define working geodatabase
geodatabase = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')
# Set environment workspace
arcpy.env.workspace = geodatabase

# Set overwrite option
arcpy.env.overwriteOutput = True

month = 'Sent2_08August'
ranges_10 = ['0000098304-0000458752',
             '0000098304-0000425984',
             '0000098304-0000393216',
             '0000098304-0000360448',
             '0000065536-0000491520',
             '0000065536-0000458752',
             '0000065536-0000425984',
             '0000065536-0000393216',
             '0000032768-0000425984',
             '0000032768-0000393216']
ranges_20 = ['0000032768-0000229376',
             '0000032768-0000196608',
             '0000032768-0000163840',
             '0000000000-0000196608'
             ]
ranges_evi2 = ['0000116480-0000442624',
               '0000116480-0000419328',
               '0000116480-0000396032',
               '0000116480-0000372736',
               '0000116480-0000349440',
               '0000093184-0000442624',
               '0000093184-0000419328',
               '0000093184-0000396032',
               '0000093184-0000372736',
               '0000093184-0000349440',
               '0000069888-0000489216',
               '0000069888-0000465920',
               '0000069888-0000442624',
               '0000069888-0000419328',
               '0000069888-0000396032',
               '0000046592-0000465920',
               '0000046592-0000442624',
               '0000046592-0000419328'
               ]
properties_10 = ['2_blue',
                 '3_green',
                 '4_red',
                 '8_nearInfrared',
                 'ndvi',
                 'ndwi'
                 ]
properties_20 = ['5_redEdge1',
                 '6_redEdge2',
                 '7_redEdge3',
                 '8a_redEdge4',
                 '11_shortInfrared1',
                 '12_shortInfrared2',
                 'nbr',
                 'ndmi',
                 'ndsi',
                 ]

# Create a list of all month-property-range combinations
metrics_list = []
for range in ranges_10:
    for property in properties_10:
        month_range = os.path.join(processed_folder, month + '_' + property + '-' + range + '.tif')
        metrics_list.append(month_range)
for range in ranges_20:
    for property in properties_20:
        month_range = os.path.join(processed_folder, month + '_' + property + '-' + range + '.tif')
        metrics_list.append(month_range)
for range in ranges_evi2:
    month_range = os.path.join(processed_folder, month + '_' + 'evi2' + '-' + range + '.tif')
    metrics_list.append(month_range)
metrics_length = len(metrics_list)

# For each metric raster, remove the erroneous data
tile_count = 1
for input_raster in metrics_list:
    # Define output raster
    output_raster = os.path.join(corrected_folder, os.path.split(input_raster)[1])

    if arcpy.Exists(output_raster) == 0:
        # Define input and output arrays
        remove_errors_inputs = [snap_raster, mask_raster, input_raster]
        remove_errors_outputs = [output_raster]

        # Create key word arguments
        remove_errors_kwargs = {'input_array': remove_errors_inputs,
                                'output_array': remove_errors_outputs
                                }

        # Process the reproject integer function
        print(f'Removing erroneous data from tile {tile_count} of {metrics_length}...')
        arcpy_geoprocessing(remove_erroneous_data, **remove_errors_kwargs)
        print('----------')

    else:
        print(f'Tile {tile_count} of {metrics_length} already exists.')
        print('----------')

    tile_count += 1
