# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Remove Erroneous Data
# Author: Timm Nawrocki
# Last Updated: 2020-01-18
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Remove Erroneous Data" is a function that removes erroneous data identified by a mask raster from a spectral tile.
# ---------------------------------------------------------------------------

# Define a function to remove erroneous data from a spectral tile
def remove_erroneous_data(**kwargs):
    """
    Description: replaces erroneous data in a spectral tile with NoData based on a mask raster with values of 1 set to NoData in the spectral tile
    Inputs: 'input_array' -- an array containing the snap raster (must be first), the mask raster (must be second), and input spectral tile that must have erroneous data removed
            'output_array' -- an array containing the output spectral tile
    Returned Value: Returns a raster dataset on disk containing the a mask raster with values of 1 or NoData
    Preconditions: requires processed source spectral tiles and snap raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import IsNull
    from arcpy.sa import SetNull
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "66%"

    # Parse key word argument inputs
    snap_raster = kwargs['input_array'][0]
    mask_raster = kwargs['input_array'][1]
    tile_input = kwargs['input_array'][2]
    tile_output = kwargs['output_array'][0]

    # Set snap raster
    arcpy.env.snapRaster = snap_raster

    # Set extent
    arcpy.env.extent = tile_input

    # Define intermediate dataset
    tile_intermediate = os.path.splitext(tile_input)[0] + "_intermediate.tif"

    # Replace values with NoData where mask raster has a value of 1
    print('\tRemoving erroneous values from spectral tile...')
    iteration_start = time.time()
    raster_con = Con(mask_raster, -32767, tile_input, 'VALUE = 1')
    raster_corrected = SetNull(raster_con, raster_con, 'VALUE = -32767')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export corrected raster
    print(f'\tSaving corrected raster...')
    iteration_start = time.time()
    arcpy.CopyRaster_management(raster_corrected,
                                tile_output,
                                '',
                                '',
                                '-32768',
                                'NONE',
                                'NONE',
                                '16_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE')
    #if arcpy.Exists(tile_intermediate) == 1:
        #arcpy.Delete_management(tile_intermediate)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully removed erroneous data for {os.path.split(tile_input)[1]}.'
    return out_process