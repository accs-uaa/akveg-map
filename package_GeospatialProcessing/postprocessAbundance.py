# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Post-process Species Abundance
# Author: Timm Nawrocki
# Last Updated: 2020-06-04
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Post-process Species Abundance" is a function that merges species raster tiles into a single raster.
# ---------------------------------------------------------------------------

# Define a function to post-process species abundance tiles
def postprocess_abundance(**kwargs):
    """
    Description: merges a list of species raster tiles
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'cell_size' -- an integer cell size in the same units as the coordinate system
            'output_projection' -- an integer EPSG code for the output projected coordinate system
            'input_array' -- an array containing the snap raster (must be first) and all tile rasters
            'output_array' -- an array that contains the output species raster
    Returned Value: Returns a raster for the species abundance
    Preconditions: a set of species raster tiles must be generated through model prediction and conversion to raster.
    """

    # Import packages
    import arcpy
    import os
    import datetime
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    cell_size = kwargs['cell_size']
    output_projection = kwargs['output_projection']
    raster_tiles = kwargs['input_array']
    snap_raster = raster_tiles.pop(0)
    output_raster = kwargs['output_array'][0]

    # Set mosaic location and name
    mosaic_location, mosaic_name = os.path.split(output_raster)

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace and snap raster
    arcpy.env.workspace = work_geodatabase
    # Set snap raster
    arcpy.env.snapRaster = snap_raster

    # Set output projection
    composite_projection = arcpy.SpatialReference(output_projection)

    # Mosaic raster tiles to new raster
    print('\tMerging raster tiles...')
    iteration_start = time.time()
    arcpy.MosaicToNewRaster_management(raster_tiles,
                                       mosaic_location,
                                       mosaic_name,
                                       composite_projection,
                                       '8_BIT_SIGNED',
                                       cell_size,
                                       '1',
                                       'LAST',
                                       'LAST'
                                       )
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully post-processed species abundance data.'
    return out_process