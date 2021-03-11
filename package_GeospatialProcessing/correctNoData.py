# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Correct No Data
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Correct No Data" is a function that replaces raster values with No Data.
# ---------------------------------------------------------------------------

# Define function to correct raster values to No Data
def correct_no_data(**kwargs):
    """
    Description: correct values to No Data
    Inputs: 'value_threshold' -- a value that marks the start of No Data
            'direction' -- inequality direction must be either 'above' or 'below'
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the snap raster and input raster
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster dataset on disk containing the corrected raster
    Preconditions: requires predefined snap raster and input raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    import datetime
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    value_threshold = kwargs['value_threshold']
    direction = kwargs['direction']
    snap_raster = kwargs['input_array'][0]
    input_raster = kwargs['input_array'][1]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = snap_raster

    # Determine input raster value type
    value_number = arcpy.management.GetRasterProperties(input_raster, "VALUETYPE")[0]
    no_data_value = arcpy.Describe(input_raster).noDataValue
    value_dictionary = {
        0: '1_BIT',
        1: '2_BIT',
        2: '4_BIT',
        3: '8_BIT_UNSIGNED',
        4: '8_BIT_SIGNED',
        5: '16_BIT_UNSIGNED',
        6: '16_BIT_SIGNED',
        7: '32_BIT_UNSIGNED',
        8: '32_BIT_SIGNED',
        9: '32_BIT_FLOAT',
        10: '64_BIT'
    }
    value_type = value_dictionary.get(int(value_number))
    print(f'Output data type will be {value_type}.')
    print(f'Output no data value will be {no_data_value}.')

    # Correct and export raster values by threshold and direction
    print('Correcting No Data in raster...')
    iteration_start = time.time()
    # Set values to null based on threshold
    if direction == 'above':
        corrected_raster = SetNull(Raster(input_raster), Raster(input_raster), f'VALUE > {value_threshold}')
    elif direction == 'below':
        corrected_raster = SetNull(Raster(input_raster), Raster(input_raster), f'VALUE < {value_threshold}')
    else:
        print('Incorrect direction entered.')
        quit()
    # Export corrected raster
    print(f'Exporting corrected raster to output raster...')
    arcpy.CopyRaster_management(corrected_raster,
                                output_raster,
                                '',
                                '',
                                no_data_value,
                                'NONE',
                                'NONE',
                                value_type,
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished correcting no data values.'
    return out_process
