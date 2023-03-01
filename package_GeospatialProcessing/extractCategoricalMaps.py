# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Categorical Maps to Model Results
# Author: Timm Nawrocki
# Last Updated: 2023-02-17
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Extract Categorical Maps to Model Results" is a function that extracts the class values of the NLCD, the coarse classes of the Alaska Vegetation and Wetland Composite, and the fine classes of the Alaska Vegetation and Wetland Composite to a set of x and y values in a table.
# ---------------------------------------------------------------------------

# Define function to extract categorical map values to x, y points
def extract_categorical_maps(**kwargs):
    """
    Description: extracts categorical map values to a set of x and y values in a table
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_projection' -- the machine number for the input projection
            'input_array' -- an array containing the input table (must be first) and the NLCD, AKVWC Coarse Classes, AKVWC Fine Classes, NASA ABoVE Land Cover, and Landfire Existing Vegetation (in that order)
            'output_array' -- an array containing an output csv table for the extracted data results
    Returned Value: Returns a csv table containing the extracted data results
    Preconditions: requires results from a statistical model in csv format
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractMultiValuesToPoints
    import datetime
    import os
    import pandas as pd
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    input_projection = kwargs['input_projection']
    input_table = kwargs['input_array'][0]
    nlcd = kwargs['input_array'][1]
    coarse = kwargs['input_array'][2]
    fine = kwargs['input_array'][3]
    above = kwargs['input_array'][4]
    landfire = kwargs['input_array'][5]
    epscor = kwargs['input_array'][6]
    minor_grid = kwargs['input_array'][7]
    ecoregions = kwargs['input_array'][8]
    output_file = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

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
                               [[nlcd, 'nlcd'], [coarse, 'coarse'], [fine, 'fine'], [above, 'above'],
                                [landfire, 'landfire'], [epscor, 'epscor'], [minor_grid, 'minor'],
                                [ecoregions, 'ecoregion']],
                               'NONE')
    # Export table
    final_fields = [field.name for field in arcpy.ListFields(points_feature)
                    if field.name != arcpy.Describe(points_feature).shapeFieldName]
    output_data = pd.DataFrame(arcpy.da.TableToNumPyArray(points_feature,
                                                          final_fields,
                                                          '',
                                                          False,
                                                          -99999))
    output_data.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')
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
