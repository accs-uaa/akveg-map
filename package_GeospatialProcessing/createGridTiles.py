# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create grid tiles
# Author: Timm Nawrocki
# Last Updated: 2023-03-30
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create grid tiles" is a function that creates grid tiles for a given study area.
# ---------------------------------------------------------------------------

# Define function to create grid tiles
def create_grid_tiles(**kwargs):
    """
    Description: create grid tiles from a study area
    Inputs: 'distance' -- a string representing an integer distance and units
            'grid_field' -- a string representing the name of the field to store grid information
            'work_geodatabase' -- a geodatabase to store temporary results
            'input_array' -- an array containing the total area feature class
            'output_array' -- an array containing the grid tile feature class
    Returned Value: Returns feature class containing the grid tiles
    Preconditions: an area of interest feature class must be manually generated to define grid extent
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    distance_km = kwargs['distance_km']
    distance = str(distance_km) + ' Kilometers'
    origin_coordinate = kwargs['origin_coordinate']
    height = kwargs['height']
    length = kwargs['length']
    number_rows = height/distance_km
    number_columns = length/distance_km
    work_geodatabase = kwargs['work_geodatabase']
    input_feature = kwargs['input_array'][0]
    grid_output = kwargs['output_array'][0]

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of the possible cores on the machine
    arcpy.env.parallelProcessingFactor = '66%'

    # Set workspace
    arcpy.env.workspace = work_geodatabase

    # Create grid index
    print(f'\tCreating grid index at {distance}...')
    iteration_start = time.time()
    arcpy.cartography.GridIndexFeatures(grid_output,
                                        input_feature,
                                        'NO_INTERSECTFEATURE',
                                        'NO_USEPAGEUNIT',
                                        '',
                                        distance,
                                        distance,
                                        origin_coordinate,
                                        number_rows,
                                        number_columns,
                                        1,
                                        'NO_LABELFROMORIGIN')
    # Calculate grid V
    expression_v = f'get_v(float(!PageNumber!), {number_columns})'
    code_block_v = '''def get_v(page_number, denominator):
    v_value = math.ceil(page_number/denominator)
    return v_value
    '''
    arcpy.management.CalculateField(grid_output,
                                    'V',
                                    expression_v,
                                    'PYTHON3',
                                    code_block_v,
                                    'SHORT',
                                    )
    # Calculate grid H
    expression_h = f'get_h(float(!PageNumber!), {number_columns})'
    code_block_h = '''def get_h(page_number, denominator):
    v_value = math.ceil(page_number/denominator)
    h_value = page_number - ((v_value * denominator) - denominator)
    return h_value
    '''
    arcpy.management.CalculateField(grid_output,
                                    'H',
                                    expression_h,
                                    'PYTHON3',
                                    code_block_h,
                                    'SHORT',
                                    )
    # Calculate dimensions_km
    expression_dimensions = f'get_dimensions({distance_km})'
    code_block_dimensions = '''def get_dimensions(distance_km):
    dimensions_km = str(distance_km) + 'x' + str(distance_km)
    return dimensions_km
    '''
    arcpy.management.CalculateField(grid_output,
                                    'dimensions_km',
                                    expression_dimensions,
                                    'PYTHON3',
                                    code_block_dimensions,
                                    'TEXT')
    # Calculate grid code
    expression_code = f'define_code(!H!, !V!, {distance_km})'
    code_block_code = '''def define_code(H, V, distance_km):
    if distance_km < 10:
        distance_string = '00' + str(distance_km)
    elif distance_km < 100:
        distance_string = '0' + str(distance_km)
    else:
        distance_string = str(distance_km)
    if H < 10:
        h_string = '00' + str(H)
    elif H < 100:
        h_string = '0' + str(H)
    else:
        h_string = str(H)
    if V < 10:
        v_string = '00' + str(V)
    elif V < 100:
        v_string = '0' + str(V)
    else:
        v_string = str(V)
    code_string = 'AK' + distance_string + 'H' + h_string + 'V' + v_string
    return code_string
    '''
    arcpy.management.CalculateField(grid_output,
                                    'grid_code',
                                    expression_code,
                                    'PYTHON3',
                                    code_block_code,
                                    'TEXT',
                                    )
    # Calculate grid geometry
    arcpy.management.CalculateGeometryAttributes(grid_output,
                                                 [['xmin', 'EXTENT_MIN_X'],
                                                  ['ymin', 'EXTENT_MIN_Y'],
                                                  ['xmax', 'EXTENT_MAX_X'],
                                                  ['ymax', 'EXTENT_MAX_Y']],
                                                 'METERS')
    # Calculate centroid
    arcpy.management.CalculateGeometryAttributes(grid_output,
                                                 [['centroid_latitude_dd', 'CENTROID_Y'],
                                                  ['centroid_longitude_dd', 'CENTROID_X']],
                                                 coordinate_format='DD')
    # Delete extra fields
    arcpy.management.DeleteField(grid_output, ['PageName', 'PageNumber'])
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'\tFinished creating grid index at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return success message
    outprocess = 'Successfully created major and minor grid indices.'
    return outprocess
