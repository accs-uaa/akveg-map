# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract to Study Area
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Extract to Study Area" is a function that extracts raster data to a smaller study area. This script is intended to ensure that all gridded predictor datasets are within the target study area and have the same extent.
# ---------------------------------------------------------------------------

# Define a function to extract raster data to a study area
def extract_to_study_area(**kwargs):
    """
    Description: extracts a raster to a study area
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the target raster to extract (must be first), the study area raster (must be second), and the grid raster (must be third)
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster dataset
    Preconditions: the initial raster must be created from other scripts and the study area raster must be created manually
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    input_raster = kwargs['input_array'][0]
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

    # Define intermediate datasets
    extract_intermediate = os.path.splitext(output_raster)[0] + '_intermediate.tif'

    # Extract raster to grid
    print('\t\tPerforming extraction to grid...')
    iteration_start = time.time()
    intermediate_raster = ExtractByMask(input_raster, grid_raster)
    arcpy.management.CopyRaster(intermediate_raster,
                                extract_intermediate,
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
                                'NO_TRANSPOSE')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')

    # Extract raster to study area
    print('\t\tPerforming extraction to study area...')
    iteration_start = time.time()
    extract_raster = ExtractByMask(extract_intermediate, study_area)
    arcpy.management.CopyRaster(extract_raster,
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
                                'NO_TRANSPOSE')
    # Delete intermediate dataset if it exists
    if arcpy.Exists(extract_intermediate) == 1:
        arcpy.management.Delete(extract_intermediate)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')
    out_process = f'\tSuccessfully extracted data to study area.'
    return out_process
