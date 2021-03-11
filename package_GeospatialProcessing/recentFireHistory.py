# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Recent Fire History
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Recent Fire History" is a function that extracts fire perimeter polygons from 1990-2020 to a new feature class.
# ---------------------------------------------------------------------------

# Define a function to extract recent fire history
def recent_fire_history(**kwargs):
    """
    Description: extracts recent fire history to new feature class
    Inputs: 'work_geodatabase' -- a file geodatabase to use as a workspace
            'year_start' -- a start year in yyyy format
            'year_end' -- an end year in yyyy format
            'input_array' -- an array containing the input fire history perimeter polygons
            'output_array' -- an array containing the output recent fire history perimeter polygons
    Returned Value: Returns a feature class on disk containing the recent fire history polygons
    Preconditions: requires input fire history polygons that must be downloaded from the Alaska Fire Science Consortium
    """

    # Import packages
    import arcpy
    import datetime
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    year_start = kwargs['year_start']
    year_end = kwargs['year_end']
    fire_history = kwargs['input_array'][0]
    recent_fire = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Select years from feature class and export to new feature class
    print('\tCreating new fire feature class...')
    iteration_start = time.time()
    fire_layer = 'fire_layer'
    year_query = f'FireYear >= {year_start} And FireYear <= {year_end}'
    arcpy.management.MakeFeatureLayer(fire_history, fire_layer, year_query)
    arcpy.management.CopyFeatures(fire_layer, recent_fire)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished creating recent fire history feature class.'
    return out_process
