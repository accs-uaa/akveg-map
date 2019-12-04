# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Composite DEM
# Author: Timm Nawrocki
# Last Updated: 2019-12-03
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Composite DEM" is a function that merges multiple DEM source rasters according to a specified order of priority.
# ---------------------------------------------------------------------------

# Define a wrapper function for arcpy geoprocessing tasks
def create_composite_dem(**kwargs):
    """
    Description: extracts source rasters to an area and mosaics extracted source rasters with first data priority
    Inputs: 'cell_size' -- a cell size for the output DEM
            'output_projection' -- the machine number for the output projection
            'input_array' -- an array containing the grid raster (must be first) and the list of sources DEMs in prioritized order
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster dataset on disk containing the merged source DEM
    Preconditions: requires source DEMs and predefined grid
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "66%"

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    output_projection = kwargs['output_projection']
    elevation_inputs = kwargs['input_array']
    grid_raster = elevation_inputs.pop(0)
    composite_raster = kwargs['output_array'][0]

    # Set snap raster
    arcpy.env.snapRaster = grid_raster

    # Define the target projection
    composite_projection = arcpy.SpatialReference(output_projection)

    # Define folder structure
    grid_title = os.path.splitext(os.path.split(grid_raster)[1])[0]
    mosaic_location, mosaic_name = os.path.split(composite_raster)
    # Create mosaic location if it does not already exist
    if os.path.exists(mosaic_location) == 0:
        os.mkdir(mosaic_location)

    # Create source folder within mosaic location if it does not already exist
    source_folder = os.path.join(mosaic_location, 'sources')
    if os.path.exists(source_folder) == 0:
        os.mkdir(source_folder)

    # Create an empty list to store existing extracted source rasters for the area of interest
    input_length = len(elevation_inputs)
    input_rasters = []
    count = 1
    for raster in elevation_inputs:
        output_raster = os.path.join(source_folder, os.path.split(raster)[1])
        if os.path.exists(output_raster) == 0:
            try:
                # Start timing function
                iteration_start = time.time()
                print(f'\tExtracting elevation source {count} of {input_length}...')
                # Extract raster to mask
                extract_raster = ExtractByMask(raster, grid_raster)
                # Copy extracted raster to output
                print(f'\tSaving elevation source {count} of {input_length}...')
                arcpy.CopyRaster_management(extract_raster,
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
                print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
                print('\t----------')
            except:
                print('\tElevation source does not overlap grid...')
                print('\t----------')
        else:
            print(f'\tExtracted elevation source {count} of {input_length} already exists...')
            print('\t----------')
        if os.path.exists(output_raster) == 1:
            input_rasters.append(output_raster)
        count += 1

    # Report the raster priority order
    raster_order = []
    for raster in input_rasters:
        name = os.path.split(raster)[1]
        raster_order.append(name)
    print(f'\tPriority of input sources for {grid_title}...')
    count = 1
    for raster in raster_order:
        print(f'\t\t{count}. {raster}')
        count += 1

    # Mosaic raster tiles to new raster
    print(f'\tMosaicking the input rasters for {grid_title}...')
    iteration_start = time.time()
    out_process = arcpy.MosaicToNewRaster_management(input_rasters,
                                                     mosaic_location,
                                                     mosaic_name,
                                                     composite_projection,
                                                     '16_BIT_SIGNED',
                                                     cell_size,
                                                     '1',
                                                     'FIRST',
                                                     'FIRST')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished elevation composite for {grid_title}.'
    return out_process