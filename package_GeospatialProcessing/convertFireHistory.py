# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert Fire History to Gridded Raster
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Convert Fire History to Gridded Raster" is a function that converts fire history polygons to raster with the fire year as the value and extracts the raster data to a major grid and study area.
# ---------------------------------------------------------------------------

# Define a function to convert fire history polygons to rasters
def convert_fire_history(**kwargs):
    """
    Description: converts fire history polygons to rasters and extracts to major grid and study area
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the target feature class to convert (must be first), the study area raster (must be second), and the grid raster (must be third)
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster dataset
    Preconditions: the target feature class must be created using the recent fire history function
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import ExtractByMask
    from arcpy.sa import IsNull
    from arcpy.sa import Raster
    import datetime
    import time
    import os

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    input_feature = kwargs['input_array'][0]
    study_area = kwargs['input_array'][1]
    grid_raster = kwargs['input_array'][2]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster and extent
    arcpy.env.snapRaster = study_area
    arcpy.env.extent = Raster(grid_raster).extent
    arcpy.env.cellSize = 'MINOF'

    # Define intermediate rasters
    convert_raster = os.path.splitext(output_raster)[0] + '.tif'

    # Convert fire history feature class to raster
    print('\tConverting feature class to raster within grid...')
    iteration_start = time.time()
    arcpy.conversion.PolygonToRaster(input_feature, 'FireYear', convert_raster, 'CELL_CENTER', 'FireYear', 10)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Convert no data values to zero
    print('\tConverting no data to zero...')
    iteration_start = time.time()
    zero_raster = Con(IsNull(Raster(convert_raster)), 0, Raster(convert_raster))
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Extract raster to study area
    print(f'\tExtracting raster to grid...')
    iteration_start = time.time()
    extract1_raster = ExtractByMask(zero_raster, grid_raster)
    print(f'\tExtracting raster to study area...')
    extract2_raster = ExtractByMask(extract1_raster, study_area)
    print(f'\tCopying extracted raster to new raster...')
    arcpy.management.CopyRaster(extract2_raster,
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
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE'
                                )
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully extracted recent fire history to study area.'
    return out_process
