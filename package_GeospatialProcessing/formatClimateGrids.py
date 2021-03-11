# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Format Climate Grids
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Format Climate Grids" is a function that extracts the combined resolution climate data to the major analysis grids.
# ---------------------------------------------------------------------------

# Define a function to format climate data to analysis grids
def format_climate_grids(**kwargs):
    """
    Description: extracts climate data to the grid
    Inputs: 'input_array' -- an array containing the study area raster (must be first), grid raster (must be second) and the climate raster (last)
            'output_array' -- an array containing the output climate raster for the grid
    Returned Value: Returns a raster dataset on disk containing the combined climate property for a grid
    Preconditions: requires an input grid raster and climate property raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Raster
    import datetime
    import time

    # Parse key word argument inputs
    study_area = kwargs['input_array'][0]
    grid_raster = kwargs['input_array'][1]
    climate_raster = kwargs['input_array'][2]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set snap raster and extent
    arcpy.env.snapRaster = study_area
    arcpy.env.cellSize = 'MINOF'
    arcpy.env.extent = Raster(grid_raster).extent

    # Extract the climate data to the grid raster and study area
    print(f'\tExtracting climate data to grid...')
    iteration_start = time.time()
    extract_grid = ExtractByMask(climate_raster, grid_raster)
    extract_area = ExtractByMask(extract_grid, study_area)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export extracted raster to output raster
    print(f'\tExporting extracted raster to output raster...')
    iteration_start = time.time()
    arcpy.CopyRaster_management(extract_area,
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
    out_process = f'Finished formatting climate data to grid.'
    return out_process
