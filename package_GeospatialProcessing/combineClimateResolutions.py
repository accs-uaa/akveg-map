# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Combine Climate Resolutions
# Author: Timm Nawrocki
# Last Updated: 2020-05-28
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Combine Climate Resolutions" is a function that combines two resolutions of climate data for the same property into a single representation with the minimum cell size of the inputs.
# ---------------------------------------------------------------------------

# Define a function to combine multiple resolutions of climate data
def combine_climate_resolutions(**kwargs):
    """
    Description: calculates mean annual climate properties from a set of month-year climate rasters
    Inputs: 'input_array' -- an array containing the two scales of climate data to combine with the smaller resolution first
            'output_array' -- an array containing the output mean annual climate raster
    Returned Value: Returns a raster dataset on disk containing the combined climate property
    Preconditions: requires input climate means that must be calculated from the calculate climate mean function
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import IsNull
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    import datetime
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Parse key word argument inputs
    input_rasters = kwargs['input_array']
    output_raster = kwargs['output_array'][0]

    # Set snap raster and extent
    arcpy.env.snapRaster = input_rasters[0]
    arcpy.env.cellSize = 'MINOF'

    # Combine values of second raster where first raster is null
    iteration_start = time.time()
    print(f'\tCombining climate resolutions...')
    combined_climate = Con(IsNull(Raster(input_rasters[0])), Raster(input_rasters[1]), Raster(input_rasters[0]))
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Expand the raster into the NoData region
    iteration_start = time.time()
    print(f'\tExpanding climate data into NoData...')
    expanded_climate = Nibble(combined_climate, combined_climate, 'DATA_ONLY', 'PROCESS_NODATA')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export expanded raster to output raster
    iteration_start = time.time()
    print(f'\tExporting climate mean to output raster...')
    arcpy.CopyRaster_management(expanded_climate,
                                output_raster,
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
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished combining climate resolutions.'
    return out_process