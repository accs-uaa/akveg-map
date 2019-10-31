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

    # Parse key word argument inputs
    distance_major = kwargs['distance_major']
    distance_minor = kwargs['distance_minor']
    total_area = kwargs['input_array'][0]
    major_grid = kwargs['output_array'][0]
    minor_grid = kwargs['output_array'][1]

    # Create intermediate datasets
    minor_grid_full = os.path.join(arcpy.env.workspace, os.path.split(minor_grid)[1] + '_Full')
    minor_grid_join = os.path.join(arcpy.env.workspace, os.path.split(minor_grid)[1] + '_Join')

    # Start timing function
    iteration_start = time.time()
    # Report initial status
    print('Creating major grid index...')
    # Create major grid
    arcpy.GridIndexFeatures_cartography(major_grid, total_area, 'INTERSECTFEATURE', 'NO_USEPAGEUNIT', '',
                                        distance_major, distance_major)
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

    # Start timing function
    iteration_start = time.time()
    # Report initial status
    print('Creating minor grid index...')
    # Create minor grid
    arcpy.GridIndexFeatures_cartography(minor_grid_full, major_grid, 'INTERSECTFEATURE', 'NO_USEPAGEUNIT', '',
                                        distance_minor, distance_minor)
    # Join major grid to minor grid
    arcpy.SpatialJoin_analysis(minor_grid_full, major_grid, minor_grid_join, 'JOIN_ONE_TO_MANY', 'KEEP_COMMON', '',
                               'WITHIN')
    arcpy.AddField_management(minor_grid_join, 'Minor', 'TEXT')
    arcpy.CalculateField_management(minor_grid_join, 'Minor', '!Major! + "-" + str(!PageNumber!)')
    arcpy.DeleteField_management(minor_grid_join,
                                 ['PageName', 'PageNumber', 'Join_Count', 'TARGET_FID', 'JOIN_FID', 'Shape_Length_1',
                                  'Shape_Area_1'])
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Finished minor grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Start timing function
    iteration_start = time.time()
    # Report initial status
    print('Clipping minor grid index to total area...')
    # Clip minor grid to total area
    arcpy.Clip_analysis(minor_grid_join, total_area, minor_grid)
    arcpy.Delete_management([minor_grid_full, minor_grid_join])
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Finished clipping minor grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    outprocess = 'Successfully created major and minor grid indices.'
    return outprocess
