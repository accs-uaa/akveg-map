# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Mask Raster
# Author: Timm Nawrocki
# Last Updated: 2020-01-18
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Mask Raster" is a function that creates a mask from a set of spectral tiles and a user-defined threshold value.
# ---------------------------------------------------------------------------

# Define a function to create a mask raster from a set of spectral tiles
def create_mask_raster(**kwargs):
    """
    Description: extracts spectral tiles to an area and mosaics extracted tiles with first data priority
    Inputs: 'threshold' -- an integer value that will define the mask (all values less than or equal to threshold will become the mask value of 1)
            'input_array' -- an array containing the snap raster (must be first), a feature class that sets the processing extent (must be second), and the list of spectral tiles from which to create the mask
            'output_array' -- an array containing the output mask raster
    Returned Value: Returns a raster dataset on disk containing the a mask raster with values of 1 or NoData
    Preconditions: requires processed source spectral tiles and snap raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import Expand
    from arcpy.sa import IsNull
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "66%"

    # Parse key word argument inputs
    threshold = kwargs['threshold']
    tile_inputs = kwargs['input_array'][2:]
    snap_raster = kwargs['input_array'][0]
    extent_feature = kwargs['input_array'][1]
    mask_raster = kwargs['output_array'][0]

    # Set snap raster and extent
    arcpy.env.snapRaster = snap_raster
    arcpy.env.extent = extent_feature

    # Define mosaic raster
    mosaic_raster = os.path.splitext(mask_raster)[0] + '_mosaic.tif'
    mosaic_location, mosaic_name = os.path.split(mosaic_raster)

    # Define composite projection and cell size
    composite_projection = arcpy.Describe(tile_inputs[0]).spatialReference
    cell_size = arcpy.GetRasterProperties_management(tile_inputs[0], 'CELLSIZEX')

    # Mosaic raster tiles to new raster
    print(f'\tMosaicking the input spectral tiles...')
    iteration_start = time.time()
    arcpy.MosaicToNewRaster_management(tile_inputs,
                                       mosaic_location,
                                       mosaic_name,
                                       composite_projection,
                                       '16_BIT_SIGNED',
                                       cell_size,
                                       '1',
                                       'FIRST',
                                       'FIRST')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate a 1 or NoData mask raster
    print('\tSetting null values in mask...')
    iteration_start = time.time()
    raster_nullRemove = Con(IsNull(mosaic_raster), threshold + 1, mosaic_raster, 'VALUE = 1')
    raster_con = Con(raster_nullRemove, 1, -32767, f'VALUE <= {str(threshold)}')
    raster_expand = Expand(raster_con, 2, 1, 'MORPHOLOGICAL')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export mask raster
    print(f'\tSaving mask raster...')
    iteration_start = time.time()
    arcpy.CopyRaster_management(raster_expand,
                                mask_raster,
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
    # Delete mosaic raster
    if arcpy.Exists(mosaic_raster) == 1:
        arcpy.Delete_management(mosaic_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully created mask raster.'
    return out_process