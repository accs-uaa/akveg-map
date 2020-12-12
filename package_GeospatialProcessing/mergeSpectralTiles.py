# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge Spectral Tiles
# Author: Timm Nawrocki
# Last Updated: 2019-12-30
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Merge spectral tiles" is a function that merges tiles of a spectral metric within a predefined grid.
# ---------------------------------------------------------------------------

# Define a function to merge multiple source spectral tiles
def merge_spectral_tiles(**kwargs):
    """
    Description: extracts spectral tiles to an area and mosaics extracted tiles with first data priority
    Inputs: 'cell_size' -- a cell size for the output spectral raster
            'output_projection' -- the machine number for the output projection
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

    # Define intermediate datasets
    mosaic_raster = os.path.splitext(spectral_grid)[0] + '_mosaic.tif'

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
    count = 1
    for raster in tile_inputs:
        output_raster = os.path.join(source_folder, os.path.split(raster)[1])
        if os.path.exists(output_raster) == 0:
            try:
                # Start timing function
                iteration_start = time.time()
                print(f'\tExtracting spectral tile {count} of {input_length}...')
                # Extract raster to mask
                extract_raster = ExtractByMask(raster, grid_raster)
                # Copy extracted raster to output
                print(f'\tSaving spectral tile {count} of {input_length}...')
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
                print('\tSpectral tile does not overlap grid...')
                print('\t----------')
        else:
            print(f'\tExtracted spectral tile {count} of {input_length} already exists...')
            print('\t----------')
        if os.path.exists(output_raster) == 1:
            input_rasters.append(output_raster)
        count += 1

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
    raster_nibble = Nibble(Raster(mosaic_raster), raster_null, 'DATA_ONLY', 'PROCESS_NODATA', '')
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
    raster_preliminary = ExtractByMask(raster_nibble, study_area)
    raster_final = ExtractByMask(raster_preliminary, grid_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Export filled raster to output
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
                                'NONE')
    # Delete mosaic raster
    if arcpy.Exists(mosaic_raster) == 1:
        arcpy.Delete_management(mosaic_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully created {os.path.split(spectral_grid)[1]}'
    return out_process
