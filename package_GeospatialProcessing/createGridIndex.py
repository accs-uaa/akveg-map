# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Grid Indices
# Author: Timm Nawrocki
# Last Updated: 2020-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Grid Indices" is a function that creates a major and minor grid index from a study area.
# ---------------------------------------------------------------------------

# Define function to create grid indices
def create_grid_index(**kwargs):
    """
    Description: creates a major and minor grid index from a study area
    Inputs: 'distance' -- a string representing an integer distance and units
            'grid_field' -- a string representing the name of the field to store grid information
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the total area feature class and an optional spatial join feature class
            'output_array' -- an array containing the grid index
    Returned Value: Returns feature class containing the full grid index
    Preconditions: an area of interest feature class must be manually generated to define grid extent
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    distance = kwargs['distance']
    grid_field = kwargs['grid_field']
    work_geodatabase = kwargs['work_geodatabase']
    input_feature = kwargs['input_array'][0]
    if len(kwargs['input_array']) > 1:
        join_feature = kwargs['input_array'][1]
    else:
        join_feature = ''
    grid_output = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of the possible cores on the machine
    arcpy.env.parallelProcessingFactor = '66%'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Create intermediate datasets
    grid_intermediate = os.path.join(work_geodatabase, os.path.split(grid_output)[1] + '_Int')

    # Create grid index
    print(f'\tCreating grid index at {distance}...')
    iteration_start = time.time()
    arcpy.cartography.GridIndexFeatures(grid_intermediate,
                                        input_feature,
                                        'INTERSECTFEATURE',
                                        'NO_USEPAGEUNIT',
                                        '',
                                        distance,
                                        distance)
    arcpy.management.AddField(grid_intermediate, grid_field, 'TEXT')
    arcpy.management.CalculateField(grid_intermediate, grid_field, '!PageName!')
    arcpy.management.DeleteField(grid_intermediate, ['PageName', 'PageNumber'])
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tFinished creating grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # If spatial join feature is defined
    if join_feature != '':
        # Join grid index to feature
        print('\tJoining grid index to feature...')
        iteration_start = time.time()
        arcpy.analysis.SpatialJoin(grid_intermediate,
                                   join_feature,
                                   grid_output,
                                   'JOIN_ONE_TO_MANY',
                                   'KEEP_COMMON',
                                   '',
                                   'WITHIN')
        arcpy.management.DeleteField(grid_output, ['Join_Count', 'TARGET_FID', 'JOIN_FID', 'Shape_Length_1', 'Shape_Area_1'])
        if grid_field == 'grid_minor':
            arcpy.management.DeleteField(grid_output, ['grid_minor'])
            arcpy.management.AddField(grid_intermediate, grid_field, 'TEXT')
            code_block = """def get_grid_name(objectID, grid_major):
    if objectID < 10:
        grid_name = grid_major + "_0000" + str(objectID)
    elif objectID < 100:
        grid_name = grid_major + "_000" + str(objectID)
    elif objectID < 1000:
        grid_name = grid_major + "_00" + str(objectID)
    elif objectID < 10000:
        grid_name = grid_major + "_0" + str(objectID)
    else:
        grid_name = grid_major + "_" + str(objectID)
    return grid_name"""
            arcpy.management.CalculateField(grid_output,
                                            grid_field,
                                            'get_grid_name(!OBJECTID!, !grid_major!)',
                                            'PYTHON3',
                                            code_block)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tFinished grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print('\tExporting grid index...')
        iteration_start = time.time()
        arcpy.management.CopyFeatures(grid_intermediate, grid_output)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tFinished grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')

    # Remove intermediate datasets
    arcpy.management.Delete(grid_intermediate)

    # Return success message
    outprocess = 'Successfully created major and minor grid indices.'
    return outprocess
