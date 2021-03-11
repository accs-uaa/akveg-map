# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate Land Surface Temperature Summer Warmth Index
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Calculate Land Surface Temperature Summer Warmth Index" is a function that sums LST means from May-September and then reprojects them to Alaska Albers Equal Area Conic.
# ---------------------------------------------------------------------------

# Define a function to calculate land surface temperature warmth index
def calculate_lst_warmth_index(**kwargs):
    """
    Description: sums LST values from multiple months and reprojects to AKALB
    Inputs: 'cell_size' -- a cell size for the output LST
            'input_projection' -- the machine number for the LST input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transform' -- the ESRI code for the necessary geographic transformation (can be blank)
            'input_array' -- an array containing the study area raster (must be first) and the mean LST rasters for May-September
            'output_array' -- an array containing the output LST warmth index raster
    Returned Value: Returns a raster dataset on disk containing the reformatted LST
    Preconditions: requires mean decadal monthly LST downloaded from Google Earth Engine
    """

    # Import packages
    import arcpy
    from arcpy.sa import CellStatistics
    from arcpy.sa import Int
    from arcpy.sa import Nibble
    import datetime
    import os
    import time

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transform = kwargs['geographic_transform']
    input_rasters = kwargs['input_array']
    study_area = input_rasters.pop(0)
    lst_processed = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set snap raster
    arcpy.env.snapRaster = input_rasters[0]

    # Define intermediate dataset
    reprojected_raster = os.path.splitext(lst_processed)[0] + '_reprojected.tif'

    # Define the coordinate systems
    input_system = arcpy.SpatialReference(input_projection)
    output_system = arcpy.SpatialReference(output_projection)

    # Calculate LST sum
    print('\tCalculating MODIS LST Warmth Index...')
    iteration_start = time.time()
    lst_sum = CellStatistics(input_rasters, 'SUM', 'NODATA', 'SINGLE_BAND')
    lst_warmth = Int((lst_sum / 10) + 0.5)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Set snap raster
    arcpy.env.snapRaster = study_area

    # Reproject and resample LST raster
    print('\tReprojecting LST warmth index to AKALB...')
    iteration_start = time.time()
    arcpy.management.ProjectRaster(lst_warmth,
                                   reprojected_raster,
                                   output_system,
                                   'BILINEAR',
                                   cell_size,
                                   geographic_transform,
                                   '',
                                   input_system)
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
    print(f'\tExpanding lst warmth index into NoData...')
    expanded_lst = Nibble(reprojected_raster, reprojected_raster, 'DATA_ONLY', 'PROCESS_NODATA')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export the reprojected raster as a 16 bit unsigned raster
    print('\tExporting the expanded raster...')
    iteration_start = time.time()
    arcpy.management.CopyRaster(expanded_lst,
                                lst_processed,
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
        arcpy.management.Delete(reprojected_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully created MODIS LST Warmth Index.'
    return out_process
