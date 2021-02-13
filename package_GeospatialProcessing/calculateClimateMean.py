# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate Climate Mean
# Author: Timm Nawrocki
# Last Updated: 2021-01-13
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Calculate Climate Mean" is a function that calculates mean annual climate metrics from a set of individual month-year rasters representing a particular climate property. This function is intended to allow the creation of mean total annual precipitation and mean annual summer warmth index.
# ---------------------------------------------------------------------------

# Define a function to calculate mean annual climate properties from a set of input rasters
def calculate_climate_mean(**kwargs):
    """
    Description: calculates mean annual climate properties from a set of month-year climate rasters
    Inputs: 'input_array' -- an array containing the input month-year climate rasters
            'output_array' -- an array containing the output mean annual climate raster
            'denominator' -- an integer value of the number of years, which is the denominator in the mean calculation
    Returned Value: Returns a raster dataset on disk containing the mean annual climate property
    Preconditions: requires input month-year climate rasters that can be downloaded from SNAP at UAF
    """

    # Import packages
    import arcpy
    from arcpy.sa import CellStatistics
    from arcpy.sa import Int
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Parse key word argument inputs
    denominator = kwargs['denominator']
    input_rasters = kwargs['input_array']
    output_raster = kwargs['output_array'][0]

    # Set snap raster and extent
    arcpy.env.snapRaster = input_rasters[0]

    # Add all rasters in input array and divide by denominator
    iteration_start = time.time()
    print(f'\tCalculating climate mean from {len(input_rasters)} input rasters...')
    climate_sum = CellStatistics(input_rasters, 'SUM', 'NODATA', 'SINGLE_BAND')
    climate_mean = Int((climate_sum / denominator) + 0.5)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export climate mean to output raster
    iteration_start = time.time()
    print(f'\tExporting climate mean to output raster...')
    arcpy.management.CopyRaster(climate_mean,
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
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished calculating climate mean.'
    return out_process
