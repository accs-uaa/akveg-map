# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Interpolate Raster
# Author: Timm Nawrocki
# Last Updated: 2021-01-08
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Interpolate Raster" is a function that interpolates a raster based on geographic nearest neighbors.
# ---------------------------------------------------------------------------

# Define a function to interpolate a raster using geographic nearest neighbors
def interpolate_raster(**kwargs):
    """
    Description: interpolates missing raster data using nearest existing raster data
    Inputs: 'input_array' -- an array containing the study area raster (must be first) and the climate raster (last)
            'output_array' -- an array containing the output climate raster for the grid
    Returned Value: Returns a raster dataset on disk containing the combined climate property for a grid
    Preconditions: requires an input grid raster and climate property raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import IsNull
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    import datetime
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Parse key word argument inputs
    study_area = kwargs['input_array'][0]
    climate_raster = kwargs['input_array'][1]
    output_raster = kwargs['output_array'][0]

    # Set snap raster and extent
    arcpy.env.snapRaster = climate_raster
    arcpy.env.cellSize = 'MINOF'
    arcpy.env.extent = Raster(study_area).extent

    # Interpolate missing data from the climate raster
    iteration_start = time.time()
    # Calculate the missing area
    print('\tCalculating null space...')
    raster_null = SetNull(IsNull(Raster(climate_raster)), 1, 'VALUE = 1')
    print(f'\tInterpolating missing data...')
    nibble_raster = Nibble(Raster(climate_raster), raster_null, 'DATA_ONLY', 'PROCESS_NODATA', '')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export extracted raster to output raster
    iteration_start = time.time()
    print(f'\tExporting interpolated raster to output raster...')
    arcpy.CopyRaster_management(nibble_raster,
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
    out_process = f'Finished interpolating raster.'
    return out_process
