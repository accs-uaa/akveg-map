# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Raster
# Author: Timm Nawrocki
# Last Updated: 2021-05-31
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Extract Raster" is a function that extracts raster data to a mask.
# ---------------------------------------------------------------------------

# Define a function to extract raster data to a mask
def extract_raster(**kwargs):
    """
    Description: extracts a raster to a mask
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the target raster to extract (must be first) and the mask raster (must be second)
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster dataset
    Preconditions: the initial raster must be created from other scripts and the study area raster must be created manually
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Raster
    import datetime
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    input_raster = kwargs['input_array'][0]
    mask_raster = kwargs['input_array'][1]
    output_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster and extent
    arcpy.env.snapRaster = mask_raster
    arcpy.env.extent = Raster(mask_raster).extent

    # Extract raster to study area
    print('\t\tPerforming extraction to study area...')
    iteration_start = time.time()
    extract_raster = ExtractByMask(input_raster, mask_raster)
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
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')
    out_process = f'\tSuccessfully extracted raster data to mask.'
    return out_process
