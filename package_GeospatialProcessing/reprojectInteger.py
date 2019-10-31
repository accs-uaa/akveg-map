# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Reproject to Integer Raster
# Author: Timm Nawrocki
# Last Updated: 2019-10-29
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Reproject to Integer Raster" is a function that reprojects and resamples a raster and converts the output to 16 bit signed integers.
# ---------------------------------------------------------------------------

# Define function to reproject raster and store integer result
def reproject_integer(**kwargs):
    """
    Description: creates a DEM from individual DEM tiles
    Inputs: 'cell_size' -- a cell size for the output DEM
            'input_projection' -- the machine number for the input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'input_array' -- an array containing the input raster and the snap raster
            'output_array' -- the output should be an array with a full feature class and a clipped feature class
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
    print(f'Reprojecting input raster...')
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
    print(f'Finished reprojecting input raster...')
    print(f'Projection completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Start timing function
    iteration_start = time.time()
    print(f'Converting raster to 16 bit integer...')
    # Round to integer and store as 16 bit signed raster
    integer_raster = Int(Raster(reprojected_raster) + 0.5)
    arcpy.CopyRaster_management(integer_raster, output_raster, '', '', '-32768', 'NONE', 'NONE', '16_BIT_SIGNED',
                                'NONE', 'NONE', 'TIFF', 'NONE')
    # Delete intermediate raster
    arcpy.Delete_management(reprojected_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(f'Finished converting to 16 bit integer...')
    print(
        f'Conversion completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Delete intermediate dataset
    out_process = 'Successful reprojecting and converting raster.'
    return out_process