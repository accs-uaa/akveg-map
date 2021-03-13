# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge Sites
# Author: Timm Nawrocki
# Last Updated: 2021-03-12
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Merge Sites" is a function that merges observation sites with synthetic absence sites.
# ---------------------------------------------------------------------------

# Define a function to merge sites
def merge_sites(**kwargs):
    """
    Description: merges site point feature classes
    Inputs: 'output_fields' -- an array of column names to be selected into the output table
            'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the site feature classes to be merged
            'output_array' -- an array containing the output sites feature class and excel file
    Returned Value: Returns a point feature class of merged sites
    Preconditions: must have a database sites feature class and generated absence feature classes
    """

    # Import packages
    import arcpy
    import datetime
    from package_GeospatialProcessing import feature_to_csv
    import time

    # Parse key word argument inputs
    output_fields = kwargs['output_fields']
    work_geodatabase = kwargs['work_geodatabase']
    input_array = kwargs['input_array']
    output_feature = kwargs['output_array'][0]
    output_file = kwargs['output_array'][1]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Merge site features
    print('\tMerging site feature classes...')
    iteration_start = time.time()
    arcpy.management.Merge(input_array,
                           output_feature)
    # Export merged sites as csv table
    print('\tExporting site table to csv...')
    feature_to_csv(output_feature, output_fields, output_file)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished merging sites.'
    return out_process
