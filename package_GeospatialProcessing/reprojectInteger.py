# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Reproject to Integer Raster
# Author: Timm Nawrocki
# Last Updated: 2019-10-29
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Reproject to Integer Raster" is a function that reprojects and resamples a raster and converts the output to 16 bit signed integers with some conversion factor representing the number of decimal points to preserve.
# ---------------------------------------------------------------------------

# Define function to reproject raster and store integer result
def reproject_integer(**kwargs):
    """
    Description: reprojects a raster and converts to integer by a specified multiplicative factor
    Inputs: 'cell_size' -- a cell size for the output DEM
            'input_projection' -- the machine number for the input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'conversion_factor' -- a number that will be multiplied with the original value before being converted to integer
            'input_array' -- an array containing the input raster and the snap raster
            'output_array' -- an array containing the output raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Int
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transformation = kwargs['geographic_transformation']
    conversion_factor = kwargs['conversion_factor']
    input_raster = kwargs['input_array'][0]
    snap_raster = kwargs['input_array'][1]
    output_raster = kwargs['output_array'][0]

    # Define the initial projection
    initial_projection = arcpy.SpatialReference(input_projection)
    # Define the target projection
    composite_projection = arcpy.SpatialReference(output_projection)
    # Set snap raster
    arcpy.env.snapRaster = snap_raster

    # Start timing function
    iteration_start = time.time()
    print(f'\tReprojecting input raster...')
    # Define intermediate and output raster
    reprojected_raster = os.path.splitext(input_raster)[0] + '_reprojected.tif'
    # Define initial projection
    arcpy.DefineProjection_management(input_raster, initial_projection)
    # Reproject raster
    arcpy.ProjectRaster_management(input_raster,
                                   reprojected_raster,
                                   composite_projection,
                                   'BILINEAR',
                                   cell_size,
                                   geographic_transformation)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(f'\tProjection completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Start timing function
    iteration_start = time.time()
    print(f'\tConverting raster to 16 bit integer...')
    # Round to integer and store as 16 bit signed raster
    integer_raster = Int((Raster(reprojected_raster) * conversion_factor) + 0.5)
    arcpy.CopyRaster_management(integer_raster, output_raster, '', '', '-32768', 'NONE', 'NONE', '16_BIT_SIGNED',
                                'NONE', 'NONE', 'TIFF', 'NONE')
    # Delete intermediate raster
    arcpy.Delete_management(reprojected_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(f'\tConversion completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Delete intermediate dataset
    out_process = 'Successful reprojecting and converting raster.'
    return out_process