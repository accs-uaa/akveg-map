# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Grid Indices
# Author: Timm Nawrocki
# Last Updated: 2020-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Grid Indices" is a function that creates a major and minor grid index from a study area.
# ---------------------------------------------------------------------------

# Define function to create grid indices
def create_grid_indices(**kwargs):
    """
    Description: creates a major and minor grid index from a study area
    Inputs: 'distance_major' -- a string representing an integer distance and units for the major grid
            'distance_minor' -- a string representing an integer distance and units for the minor grid
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the total area
            'output_array' -- an array containing the major grid and minor grid
    Returned Value: Returns a feature class
    Preconditions: an area of interest feature class must be manually generated to define grid extent
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    distance_major = kwargs['distance_major']
    distance_minor = kwargs['distance_minor']
    work_geodatabase = kwargs['work_geodatabase']
    total_area = kwargs['input_array'][0]
    major_grid = kwargs['output_array'][0]
    minor_grid = kwargs['output_array'][1]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of the possible cores on the machine
    arcpy.env.parallelProcessingFactor = '66%'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Create intermediate datasets
    minor_grid_full = os.path.join(work_geodatabase, os.path.split(minor_grid)[1] + '_Full')
    minor_grid_join = os.path.join(work_geodatabase, os.path.split(minor_grid)[1] + '_Join')

    # If major grid does not already exist, then create major grid
    if arcpy.Exists(major_grid) == 0:
        # Create major grid
        print('\tCreating major grid index...')
        iteration_start = time.time()
        arcpy.cartography.GridIndexFeatures(major_grid, total_area, 'INTERSECTFEATURE', 'NO_USEPAGEUNIT', '', distance_major, distance_major)
        arcpy.management.AddField(major_grid, 'Major', 'TEXT')
        arcpy.management.CalculateField(major_grid, 'Major', '!PageName!')
        arcpy.managment.DeleteField(major_grid, ['PageName', 'PageNumber'])
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tFinished major grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print('\tMajor grid already exists...')

    # If minor grid does not already exist, then create minor grid
    if arcpy.Exists(minor_grid) == 0:
        # Create minor grid
        print('\tCreating minor grid index...')
        iteration_start = time.time()
        # Create minor grid
        arcpy.cartography.GridIndexFeatures(minor_grid_full, major_grid, 'INTERSECTFEATURE', 'NO_USEPAGEUNIT', '', distance_minor, distance_minor)
        # Join major grid to minor grid
        arcpy.analysis.SpatialJoin(minor_grid_full, major_grid, minor_grid_join, 'JOIN_ONE_TO_MANY', 'KEEP_COMMON', '', 'WITHIN')
        arcpy.analysis.SpatialJoin(minor_grid_join, total_area, minor_grid, 'JOIN_ONE_TO_MANY', 'KEEP_COMMON', '', 'INTERSECT')
        arcpy.management.AddField(minor_grid, 'Minor', 'TEXT')
        arcpy.management.CalculateField(minor_grid, 'Minor', '!Major! + "_" + str(!PageNumber!)')
        arcpy.management.DeleteField(minor_grid, ['PageName', 'PageNumber', 'Join_Count', 'Join_Count_1', 'TARGET_FID', 'TARGET_FID_1', 'JOIN_FID', 'JOIN_FID_1', 'Shape_Length_1', 'Shape_Area_1', 'Shape_Length_12', 'Shape_Area_12'])
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tFinished minor grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')

        # Remove intermediate datasets
        arcpy.management.Delete(minor_grid_full)
        arcpy.management.Delete(minor_grid_join)

    else:
        print('\tMinor grid already exists...')

    outprocess = 'Successfully created major and minor grid indices.'
    return outprocess
