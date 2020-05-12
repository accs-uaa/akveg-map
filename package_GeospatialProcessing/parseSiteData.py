# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse Site Data
# Author: Timm Nawrocki
# Last Updated: 2020-05-07
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Parse Site Data" is a function that extracts a set of sampling points within a polygon.
# ---------------------------------------------------------------------------

# Define a function to extract site data to a polygon
def parse_site_data(**kwargs):
    """
    Description: clips a set of sampling points to a polygon
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'grid_name' -- the name of a grid from a grid polygon feature class
            'input_array' -- an array containing the site point feature class (must be first) and the major grid feature class
            'output_array' -- an array that contains the output site point feature class
    Returned Value: Returns a point shapefile for each grid in the Major Grid for which sample points exist
    Preconditions: the set of site points must be created using the format_site_data function.
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    grid_name = kwargs['grid_name']
    sites_formatted = kwargs['input_array'][0]
    grid_major = kwargs['input_array'][1]
    output_shapefile = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Clip point features to polygon feature
    print('\tClipping points to grid polygon...')
    iteration_start = time.time()
    # Create a new feature class of plot locations that will be buffered
    arcpy.MakeFeatureLayer_management(grid_major,
                                      'grid_layer',
                                      f'Major = \'{grid_name}\'')
    # Clip points to selected polygon
    arcpy.Clip_analysis(sites_formatted,
                        'grid_layer',
                        output_shapefile)
    # Check if output is empty
    feature_count = int(arcpy.GetCount_management(output_shapefile)[0])
    print(f'\tGrid {grid_name} contains {str(feature_count)} points...')
    if feature_count == 0:
        arcpy.Delete_management(output_shapefile)
        print(f'\tRemoved empty feature class for Grid {grid_name}...')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    if feature_count == 0:
        out_process = f'No data available for Grid {grid_name}.'
    else:
        out_process = f'Successfully parsed site data to Grid {grid_name}.'
    return out_process