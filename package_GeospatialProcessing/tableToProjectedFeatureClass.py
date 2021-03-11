# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Table to Projected Feature Class
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Table to Projected Feature Class" is a function that converts a csv table containing point coordinates in a geographic coordinate system to feature class with a projected coordinate system and clipped to a study area.
# ---------------------------------------------------------------------------

# Define a function to convert a csv table of point coordinates to a projected point feature class
def table_to_feature_projected(**kwargs):
    """
    Description: creates, reprojects, and clips a point feature class from a csv table
    Inputs: 'input_projection' -- the machine number for the input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the study area feature class (must be first) and the csv table of points (must be second)
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a point feature class of the projected and clipped input table
    Preconditions: the initial site table must exist as a csv file
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transformation = kwargs['geographic_transformation']
    work_geodatabase = kwargs['work_geodatabase']
    study_area = kwargs['input_array'][0]
    input_table = kwargs['input_array'][1]
    output_feature = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Define the input and output coordinate systems
    input_system = arcpy.SpatialReference(input_projection)
    output_system = arcpy.SpatialReference(output_projection)

    # Define intermediate datasets
    table_initial = os.path.join(work_geodatabase, 'table_initial')
    table_projected = os.path.join(work_geodatabase, 'table_projected')

    # Convert csv table to a point feature class and project
    print('\tConverting csv table to point feature class and projecting...')
    iteration_start = time.time()
    arcpy.management.XYTableToPoint(input_table,
                                    table_initial,
                                    'longitude',
                                    'latitude',
                                    '',
                                    input_system)
    arcpy.management.Project(table_initial,
                             table_projected,
                             output_system,
                             geographic_transformation,
                             input_system,
                             'NO_PRESERVE_SHAPE')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Clip projected points to study area
    print('\tClipping points to study area...')
    iteration_start = time.time()
    arcpy.analysis.Clip(table_projected,
                        study_area,
                        output_feature)
    # Add XY coordinates
    arcpy.management.AddXY(output_feature)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished converting table to point feature class.'
    return out_process
