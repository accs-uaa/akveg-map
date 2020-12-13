# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge Spectral Tiles
# Author: Timm Nawrocki
# Last Updated: 2020-12-13
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Merge spectral tiles" is a function that merges tiles of a spectral metric within a predefined grid.
# ---------------------------------------------------------------------------

# Define a function to merge multiple source spectral tiles
def merge_spectral_tiles(**kwargs):
    """
    Description: extracts spectral tiles to an area and mosaics extracted tiles with first data priority
    Inputs: 'cell_size' -- a cell size for the output spectral raster
            'output_projection' -- the machine number for the output projection
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the grid raster (must be first), the study area raster (must be second), and the list of spectral tiles
            'output_array' -- an array containing the output spectral grid raster
    Returned Value: Returns a raster dataset on disk containing the merged spectral grid raster
    Preconditions: requires processed source spectral tiles and predefined grid
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import IsNull
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    import datetime
    import os
    import time

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    output_projection = kwargs['output_projection']
    work_geodatabase = kwargs['work_geodatabase']
    tile_inputs = kwargs['input_array']
    grid_raster = tile_inputs.pop(0)
    study_area = tile_inputs.pop(0)
    spectral_grid = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "66%"

    # Set snap raster and extent
    arcpy.env.snapRaster = study_area
    arcpy.env.extent = Raster(grid_raster).extent

    # Define the target projection
    composite_projection = arcpy.SpatialReference(output_projection)

    # Define intermediate rasters
    mosaic_raster = os.path.splitext(spectral_grid)[0] + '_mosaic.tif'
    nibble_raster = os.path.splitext(spectral_grid)[0] + '_nibble.tif'
    spectral_area = os.path.splitext(spectral_grid)[0] + '_area.tif'

    # Define folder structure
    grid_title = os.path.splitext(os.path.split(grid_raster)[1])[0]
    mosaic_location, mosaic_name = os.path.split(mosaic_raster)

    # Create source folder within mosaic location if it does not already exist
    source_folder = os.path.join(mosaic_location, 'sources')
    if os.path.exists(source_folder) == 0:
        os.mkdir(source_folder)

    # Create an empty list to store existing extracted source rasters for the grid
    input_length = len(tile_inputs)
    input_rasters = []

    # Identify raster extent of grid
    print(f'\tExtracting {input_length} spectral tiles...')
    grid_extent = Raster(grid_raster).extent
    grid_array = arcpy.Array()
    grid_array.add(arcpy.Point(grid_extent.XMin, grid_extent.YMin))
    grid_array.add(arcpy.Point(grid_extent.XMin, grid_extent.YMax))
    grid_array.add(arcpy.Point(grid_extent.XMax, grid_extent.YMax))
    grid_array.add(arcpy.Point(grid_extent.XMax, grid_extent.YMin))
    grid_array.add(arcpy.Point(grid_extent.XMin, grid_extent.YMin))
    grid_polygon = arcpy.Polygon(grid_array)

    # Save grid polygon
    grid_feature = os.path.join(work_geodatabase, 'grid_polygon')
    arcpy.CopyFeatures_management(grid_polygon, grid_feature)
    arcpy.DefineProjection_management(grid_feature, composite_projection)

    # Iterate through all input tiles and extract to grid if they overlap
    count = 1
    for raster in tile_inputs:
        output_raster = os.path.join(source_folder, os.path.split(raster)[1])
        if os.path.exists(output_raster) == 0:
            # Identify raster extent of tile
            tile_extent = Raster(raster).extent
            tile_array = arcpy.Array()
            tile_array.add(arcpy.Point(tile_extent.XMin, tile_extent.YMin))
            tile_array.add(arcpy.Point(tile_extent.XMin, tile_extent.YMax))
            tile_array.add(arcpy.Point(tile_extent.XMax, tile_extent.YMax))
            tile_array.add(arcpy.Point(tile_extent.XMax, tile_extent.YMin))
            tile_array.add(arcpy.Point(tile_extent.XMin, tile_extent.YMin))
            tile_polygon = arcpy.Polygon(tile_array)

            # Save tile polygon
            tile_feature = os.path.join(work_geodatabase, 'tile_polygon')
            arcpy.CopyFeatures_management(tile_polygon, tile_feature)
            arcpy.DefineProjection_management(tile_feature, composite_projection)

            # Select tile extent with grid extent
            selection = int(arcpy.GetCount_management(
                arcpy.SelectLayerByLocation_management(tile_feature,
                                                       'INTERSECT',
                                                       grid_feature,
                                                       '',
                                                       'NEW_SELECTION',
                                                       'NOT_INVERT'))
                            .getOutput(0))

            # If tile overlaps grid then perform extraction
            if selection == 1:
                # Start timing function
                iteration_start = time.time()
                print(f'\t\tExtracting spectral tile {count} of {input_length}...')
                # Extract raster to mask
                extract_raster = ExtractByMask(raster, grid_raster)
                # Copy extracted raster to output
                print(f'\t\tSaving spectral tile {count} of {input_length}...')
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
            # If tile does not overlap grid then report message
            else:
                print(f'\t\tSpectral tile {count} of {input_length} does not overlap grid...')
                print('\t\t----------')

            # Remove tile feature class
            if arcpy.Exists(tile_feature) == 1:
                arcpy.Delete_management(tile_feature)

        # If extracted tile already exists then report message
        else:
            print(f'\t\tExtracted spectral tile {count} of {input_length} already exists...')
            print('\t\t----------')

        # If the output raster exists then append it to the raster list
        if os.path.exists(output_raster) == 1:
            input_rasters.append(output_raster)
        count += 1

    # Remove grid feature
    if arcpy.Exists(grid_feature) == 1:
        arcpy.Delete_management(grid_feature)
    print(f'\tFinished extracting {input_length} spectral tiles.')
    print('\t----------')

    # Mosaic raster tiles to new raster
    print(f'\tMosaicking the input rasters for {grid_title}...')
    iteration_start = time.time()
    arcpy.MosaicToNewRaster_management(input_rasters,
                                       mosaic_location,
                                       mosaic_name,
                                       composite_projection,
                                       '16_BIT_SIGNED',
                                       cell_size,
                                       '1',
                                       'FIRST',
                                       'FIRST')
    # Enforce correct projection
    arcpy.DefineProjection_management(mosaic_raster, composite_projection)
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
    raster_null = SetNull(IsNull(Raster(mosaic_raster)), 1, 'VALUE = 1')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Impute missing data by nibbling the NoData from the focal mean
    print('\tImputing missing values by geographic nearest neighbor...')
    iteration_start = time.time()
    raster_filled = Nibble(Raster(mosaic_raster), raster_null, 'DATA_ONLY', 'PROCESS_NODATA', '')
    # Copy nibble raster to output
    print(f'\tSaving filled raster...')
    arcpy.CopyRaster_management(raster_filled,
                                nibble_raster,
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
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Remove overflow fill from the grid and the study area
    print('\tRemoving overflow fill...')
    iteration_start = time.time()
    raster_preliminary = ExtractByMask(nibble_raster, study_area)
    # Copy nibble raster to output
    arcpy.CopyRaster_management(raster_preliminary,
                                spectral_area,
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
    raster_final = ExtractByMask(spectral_area, grid_raster)
    print(f'\tSaving spectral composite for {grid_title}...')
    iteration_start = time.time()
    arcpy.CopyRaster_management(raster_final,
                                spectral_grid,
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
    # Delete intermediate rasters
    if arcpy.Exists(mosaic_raster) == 1:
        arcpy.Delete_management(mosaic_raster)
    if arcpy.Exists(nibble_raster) == 1:
        arcpy.Delete_management(nibble_raster)
    if arcpy.Exists(spectral_area) == 1:
        arcpy.Delete_management(spectral_area)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully created {os.path.split(spectral_grid)[1]}'
    return out_process
