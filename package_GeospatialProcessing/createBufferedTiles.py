# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Buffered Tiles
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Buffered Tiles" is a function that extracts, buffers, and clips a set of grids from a grid index to form individual raster tiles.
# ---------------------------------------------------------------------------

# Define a function to create buffered tiles for a grid index
def create_buffered_tiles(**kwargs):
    """
    Description: creates buffered grid rasters
    Inputs: 'tile_name' -- a field name in the grid index that stores the tile name
            'distance' -- a string representing a number and units for buffer distance
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the input grid index and a clip area
            'output_folder' -- an empty folder to store the output tiles
    Returned Value: Returns a raster dataset for each grid in grid index
    Preconditions: grid index must have been generated using create_grid_indices
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Reclassify
    from arcpy.sa import RemapRange
    import datetime
    import os
    import time

    # Parse key word argument inputs
    tile_name = kwargs['tile_name']
    distance = kwargs['distance']
    work_geodatabase = kwargs['work_geodatabase']
    grid_index = kwargs['input_array'][0]
    snap_raster = kwargs['input_array'][1]
    output_folder = kwargs['output_folder']

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of the possible cores on the machine
    arcpy.env.parallelProcessingFactor = '66%'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set the snap raster
    arcpy.env.snapRaster = snap_raster

    # Print initial status
    print(f'Extracting grid tiles from {os.path.split(grid_index)[1]}...')

    # Define fields for search cursor
    fields = ['SHAPE@', tile_name]
    # Initiate search cursor on grid index with defined fields
    with arcpy.da.SearchCursor(grid_index, fields) as cursor:
        # Iterate through each feature in the feature class
        for row in cursor:
            # Define an output and temporary raster
            buffer_feature = os.path.join(arcpy.env.workspace, 'Grid_' + row[1] + '_Buffer')
            output_grid = os.path.join(output_folder, 'Grid_' + row[1] + '.tif')

            # If tile does not exist, then create tile
            if arcpy.Exists(output_grid) == 0:
                print(f'\tProcessing grid tile {os.path.split(output_grid)[1]}...')
                iteration_start = time.time()
                # Define feature
                feature = row[0]
                # Buffer feature by user specified distance
                arcpy.analysis.Buffer(feature, buffer_feature, distance)
                # Extract snap raster to buffered tile feature
                extract_raster = ExtractByMask(snap_raster, buffer_feature)
                # Reclassify values to 1
                reclassify_raster = Reclassify(extract_raster, 'Value', RemapRange([[1,100000,1]]))
                # Copy raster to output
                arcpy.management.CopyRaster(reclassify_raster,
                                            output_grid,
                                            '',
                                            '',
                                            '0',
                                            'NONE',
                                            'NONE',
                                            '1_BIT',
                                            'NONE',
                                            'NONE',
                                            'TIFF',
                                            'None')
                # If temporary feature class exists, then delete it
                if arcpy.Exists(buffer_feature) == 1:
                    arcpy.management.Delete(buffer_feature)
                # End timing
                iteration_end = time.time()
                iteration_elapsed = int(iteration_end - iteration_start)
                iteration_success_time = datetime.datetime.now()
                # Report success
                print(
                    f'\tOutput grid {os.path.split(output_grid)[1]} completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
                print('\t----------')
            else:
                print(f'\tOutput grid {os.path.split(output_grid)[1]} already exists...')
                print('\t----------')

    # Return final status
    out_process = 'Completed creation of grid tiles.'
    return out_process
