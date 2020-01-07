# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge Source Elevation Tiles
# Author: Timm Nawrocki
# Last Updated: 2019-12-03
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Merge Source Elevation Tiles" is a function that creates single merged DEM from input tiles of the same source with new projection, snap raster, and cell size.
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
            'input_array' -- an array containing the snap raster
            'output_array' -- an array containing the output raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Int
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "66%"

    # Parse key word argument inputs
    tile_folder = kwargs['tile_folder']
    projected_folder = kwargs['projected_folder']
    workspace = kwargs['workspace']
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transformation = kwargs['geographic_transformation']
    snap_raster = kwargs['input_array'][0]
    dem_composite = kwargs['output_array'][0]

    # Define intermediate datasets
    mosaic_location, mosaic_name = os.path.split(dem_composite)

    # Start timing function
    iteration_start = time.time()
    # Create a list of DEM raster tiles
    print('Compiling list of raster tiles...')
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
    print(f'Raster list completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Define projection and reproject all rasters in list
    print(f'Reprojecting {len(tile_rasters)} raster tiles...')
    # Define the initial projection
    tile_projection = arcpy.SpatialReference(input_projection)
    # Define the target projection
    composite_projection = arcpy.SpatialReference(output_projection)
    # Set snap raster
    arcpy.env.snapRaster = snap_raster
    # Set initial counter
    count = 1
    # Reproject all rasters in list
    for raster in tile_rasters:
        # Define intermediate and output raster
        reprojected_raster = os.path.join(projected_folder, os.path.splitext(os.path.split(raster)[1])[0] + '_reprojected.tif')
        output_raster = os.path.join(projected_folder, os.path.splitext(os.path.split(raster)[1])[0] + '.tif')
        # Check if output raster already exists:
        if os.path.exists(output_raster) == 0:
            # Start timing function
            iteration_start = time.time()
            print(f'\tReprojecting tile {count} of {len(tile_list)}...')
            # Define initial projection
            arcpy.DefineProjection_management(raster, tile_projection)
            # Reproject tile
            arcpy.ProjectRaster_management(raster,
                                           reprojected_raster,
                                           composite_projection,
                                           'BILINEAR',
                                           cell_size,
                                           geographic_transformation)
            # Enforce new projection
            arcpy.DefineProjection_management(reprojected_raster, composite_projection)
            # Set values less than -50 to null
            corrected_raster = SetNull(reprojected_raster, reprojected_raster, 'VALUE < -50')
            # Round to integer and store as 16 bit signed raster
            integer_raster = Int(Raster(corrected_raster) + 0.5)
            # Convert corrected raster to 16 bit signed
            arcpy.CopyRaster_management(integer_raster, output_raster, '', '', '-32768', 'NONE', 'NONE', '16_BIT_SIGNED','NONE', 'NONE', 'TIFF', 'NONE')
            # Delete intermediate raster
            arcpy.Delete_management(reprojected_raster)
            # End timing
            iteration_end = time.time()
            iteration_elapsed = int(iteration_end - iteration_start)
            iteration_success_time = datetime.datetime.now()
            # Report success for iteration
            print(f'\tFinished reprojecting tile {count} of {len(tile_list)}...')
            print(f'\tTile projection completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
            print('\t----------')
        # Return message if output raster already exists
        else:
            print(f'\tTile {count} of {len(tile_list)} already processed...')
        # Increase count
        count += 1
    # Report success for loop
    print(f'Defined projection for {len(tile_list)} raster tiles...')
    print('----------')

    # Start timing function
    iteration_start = time.time()
    # Create a list of projected DEM raster tiles
    print('Compiling list of projected raster tiles...')
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
    print(f'Raster list completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Start timing function
    iteration_start = time.time()
    print('Creating composite from tiles...')
    # Mosaic raster tiles to new raster
    arcpy.MosaicToNewRaster_management(projected_rasters,
                                       mosaic_location,
                                       mosaic_name,
                                       composite_projection,
                                       '16_BIT_SIGNED',
                                       cell_size,
                                       '1',
                                       'MAXIMUM',
                                       'FIRST')
    # Enforce correct projection
    arcpy.DefineProjection_management(dem_composite, composite_projection)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Raster composite completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Delete intermediate dataset
    out_process = 'Successful creating composite DEM.'
    return out_process
