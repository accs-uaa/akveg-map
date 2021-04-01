# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Partition Results
# Author: Timm Nawrocki
# Last Updated: 2021-04-01
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Partition Results" is a function that spatially partitions model validation results within a region feature class.
# ---------------------------------------------------------------------------

# Define a function to partition model validation results to a region
def partition_results(**kwargs):
    """
    Description: spatially partitions model validation results to a region feature class
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_projection' -- the machine number for the input projection
            'input_array' -- an array containing the region feature class (must be first) and a table containing the model validation results
            'output_array' -- an array containing an output csv table for the partitioned model results
    Returned Value: Returns a csv table containing the partitioned model results
    Preconditions: requires results from a statistical model in csv format
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    input_projection = kwargs['input_projection']
    region = kwargs['input_array'][0]
    input_table = kwargs['input_array'][1]
    output_table = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Split output table into location and name
    output_location, output_name = os.path.split(output_table)

    # Define intermediate datasets
    points_feature = os.path.join(work_geodatabase, 'points_feature')
    clip_feature = os.path.join(work_geodatabase, 'points_clip')

    # Define the input coordinate system
    input_system = arcpy.SpatialReference(input_projection)

    # Mosaic raster tiles to new raster
    print(f'\tPartitioning points to region...')
    iteration_start = time.time()
    arcpy.management.XYTableToPoint(input_table,
                                    points_feature,
                                    'POINT_X',
                                    'POINT_Y',
                                    '',
                                    input_system)
    arcpy.analysis.Clip(points_feature, region, clip_feature)
    arcpy.conversion.TableToTable(clip_feature, output_location, output_name)
    # Delete intermediate datasets
    if arcpy.Exists(points_feature) == 1:
        arcpy.management.Delete(points_feature)
    if arcpy.Exists(points_feature) == 1:
        arcpy.management.Delete(clip_feature)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully partitioned points to region.'
    return out_process
