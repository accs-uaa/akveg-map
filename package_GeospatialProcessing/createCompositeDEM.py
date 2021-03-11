# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Composite DEM
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Composite DEM" is a function that merges multiple DEM source rasters according to a specified order of priority.
# ---------------------------------------------------------------------------

# Define a function to merge multiple source elevation rasters according to an order of priority
def create_composite_dem(**kwargs):
    """
    Description: mosaics extracted source rasters with first data priority and extracts to mask
    Inputs: 'cell_size' -- a cell size for the output DEM
            'output_projection' -- the machine number for the output projection
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the grid raster (must be first) and the list of sources DEMs in prioritized order
            'output_array' -- an array containing the output raster
    Returned Value: Returns a raster dataset on disk containing the merged source DEM
    Preconditions: requires source DEMs and predefined grid
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    output_projection = kwargs['output_projection']
    elevation_inputs = kwargs['input_array']
    grid_raster = elevation_inputs.pop(0)
    composite_raster = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = grid_raster
    arcpy.env.extent = Raster(grid_raster).extent

    # Determine input raster value type
    value_number = arcpy.management.GetRasterProperties(elevation_inputs[0], "VALUETYPE")[0]
    no_data_value = arcpy.Describe(elevation_inputs[0]).noDataValue
    value_dictionary = {
        0: '1_BIT',
        1: '2_BIT',
        2: '4_BIT',
        3: '8_BIT_UNSIGNED',
        4: '8_BIT_SIGNED',
        5: '16_BIT_UNSIGNED',
        6: '16_BIT_SIGNED',
        7: '32_BIT_UNSIGNED',
        8: '32_BIT_SIGNED',
        9: '32_BIT_FLOAT',
        10: '64_BIT'
    }
    value_type = value_dictionary.get(int(value_number))
    print(f'Output data type will be {value_type}.')
    print(f'Output no data value will be {no_data_value}.')

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
    # Iterate through all input rasters to extract to grid and append to input list
    for raster in elevation_inputs:
        # Define output raster file path
        output_raster = os.path.join(source_folder, os.path.split(raster)[1])
        # Extract input raster if extracted raster does not already exist
        if os.path.exists(output_raster) == 0:
            try:
                print(f'\tExtracting elevation source {count} of {input_length}...')
                iteration_start = time.time()
                # Extract raster to mask
                extract_raster = ExtractByMask(raster, grid_raster)
                # Copy extracted raster to output
                print(f'\tSaving elevation source {count} of {input_length}...')
                arcpy.management.CopyRaster(extract_raster,
                                            output_raster,
                                            '',
                                            '',
                                            no_data_value,
                                            'NONE',
                                            'NONE',
                                            value_type,
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
        # Append extracted input raster to inputs list
        if os.path.exists(output_raster) == 1:
            input_rasters.append(output_raster)
        # Increase counter
        count += 1

    # Append the grid raster to the list of input rasters
    input_rasters.append(grid_raster)

    # Report the raster priority order
    raster_order = []
    for raster in input_rasters:
        name = os.path.split(raster)[1]
        raster_order.append(name)
    print(f'\tPriority of input sources for {grid_title}...')
    count = 1
    for raster in raster_order:
        print(f'\t\t{count}. {raster}')
        # Increase the counter
        count += 1

    # Mosaic raster tiles to new raster
    print(f'\tMosaicking the input rasters for {grid_title}...')
    iteration_start = time.time()
    arcpy.management.MosaicToNewRaster(input_rasters,
                                       mosaic_location,
                                       mosaic_name,
                                       composite_projection,
                                       value_type,
                                       cell_size,
                                       '1',
                                       'FIRST',
                                       'FIRST')
    # Enforce correct projection
    arcpy.management.DefineProjection(composite_raster, composite_projection)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished elevation composite for {grid_title}.'
    return out_process
