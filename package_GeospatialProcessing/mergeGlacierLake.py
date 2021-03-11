# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge glaciers and lakes
# Author: Timm Nawrocki
# Last Updated: 2021-03-08
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Merge glaciers and lakes" is a function that lakes from the NHD Waterbodies with Glaciers.
# ---------------------------------------------------------------------------

# Define a function to merge lakes and glaciers polygons
def merge_glaciers_lakes(**kwargs):
    """
    Description: merges lake polygons from NHD Waterbodies with glacier polygons from GLIMS
    Inputs: 'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the study area feature class (must be first), the NHD Waterbodies feature class (must be second), and the GLIMS feature class (must be last)
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a feature class on disk containing the merged lakes and glaciers mask
    Preconditions: requires downloaded National Hydrography Dataset for Alaska and GLIMS
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    study_area = kwargs['input_array'][0]
    waterbodies = kwargs['input_array'][1]
    glaciers = kwargs['input_array'][2]
    lake_glacier = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "75%"

    # Define coordinate systems
    wgs84_system = arcpy.SpatialReference(4326)
    nad83_system = arcpy.SpatialReference(4269)
    akalb_system = arcpy.SpatialReference(3338)

    # Define intermediate datasets
    waterbodies_beringia = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Waterbodies_NAD83')
    glaciers_beringia = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Glaciers_WGS84')
    waterbodies_akalb = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Waterbodies')
    glaciers_akalb = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Glaciers')
    lakes_akalb = os.path.join(work_geodatabase, 'NorthAmericanBeringia_Lakes')

    # Output message of processing stage
    print(f'\tClipping input datasets to study area...')

    # Start timing function
    iteration_start = time.time()
    # Clip input waterbodies to study area
    print(f'\t\tClipping input waterbodies...')
    arcpy.analysis.Clip(waterbodies, study_area, waterbodies_beringia)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')

    # Start timing function
    iteration_start = time.time()
    # Clip input glaciers to study area
    print(f'\t\tClipping input glaciers...')
    arcpy.analysis.Clip(glaciers, study_area, glaciers_beringia)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')

    # Output message of processing stage
    print('\t----------')
    print(f'\tProjecting clipped datasets to AKALB...')

    # Start timing function
    iteration_start = time.time()
    # Project waterbodies to AKALB
    print('\t\tProjecting waterbodies to AKALB...')
    arcpy.management.Project(waterbodies_beringia,
                             waterbodies_akalb,
                             akalb_system,
                             '',
                             nad83_system,
                             'NO_PRESERVE_SHAPE'
                             )
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')

    # Start timing function
    iteration_start = time.time()
    # Project glaciers to AKALB
    print('\t\tProjecting glaciers to AKALB...')
    arcpy.management.Project(glaciers_beringia,
                             glaciers_akalb,
                             akalb_system,
                             'WGS_1984_(ITRF00)_To_NAD_1983',
                             wgs84_system,
                             'NO_PRESERVE_SHAPE'
                             )
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')

    # End processing stage
    print('\t----------')

    # Start timing function
    iteration_start = time.time()
    # Select lakes from waterbodies
    print('\tSelecting lakes from waterbodies...')
    waterbodies_layer = 'waterbodies_layer'
    arcpy.management.MakeFeatureLayer(waterbodies_akalb, waterbodies_layer)
    arcpy.management.SelectLayerByAttribute(waterbodies_layer,
                                            'NEW_SELECTION',
                                            'FType = 390',
                                            'NON_INVERT'
                                            )
    arcpy.management.CopyFeatures(waterbodies_layer, lakes_akalb)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Start timing function
    iteration_start = time.time()
    # Merge lake and glacier features
    print('\tMerging lake and glacier features...')
    # Merge lakes and glaciers
    arcpy.management.Merge([lakes_akalb, glaciers_akalb], lake_glacier)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Delete intermediate datasets
    if arcpy.Exists(waterbodies_beringia) == 1:
        arcpy.management.Delete(waterbodies_beringia)
    if arcpy.Exists(glaciers_beringia) == 1:
        arcpy.management.Delete(glaciers_beringia)
    if arcpy.Exists(waterbodies_akalb) == 1:
        arcpy.management.Delete(waterbodies_akalb)

    # Return output message
    out_process = 'Successfully created lake-glacier mask dataset.'
    return out_process
