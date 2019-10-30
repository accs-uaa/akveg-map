# Define a function to create buffered tiles for a grid index
def create_buffered_tiles(**kwargs):
    """
    Description: creates a DEM from individual DEM tiles
    Inputs: 'tile_name' -- a field name in the grid index that stores the tile name
            'distance' -- a string representing a number and units for buffer distance
            'input_array' -- an array containing the input grid index and a clip area
            'output_geodatabase' -- an empty geodatabase to store the output tiles
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    tile_name = kwargs['tile_name']
    distance = kwargs['distance']
    grid_index = kwargs['input_array'][0]
    clip_area = kwargs['input_array'][1]
    output_geodatabase = kwargs['output_geodatabase']

    # Print initial status
    print(f'Extracting grid tiles from {os.path.split(grid_index)[1]}...')

    # Define fields for search cursor
    fields = ['SHAPE@', tile_name]
    # Initiate search cursor on grid index with defined fields
    with arcpy.da.SearchCursor(grid_index, fields) as cursor:
        # Iterate through each feature in the feature class
        for row in cursor:
            # Define an output and temporary feature class
            output_grid = os.path.join(output_geodatabase, 'Grid_' + row[1])
            temporary_grid = os.path.join(output_geodatabase, 'Grid_' + row[1] + '_Buffer')
            print(f'\tProcessing grid tile {os.path.split(output_grid)[1]}...')
            # If tile does not exist, then create tile
            if arcpy.Exists(output_grid) == 0:
                # Start timing function
                iteration_start = time.time()
                # Define feature
                feature = row[0]
                # Buffer feature by user specified distance
                arcpy.Buffer_analysis(feature, temporary_grid, distance, 'FULL', 'ROUND', 'NONE', '', 'PLANAR')
                # Clip buffered feature to clip area
                arcpy.Clip_analysis(temporary_grid, clip_area, output_grid)
                # If temporary feature class exists, then delete it
                if arcpy.Exists(temporary_grid) == 1:
                    arcpy.Delete_management(temporary_grid)
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