# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Format Site Data
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Format Site Data" is a function that creates a set of sampling points for feature extraction from plot locations and sizes.
# ---------------------------------------------------------------------------

# Define a function to format site data
def format_site_data(**kwargs):
    """
    Description: creates a set of sampling points aligned with Area of Interest from points and buffered points
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the site feature class (must be first) and the area of interest raster (must be second)
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a point feature class with selected raster points labeled by site code
    Preconditions: the initial site feature class must be generated from the table_to_feature_projected function
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    work_geodatabase = kwargs['work_geodatabase']
    site_feature = kwargs['input_array'][0]
    area_of_interest = kwargs['input_array'][1]
    sites_formatted = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Set snap raster
    arcpy.env.snapRaster = area_of_interest

    # Define intermediate datasets
    sites_buffer_distance = os.path.join(work_geodatabase, 'sites_buffer_distance')
    sites_selected_point = os.path.join(work_geodatabase, 'sites_selected_points')
    sites_selected_toBuffer = os.path.join(work_geodatabase, 'sites_selected_toBuffer')
    sites_selected_buffered = os.path.join(work_geodatabase, 'sites_selected_buffered')
    sites_selected_raster = os.path.join(work_geodatabase, 'sites_selected_raster')
    sites_selected_converted = os.path.join(work_geodatabase, 'sites_selected_converted')

    # Add a new field for the buffer distance and calculate buffer distance from plot dimensions for a copy of the feature class
    print('\tSelecting plots for analysis based on plot geometry...')
    iteration_start = time.time()
    arcpy.management.CopyFeatures(site_feature, sites_buffer_distance)
    codeblock = """def set_buffer_distance(plot_dimensions):
    if (plot_dimensions == '10×10'
    or plot_dimensions == '5 radius'
    or plot_dimensions == '8×10'
    or plot_dimensions == '8×12'
    or plot_dimensions == '8×8'):
        return 1
    elif (plot_dimensions == '10 radius'
    or plot_dimensions == '8 radius'
    or plot_dimensions == '20×20'
    or plot_dimensions == '15 radius'
    or plot_dimensions == '30×30'
    or plot_dimensions == '20 radius'):
        return 15
    elif plot_dimensions == '23 radius':
        return 18
    elif plot_dimensions == '30 radius':
        return 25
    elif plot_dimensions == '34.7 radius':
        return 30
    else:
        return 0"""
    arcpy.management.AddField(sites_buffer_distance,
                              'buffer_distance',
                              'SHORT')
    arcpy.management.CalculateField(sites_buffer_distance,
                                    'buffer_distance',
                                    'set_buffer_distance(!plotDimensions!)',
                                    'PYTHON3',
                                    codeblock)
    # Create a new feature class of plot locations that will not be buffered
    arcpy.management.MakeFeatureLayer(sites_buffer_distance,
                                      'sites_selected_point_layer',
                                      'buffer_distance = 1')
    arcpy.management.CopyFeatures('sites_selected_point_layer',
                                  sites_selected_point)
    # Create a new feature class of plot locations that will be buffered
    arcpy.management.MakeFeatureLayer(sites_buffer_distance,
                                      'sites_selected_toBuffer_layer',
                                      'buffer_distance IN (15, 18, 25, 30)')
    arcpy.management.CopyFeatures('sites_selected_toBuffer_layer',
                                  sites_selected_toBuffer)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tPlot selection completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Buffer points and select raster cells to represent plot
    print('\tSelecting raster cells to represent large plots...')
    iteration_start = time.time()
    arcpy.analysis.Buffer(sites_selected_toBuffer,
                          sites_selected_buffered,
                          'buffer_distance',
                          'FULL',
                          'ROUND',
                          'NONE',
                          '',
                          'PLANAR')
    arcpy.conversion.PolygonToRaster(sites_selected_buffered,
                                     'site_code',
                                     sites_selected_raster,
                                     'CELL_CENTER',
                                     '',
                                     10
                                     )
    arcpy.conversion.RasterToPoint(sites_selected_raster,
                                   sites_selected_converted,
                                   'site_code')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tRaster cell selection completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Merge plots and remove intermediate fields and data
    print(f'\tMerging selected raster cell points...')
    iteration_start = time.time()
    # Merge the plot points and converted buffered points
    arcpy.management.Merge([sites_selected_point, sites_selected_converted],
                           sites_formatted,
                           '',
                           '')
    # Delete all fields except site code
    arcpy.management.DeleteField(sites_formatted,
                                 ['initial_project',
                                  'perspective',
                                  'cover_method',
                                  'scope_vascular',
                                  'scope_bryophyte',
                                  'scope_lichen',
                                  'plot_dimensions',
                                  'datum',
                                  'latitude',
                                  'longitude',
                                  'error',
                                  'buffer_distance',
                                  'pointid',
                                  'grid_code'])
    # Delete intermediate feature classes and rasters
    if arcpy.Exists(sites_buffer_distance) == 1:
        arcpy.management.Delete(sites_buffer_distance)
    if arcpy.Exists(sites_selected_point) == 1:
        arcpy.management.Delete(sites_selected_point)
    if arcpy.Exists(sites_selected_toBuffer) == 1:
        arcpy.management.Delete(sites_selected_toBuffer)
    if arcpy.Exists(sites_selected_buffered) == 1:
        arcpy.management.Delete(sites_selected_buffered)
    if arcpy.Exists(sites_selected_raster) == 1:
        arcpy.management.Delete(sites_selected_raster)
    if arcpy.Exists(sites_selected_converted) == 1:
        arcpy.management.Delete(sites_selected_converted)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')
    out_process = f'Successfully formatted site data for feature extraction.'
    return out_process
