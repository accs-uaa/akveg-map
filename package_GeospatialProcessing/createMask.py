# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create mask
# Author: Timm Nawrocki
# Last Updated: 2021-03-12
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create mask" is a function that clips of feature class with an optional selection query.
# ---------------------------------------------------------------------------

# Define a function to create a mask
def create_mask(**kwargs):
    """
    Description: creates a mask feature class
    Inputs: 'input_projection' -- the machine number for the input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'selection_query' -- query to select subset of mask features by attributes (optional)
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the study area feature class (must be first) and the input feature class (must be second)
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a feature class on disk containing the output mask
    Preconditions: requires existing feature classes on disk
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
    selection_query = kwargs['selection_query']
    work_geodatabase = kwargs['work_geodatabase']
    study_area = kwargs['input_array'][0]
    input_feature = kwargs['input_array'][1]
    output_feature = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "75%"

    # Define coordinate systems
    input_system = arcpy.SpatialReference(input_projection)
    output_system = arcpy.SpatialReference(output_projection)

    # Define intermediate datasets
    mask_clipped = os.path.join(work_geodatabase, 'mask_clipped')
    mask_selected = os.path.join(work_geodatabase, 'mask_selected')

    # Clip input feature class to study area
    print(f'\tClipping input feature class...')
    iteration_start = time.time()
    arcpy.analysis.Clip(input_feature, study_area, mask_clipped)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Project clipped feature to output coordinate system
    print('\tProjecting mask to output coordinate system...')
    iteration_start = time.time()
    # Select features and project if selection query is not null
    if selection_query != '':
        selection_layer = 'selection_layer'
        arcpy.management.MakeFeatureLayer(mask_clipped, selection_layer, selection_query)
        arcpy.management.CopyFeatures(selection_layer, mask_selected)
        # Project features
        arcpy.management.Project(mask_selected,
                                 output_feature,
                                 output_system,
                                 geographic_transformation,
                                 input_system,
                                 'NO_PRESERVE_SHAPE'
                                 )
    else:
        # Project features
        arcpy.management.Project(mask_clipped,
                                 output_feature,
                                 output_system,
                                 geographic_transformation,
                                 input_system,
                                 'NO_PRESERVE_SHAPE'
                                 )
    # Delete intermediate datasets
    if arcpy.Exists(mask_clipped) == 1:
        arcpy.management.Delete(mask_clipped)
    if arcpy.Exists(mask_selected) == 1:
        arcpy.management.Delete(mask_selected)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    # Return output message
    out_process = 'Successfully created mask feature class.'
    return out_process
