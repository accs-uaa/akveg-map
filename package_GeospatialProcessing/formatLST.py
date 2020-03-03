# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Format Land Surface Temperature
# Author: Timm Nawrocki
# Last Updated: 2020-03-02
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Format land surface temperature" is a function that reprojects and resamples LST within a predefined grid.
# ---------------------------------------------------------------------------

# Define a function to format land surface temperature
def format_lst(**kwargs):
    """
    Description: reprojects and resamples LST within a predefined grid
    Inputs: 'cell_size' -- a cell size for the output LST
            'input_projection' -- the machine number for the LST input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transform' -- the ESRI code for the necessary geographic transformation (can be blank)
            'input_array' -- an array containing the grid raster (must be first) and the LST raster
            'output_array' -- an array containing the output LST grid raster
    Returned Value: Returns a raster dataset on disk containing the reformatted LST
    Preconditions: requires mean decadal monthly LST downloaded from Google Earth Engine
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import ExtractByMask
    from arcpy.sa import FocalStatistics
    from arcpy.sa import Int
    from arcpy.sa import IsNull
    from arcpy.sa import NbrCircle
    from arcpy.sa import Nibble
    from arcpy.sa import SetNull
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "66%"

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transform = kwargs['geographic_transform']
    grid_raster = kwargs['input_array'][0]
    lst_raster = kwargs['input_array'][1]
    lst_grid = kwargs['output_array'][0]

    # Define intermediate dataset
    reprojected_raster = os.path.splitext(lst_grid)[0] + '_reprojected.tif'

    # Define the original and target projection
    original_projection = arcpy.SpatialReference(input_projection)
    target_projection = arcpy.SpatialReference(output_projection)

    # Define folder structure
    output_location = os.path.split(lst_grid)[0]
    # Create mosaic location if it does not already exist
    if os.path.exists(output_location) == 0:
        os.mkdir(output_location)

    # Set snap raster
    arcpy.env.snapRaster = lst_raster

    # Extract LST raster to the grid
    print('\tExtracting LST to grid...')
    iteration_start = time.time()
    extract_raster = ExtractByMask(lst_raster, grid_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Set snap raster
    arcpy.env.snapRaster = grid_raster

    # Reproject and resample LST raster
    print('\tReprojecting and resampling LST...')
    iteration_start = time.time()
    arcpy.ProjectRaster_management(extract_raster,
                                   reprojected_raster,
                                   target_projection,
                                   'BILINEAR',
                                   cell_size,
                                   geographic_transform,
                                   '',
                                   original_projection)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate a focal mean that can be used to fill missing data
    print('\tCalculating gap edge mean values...')
    iteration_start = time.time()
    raster_focal = FocalStatistics(reprojected_raster, NbrCircle(100, 'CELL'), 'MEAN', 'DATA')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Calculate the missing area
    print('\tCalculating null space...')
    iteration_start = time.time()
    raster_null = SetNull(IsNull(raster_focal), 1, 'VALUE = 1')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Impute missing data by nibbling the NoData from the focal mean
    print('\tImputing missing values by nearest neighbor...')
    iteration_start = time.time()
    raster_nibble = Nibble(raster_focal, raster_null, 'DATA_ONLY', 'PROCESS_NODATA', '')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Smooth the imputed data by calculating a second focal mean with the same parameters
    print('\tSmoothing imputed values...')
    iteration_start = time.time()
    raster_smoothed = FocalStatistics(raster_nibble, NbrCircle(100, 'CELL'), 'MEAN', 'DATA')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Fill missing values in the original data with the smoothed imputed values
    print('\tFilling missing values with smoothed imputed values...')
    iteration_start = time.time()
    raster_filled = Con(IsNull(reprojected_raster), raster_smoothed, reprojected_raster, 'VALUE = 1')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Remove overflow fill from the grid
    print('\tRemoving overflow fill...')
    iteration_start = time.time()
    raster_final = ExtractByMask(raster_filled, grid_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Round to integer and store as 16 bit signed raster
    print('\tRounding to nearest integer and exporting raster...')
    iteration_start = time.time()
    integer_raster = Int(raster_final + 0.5)
    arcpy.CopyRaster_management(integer_raster,
                                lst_grid,
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
    # Delete intermediate raster
    if arcpy.Exists(reprojected_raster) == 1:
        arcpy.Delete_management(reprojected_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully created {os.path.split(lst_grid)[1]}'
    return out_process