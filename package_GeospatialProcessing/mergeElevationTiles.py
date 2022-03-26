# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge source elevation tiles
# Author: Timm Nawrocki
# Last Updated: 2021-11-22
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Merge source elevation tiles" is a function that creates single merged DEM from input tiles of the same source with new projection, snap raster, and cell size.
# ---------------------------------------------------------------------------

# Define function to merge source elevation tiles
def merge_elevation_tiles(**kwargs):
    """
    Description: creates a DEM from individual DEM tiles
    Inputs: 'tile_folder' -- a folder containing the raster tiles
            'projected_folder' -- a folder in which to store the projected tiles
            'cell_size' -- a cell size for the output DEM
            'input_projection' -- the machine number for the input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'input_array' -- an array containing the area raster
            'output_array' -- an array containing the output raster
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    tile_folder = kwargs['tile_folder']
    projected_folder = kwargs['projected_folder']
    workspace = kwargs['workspace']
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transformation = kwargs['geographic_transformation']
    area_raster = kwargs['input_array'][0]
    dem_composite = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster
    arcpy.env.snapRaster = area_raster

    # Define input and output coordinate systems
    input_system = arcpy.SpatialReference(input_projection)
    # Define the target projection
    output_system = arcpy.SpatialReference(output_projection)

    # Define intermediate datasets
    mosaic_location, mosaic_name = os.path.split(dem_composite)

    # Create a list of DEM raster tiles
    print('Compiling list of raster tiles...')
    iteration_start = time.time()
    arcpy.env.workspace = tile_folder
    tile_list = arcpy.ListRasters('*', 'ALL')
    # Add file path to raster list
    tile_rasters = []
    for tile in tile_list:
        tile_path = os.path.join(tile_folder, tile)
        tile_rasters.append(tile_path)
    # Set environment workspace
    arcpy.env.workspace = workspace
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Process will form composite from {len(tile_list)} raster tiles...')
    print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Reproject all rasters in list
    print(f'Reprojecting {len(tile_rasters)} raster tiles...')
    # Set initial counter
    count = 1
    # Iterate through rasters
    for raster in tile_rasters:
        # Define output raster
        output_raster = os.path.join(projected_folder, os.path.splitext(os.path.split(raster)[1])[0] + '.tif')
        # Reproject raster if it does not already exist
        if os.path.exists(output_raster) == 0:
            print(f'\tReprojecting tile {count} of {len(tile_list)}...')
            iteration_start = time.time()
            # Define initial projection
            arcpy.management.DefineProjection(raster, input_system)
            # Reproject raster
            arcpy.management.ProjectRaster(raster,
                                           output_raster,
                                           output_system,
                                           'BILINEAR',
                                           cell_size,
                                           geographic_transformation,
                                           '',
                                           input_system)
            # Enforce new projection
            arcpy.management.DefineProjection(output_raster, output_system)
            # End timing
            iteration_end = time.time()
            iteration_elapsed = int(iteration_end - iteration_start)
            iteration_success_time = datetime.datetime.now()
            # Report success for iteration
            print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
            print('\t----------')
        # Return message if output raster already exists
        else:
            print(f'\tTile {count} of {len(tile_list)} already processed...')
        # Increase count
        count += 1
    # Report success for loop
    print(f'Defined projection for {len(tile_list)} raster tiles...')
    print('----------')

    # Create a list of projected DEM raster tiles
    print('Compiling list of projected raster tiles...')
    iteration_start = time.time()
    arcpy.env.workspace = projected_folder
    projected_list = arcpy.ListRasters('*', 'ALL')
    # Add file path to raster list
    projected_rasters = []
    for tile in projected_list:
        tile_path = os.path.join(projected_folder, tile)
        projected_rasters.append(tile_path)
    # Set environment workspace
    arcpy.env.workspace = workspace
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Process will form composite from {len(tile_list)} raster tiles...')
    print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Mosaic raster tiles to new raster
    print('Creating composite from tiles...')
    iteration_start = time.time()
    arcpy.management.MosaicToNewRaster(projected_rasters,
                                       mosaic_location,
                                       mosaic_name,
                                       output_system,
                                       '32_BIT_FLOAT',
                                       cell_size,
                                       '1',
                                       'LAST',
                                       'LAST')
    # Enforce correct projection
    arcpy.management.DefineProjection(dem_composite, output_system)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Report end status
    out_process = 'Successful creating composite DEM.'
    return out_process
