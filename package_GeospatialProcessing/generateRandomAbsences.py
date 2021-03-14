# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate Random Absences
# Author: Timm Nawrocki
# Last Updated: 2021-03-11
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Random Absences" is a function that creates a set of random absences within a mask layer with options to select or remove parts of the mask.
# ---------------------------------------------------------------------------

# Define a function to generate random absences
def generate_random_absences(**kwargs):
    """
    Description: generates a set of random absences within a modified mask layer
    Inputs: 'number_points' -- the number of random points to be generated
            'minimum_distance' -- the minimum distance allowable between points
            'site_prefix' -- unique alphanumeric string that will prepend object id to form point site code
            'initial_project' -- project name to store for absence set
            'selection_query' -- query to select subset of mask feature by attributes (optional)
            'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the mask feature (must be first) any number of additional feature classes to be erased from the mask
            'output_array' -- an array containing the output random absences feature class
    Returned Value: Returns a point feature class of random absences
    Preconditions: must have a database sites feature class from the table_to_feature_projected function
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    number_points = kwargs['number_points']
    minimum_distance = kwargs['minimum_distance']
    site_prefix = kwargs['site_prefix']
    initial_project = kwargs['initial_project']
    selection_query = kwargs['selection_query']
    work_geodatabase = kwargs['work_geodatabase']
    erase_features = kwargs['input_array']
    mask_feature = erase_features.pop(0)
    output_feature = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Define intermediate datasets
    mask_selected = os.path.join(work_geodatabase, 'mask_selected')
    mask_dissolve = os.path.join(work_geodatabase, 'mask_dissolved')
    mask_buffer = os.path.join(work_geodatabase, 'mask_buffer')
    mask_final = os.path.join(work_geodatabase, 'mask_final')

    # Inverse buffer the mask feature
    print('\tInverse buffering mask feature...')
    iteration_start = time.time()
    if selection_query != '':
        selection_layer = 'selection_layer'
        arcpy.management.MakeFeatureLayer(mask_feature, selection_layer, selection_query)
        arcpy.management.CopyFeatures(selection_layer, mask_selected)
        arcpy.analysis.Buffer(mask_selected,
                              mask_buffer,
                              '-250 Meters',
                              'FULL',
                              'ROUND',
                              'NONE',
                              '',
                              'PLANAR')
    else:
        arcpy.analysis.Buffer(mask_feature,
                              mask_buffer,
                              '-250 Meters',
                              'FULL',
                              'ROUND',
                              'NONE',
                              '',
                              'PLANAR')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Dissolve the buffered mask feature
    print('\tDissolving the buffered mask feature...')
    iteration_start = time.time()
    arcpy.management.RepairGeometry(mask_buffer,
                                    'DELETE_NULL',
                                    'ESRI')
    arcpy.management.Dissolve(mask_buffer,
                              mask_dissolve,
                              '',
                              '',
                              'MULTI_PART',
                              'DISSOLVE_LINES')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Erase features from dissolved mask if erase features are greater than zero
    erase_length = len(erase_features)
    if erase_length > 0:
        # Iterate through erase features to erase from mask
        count = 1
        for erase_feature in erase_features:
            # Define intermediate erase features
            buffered_eraser = os.path.join(work_geodatabase, 'buffered_eraser')
            mask_erase = os.path.join(work_geodatabase, f'mask_erased_{count}')
            # Buffer the erase features by 500 m
            print(f'\tErasing feature {count} of {erase_length} from mask...')
            iteration_start = time.time()
            arcpy.analysis.Buffer(erase_feature,
                                  buffered_eraser,
                                  '500 Meters',
                                  'FULL',
                                  'ROUND',
                                  'NONE',
                                  '',
                                  'PLANAR')
            # Erase features from the dissolved mask or from previous erased mask
            if count == 1:
                # Erase features from buffered mask
                arcpy.analysis.Erase(mask_dissolve,
                                     buffered_eraser,
                                     mask_erase,
                                     '')
            else:
                # Identify previous erased mask
                previous_erase = os.path.join(work_geodatabase, f'mask_erased_{count - 1}')
                arcpy.analysis.Erase(previous_erase,
                                     buffered_eraser,
                                     mask_erase,
                                     '')
                # Delete previous mask if it exists
                if arcpy.Exists(previous_erase) == 1:
                    arcpy.management.Delete(previous_erase)
            # Delete buffered erase feature if it exists
            if arcpy.Exists(buffered_eraser) == 1:
                arcpy.management.Delete(buffered_eraser)
            # End timing
            iteration_end = time.time()
            iteration_elapsed = int(iteration_end - iteration_start)
            iteration_success_time = datetime.datetime.now()
            # Report success
            print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
            print('\t----------')
            # Increase counter
            count += 1

        # Copy last erase to final mask
        print('\tPreparing final mask...')
        iteration_start = time.time()
        arcpy.management.CopyFeatures(mask_erase, mask_final)
        # Delete erase mask
        if arcpy.Exists(mask_erase) == 1:
            arcpy.management.Delete(mask_erase)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')

    else:
        # Copy dissolved mask to final mask
        print('\tPreparing final mask...')
        iteration_start = time.time()
        arcpy.management.CopyFeatures(mask_dissolve, mask_final)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')

    # Generate random points within mask
    print('\tGenerating random points within final mask feature...')
    iteration_start = time.time()
    output_path, output_name = os.path.split(output_feature)
    arcpy.management.CreateRandomPoints(output_path,
                                        output_name,
                                        mask_final,
                                        '',
                                        number_points,
                                        minimum_distance,
                                        'POINT')
    # Add site fields to output
    arcpy.management.AddField(output_feature, 'site_code', 'TEXT')
    arcpy.management.CalculateField(output_feature, 'site_code', f'"{site_prefix}" + "_" + str(!OID!)')
    arcpy.management.AddField(output_feature, 'initial_project', 'TEXT')
    arcpy.management.CalculateField(output_feature, 'initial_project', f'"{initial_project}"')
    arcpy.management.AddField(output_feature, 'perspective', 'TEXT')
    arcpy.management.CalculateField(output_feature, 'perspective', '"generated"')
    arcpy.management.AddField(output_feature, 'cover_method', 'TEXT')
    arcpy.management.CalculateField(output_feature, 'cover_method', '"generated"')
    arcpy.management.AddField(output_feature, 'scope_vascular', 'TEXT')
    arcpy.management.CalculateField(output_feature, 'scope_vascular', '"none"')
    arcpy.management.AddField(output_feature, 'scope_bryophyte', 'TEXT')
    arcpy.management.CalculateField(output_feature, 'scope_bryophyte', '"none"')
    arcpy.management.AddField(output_feature, 'scope_lichen', 'TEXT')
    arcpy.management.CalculateField(output_feature, 'scope_lichen', '"none"')
    arcpy.management.AddField(output_feature, 'plot_dimensions', 'TEXT')
    arcpy.management.CalculateField(output_feature, 'plot_dimensions', '"20 radius"')
    arcpy.management.AddXY(output_feature)
    # Delete intermediate datasets if they exist
    if arcpy.Exists(mask_selected) == 1:
        arcpy.management.Delete(mask_selected)
    if arcpy.Exists(mask_dissolve) == 1:
        arcpy.management.Delete(mask_dissolve)
    if arcpy.Exists(mask_final) == 1:
        arcpy.management.Delete(mask_final)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Finished generating random points.'
    return out_process
