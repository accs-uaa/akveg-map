# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Recent Fire History
# Author: Timm Nawrocki
# Last Updated: 2020-06-02
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Recent Fire History" is a function that extracts fire perimeter polygons from 2000-2019 to a new feature class.
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
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    fire_history = kwargs['input_array'][0]
    recent_fire = kwargs['output_array'][0]

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Select years from feature class and export to new feature class
    iteration_start = time.time()
    print('\tCreating new fire feature class...')
    fire_layer = 'fire_layer'
    year_query = "FIREYEAR IN ('2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019')"
    arcpy.MakeFeatureLayer_management(fire_history, fire_layer, year_query)
    arcpy.CopyFeatures_management(fire_layer, recent_fire)
    arcpy.AddField_management(recent_fire, 'YEAR', 'SHORT', '', '', '', '', 'NULLABLE', 'NON_REQUIRED', '')
    arcpy.CalculateField_management(recent_fire, 'YEAR', 'int(!FIREYEAR!)', 'PYTHON3')
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