# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Select features by location
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Select features by location" selects features by intersection with a polygon feature class and exports the results as a new feature class.
# ---------------------------------------------------------------------------

# Define a function to select features by locations and save results as new feature class
def select_location(**kwargs):
    """
    Description: selects and exports features by location
    Inputs: 'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the study area polygon (must be first) and the target feature class
            'output_folder' -- an empty folder to store the output tiles
    Returned Value: Returns a raster dataset for each grid in grid index
    Preconditions: grid index must have been generated using create_grid_indices
    """

    # Import packages
    import arcpy
    import datetime
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    study_polygon = kwargs['input_array'][0]
    target_features = kwargs['input_array'][1]
    output_features = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of the possible cores on the machine
    arcpy.env.parallelProcessingFactor = '66%'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # If output feature class does not already exist, select and export features
    if arcpy.Exists(output_features) == 0:
        # Select and export features
        print('\tSelecting and exporting features...')
        iteration_start = time.time()
        # Create layer with target features
        target_layer = 'target_lyr'
        arcpy.management.MakeFeatureLayer(target_features, target_layer)
        # Select features by intersection with study area polygon
        arcpy.management.SelectLayerByLocation(target_layer,
                                               'INTERSECT',
                                               study_polygon,
                                               '',
                                               'NEW_SELECTION',
                                               'NOT_INVERT')
        # Copy selected features to new feature class
        arcpy.management.CopyFeatures(target_layer, output_features)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
        out_process = f'Successfully created new feature class with selected features.'
        return out_process
    # If output feature class already exists return message.
    else:
        outprocess = 'Output feature class already exists.'
        return outprocess
