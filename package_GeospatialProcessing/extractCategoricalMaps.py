# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Categorical Maps to Model Results
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Extract Categorical Maps to Model Results" is a function that extracts the class values of the NLCD, the coarse classes of the Alaska Vegetation and Wetland Composite, and the fine classes of the Alaska Vegetation and Wetland Composite to a set of x and y values in a table.
# ---------------------------------------------------------------------------

# Define function to extract categorical map values to x, y points
def extract_categorical_maps(**kwargs):
    """
    Description: extracts categorical map values to a set of x and y values in a table
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_projection' -- the machine number for the input projection
            'input_array' -- an array containing the input table (must be first) and the NLCD, Coarse Classes, and Fine Classes rasters (in that order)
            'output_array' -- an array containing an output csv table for the extracted data results
    Returned Value: Returns a csv table containing the extracted data results
    Preconditions: requires results from a statistical model in csv format
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractMultiValuesToPoints
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    input_projection = kwargs['input_projection']
    input_table = kwargs['input_array'][0]
    nlcd = kwargs['input_array'][1]
    coarse = kwargs['input_array'][2]
    fine = kwargs['input_array'][3]
    minor_grid = kwargs['input_array'][4]
    ecoregions = kwargs['input_array'][5]
    output_table = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Split output table into location and name
    output_location, output_name = os.path.split(output_table)

    # Define intermediate dataset
    points_feature = os.path.join(work_geodatabase, 'points_feature')

    # Define the initial projection
    input_system = arcpy.SpatialReference(input_projection)

    # Extract raster data to points
    print(f'\tExtracting raster data to points...')
    iteration_start = time.time()
    arcpy.management.XYTableToPoint(input_table,
                                    points_feature,
                                    'POINT_X',
                                    'POINT_Y',
                                    '',
                                    input_system)
    ExtractMultiValuesToPoints(points_feature,
                               [[nlcd, 'nlcd'], [coarse, 'coarse'], [fine, 'fine'], [minor_grid, 'minor'], [ecoregions, 'ecoregion']],
                               'NONE')
    arcpy.conversion.TableToTable(points_feature,
                                  output_location,
                                  output_name)
    # Delete intermediate datasets
    if arcpy.Exists(points_feature) == 1:
        arcpy.management.Delete(points_feature)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully extracted categorical map data to points.'
    return out_process
