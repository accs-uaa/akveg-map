# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Grid Indices
# Author: Timm Nawrocki
# Last Updated: 2019-10-30
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Grid Indices" is a function that creates a major and minor grid index from a study area.
# ---------------------------------------------------------------------------

# Define function to create grid indices
def create_grid_indices(**kwargs):
    """
    Description: creates a major and minor grid index from a study area
    Inputs: 'distance_major' -- a string representing an integer distance and units for the major grid
            'distance_minor' -- a string representing an integer distance and units for the minor grid
            'input_array' -- an array containing the total area
            'output_array' -- an array containing the major grid and minor grid
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of the possible cores on the machine
    arcpy.env.parallelProcessingFactor = '66%'

    # Parse key word argument inputs
    distance_major = kwargs['distance_major']
    distance_minor = kwargs['distance_minor']
    total_area = kwargs['input_array'][0]
    major_grid = kwargs['output_array'][0]
    minor_grid = kwargs['output_array'][1]

    # Create intermediate datasets
    minor_grid_full = os.path.join(arcpy.env.workspace, os.path.split(minor_grid)[1] + '_Full')
    minor_grid_join = os.path.join(arcpy.env.workspace, os.path.split(minor_grid)[1] + '_Join')

    # If major grid does not already exist, then create major grid
    if arcpy.Exists(major_grid) == 0:
        # Start timing function
        iteration_start = time.time()
        # Report initial status
        print('Creating major grid index...')
        # Create major grid
        arcpy.GridIndexFeatures_cartography(major_grid, total_area, 'INTERSECTFEATURE', 'NO_USEPAGEUNIT', '', distance_major, distance_major)
        arcpy.AddField_management(major_grid, 'Major', 'TEXT')
        arcpy.CalculateField_management(major_grid, 'Major', '!PageName!')
        arcpy.DeleteField_management(major_grid, ['PageName', 'PageNumber'])
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'Finished major grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('----------')
    else:
        print('Major grid already exists...')

    # If minor grid does not already exist, then create minor grid
    if arcpy.Exists(minor_grid) == 0:
        # Start timing function
        iteration_start = time.time()
        # Report initial status
        print('Creating minor grid index...')
        # Create minor grid
        arcpy.GridIndexFeatures_cartography(minor_grid_full, major_grid, 'INTERSECTFEATURE', 'NO_USEPAGEUNIT', '', distance_minor, distance_minor)
        # Join major grid to minor grid
        arcpy.SpatialJoin_analysis(minor_grid_full, major_grid, minor_grid_join, 'JOIN_ONE_TO_MANY', 'KEEP_COMMON', '', 'WITHIN')
        arcpy.SpatialJoin_analysis(minor_grid_join, total_area, minor_grid, 'JOIN_ONE_TO_MANY', 'KEEP_COMMON', '', 'INTERSECT')
        arcpy.AddField_management(minor_grid, 'Minor', 'TEXT')
        arcpy.CalculateField_management(minor_grid, 'Minor', '!Major! + "_" + str(!PageNumber!)')
        arcpy.DeleteField_management(minor_grid, ['PageName', 'PageNumber', 'Join_Count', 'Join_Count_1', 'TARGET_FID', 'TARGET_FID_1', 'JOIN_FID', 'JOIN_FID_1', 'Shape_Length_1', 'Shape_Area_1', 'Shape_Length_12', 'Shape_Area_12'])
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'Finished minor grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('----------')

        # Remove intermediate datasets
        arcpy.Delete_management(minor_grid_full)
        arcpy.Delete_management(minor_grid_join)

    else:
        print('Minor grid already exists...')

    outprocess = 'Successfully created major and minor grid indices.'
    return outprocess
