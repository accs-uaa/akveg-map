# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Files from CSV
# Author: Timm Nawrocki
# Created on: 2019-10-15
# Usage: Must be executed in Python 3.7
# Description: "Download Files from CSV" contacts a server to download a series of files specified in a csv table.
# ---------------------------------------------------------------------------

# Define a function to download files from a csv
def downloadFromCSV(input_table, url_column, directory):
    """
    Description: downloads set of files specified in a particular column of a csv table.
    Inputs: input_table -- csv table containing rows for download items.
            url_column -- title for column containing download urls.
            destination -- folder to store download results.
    Returned Value: Function returns status messages only. Downloaded data are stored on drive.
    Preconditions: csv tables must be generated from web application tools or manually.
    Dependencies: requires os, pandas as pd, and urllib.
    """

    # Import packages
    import os
    import pandas as pd
    import urllib

    # Import a csv file with the download urls for the Arctic DEM tiles
    download_items = pd.read_csv(input_table)

    # Initialize download count
    n = len(download_items[url_column])
    print(f'Beginning download of {n} tiles...')
    count = 1

    # Loop through urls in the downloadURL column and download
    for url in download_items[url_column]:
        target = os.path.join(directory, os.path.split(url)[1])
        if os.path.exists(target) == 0:
            try:
                filedata = urllib.request.urlopen(url)
                datatowrite = filedata.read()
                with open(target, 'wb') as file:
                    file.write(datatowrite)
                    file.close()
                print(f'Downloaded {count} of {n} tiles...')
            except:
                print(f'Tile {count} of {n} not available for download. Check url.')
        else:
            print(f'Tile {count} of {n} already exists...')
        count += 1

    print('----------------')
    print('Finished downloading tiles.')

# Define a wrapper function for arcpy geoprocessing tasks
def arcpy_geoprocessing(geoprocessing_function, check_output = True, check_input = True, **kwargs):
    """
    Description: wraps arcpy geoprocessing and data access functions for file checks, message reporting, and errors.
    Inputs: geoprocessing function -- any arcpy geoprocessing or data access processing steps defined as a function that receive ** kwargs arguments.
            check_output -- boolean input to control if the function should check if the output already exists prior to executing geoprocessing function
            check_input -- boolean input to control if the function should check if the inputs already exist prior to executing geoprocessing function
            **kwargs -- key word arguments that are used in the wrapper and passed to the geoprocessing function
                'input_array' -- if check_input == True, then the input datasets must be passed as an array
                'output_array' -- if check_output == True, then the output datasets must be passed as an array
    Returned Value: Function returns messages, warnings, and errors from geoprocessing functions.
    Preconditions: geoprocessing function and kwargs must be defined, this function does not conduct any geoprocessing on its own
    """

    # Import packages
    import arcpy

    try:
        # If check_output is True, then check if output exists and warn of overwrite if it does
        if check_output == True:
            for output_data in kwargs['output_array']:
                if arcpy.Exists(output_data) == True:
                    print(f"{output_data} already exists and will be overwritten.")
        # If check_input is True, then check if inputs exist and quit if any do not
        if check_input == True:
            for input_data in kwargs['input_array']:
                if arcpy.Exists(input_data) != True:
                    print(f'{input_data} does not exist. Check that environment workspace is correct.')
                    quit()
        # Execute geoprocessing function if all input data exists
        out_process = geoprocessing_function(**kwargs)
        # Provide results report
        try:
            msg_count = out_process.messageCount
            print(out_process.getMessage(msg_count - 1))
        except:
            print(out_process)
    # Provide arcpy errors for execution error
    except arcpy.ExecuteError as err:
        print(arcpy.GetMessages())
        quit()

# Define function to create composite DEM
def create_composite_dem(**kwargs):
    """
    Description: creates a DEM from individual DEM tiles
    Inputs: 'tile_folder' -- a folder containing the raster tiles
            'projected_folder' -- a folder in which to store the projected tiles
            'cell_size' -- a cell size for the output DEM
            'input_projection' -- the machine number for the input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'input_array' -- an array containing the snap raster
            'output_array' -- an array containing the output raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Int
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Parse key word argument inputs
    tile_folder = kwargs['tile_folder']
    projected_folder = kwargs['projected_folder']
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transformation = kwargs['geographic_transformation']
    snap_raster = kwargs['input_array'][0]
    dem_composite = kwargs['output_array'][0]

    # Define intermediate datasets
    mosaic_location, mosaic_name = os.path.split(dem_composite)

    # Start timing function
    iteration_start = time.time()
    # Create a list of DEM raster tiles
    print('Compiling list of raster tiles...')
    arcpy.env.workspace = tile_folder
    tile_list = arcpy.ListRasters('*', 'ALL')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Process will form composite from {len(tile_list)} raster tiles...')
    print(f'Raster list completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Define projection and reproject all rasters in list
    print(f'Reprojecting {len(tile_list)} raster tiles...')
    # Define the initial projection
    tile_projection = arcpy.SpatialReference(input_projection)
    # Define the target projection
    composite_projection = arcpy.SpatialReference(output_projection)
    # Set snap raster
    arcpy.env.snapRaster = snap_raster
    # Set initial counter
    count = 1
    # Reproject all rasters in list
    for raster in tile_list:
        # Define input raster path
        input_raster = os.path.join(tile_folder, raster)
        # Define intermediate and output raster
        reprojected_raster = os.path.join(projected_folder, os.path.splitext(raster)[0] + '_reprojected.tif')
        output_raster = os.path.join(projected_folder, os.path.splitext(raster)[0] + '.tif')
        # Check if output raster already exists:
        if os.path.exists(output_raster) == 0:
            # Start timing function
            iteration_start = time.time()
            print(f'\tReprojecting tile {count} of {len(tile_list)}...')
            # Define initial projection
            arcpy.DefineProjection_management(input_raster, tile_projection)
            # Reproject tile
            arcpy.ProjectRaster_management(input_raster,
                                           reprojected_raster,
                                           composite_projection,
                                           'BILINEAR',
                                           cell_size,
                                           geographic_transformation)
            # Round to integer and store as 16 bit signed raster
            integer_raster = Int(Raster(reprojected_raster) + 0.5)
            # Set values less than -50 to null
            corrected_raster = SetNull(integer_raster, integer_raster, 'VALUE < -50')
            # Convert corrected raster to 16 bit signed
            arcpy.CopyRaster_management(corrected_raster, output_raster, '', '', '-32768', 'NONE', 'NONE', '16_BIT_SIGNED','NONE', 'NONE', 'TIFF', 'NONE')
            # Delete intermediate raster
            arcpy.Delete_management(reprojected_raster)
            # End timing
            iteration_end = time.time()
            iteration_elapsed = int(iteration_end - iteration_start)
            iteration_success_time = datetime.datetime.now()
            # Report success for iteration
            print(f'\tFinished reprojecting tile {count} of {len(tile_list)}...')
            print(f'\tTile projection completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
            print('\t----------')
        # Return message if output raster already exists
        else:
            print(f'\tTile {count} of {len(tile_list)} already processed...')
        # Increase count
        count += 1
    # Report success for loop
    print(f'Defined projection for {len(tile_list)} raster tiles...')
    print('----------')

    # Start timing function
    iteration_start = time.time()
    # Create a list of projected DEM raster tiles
    print('Compiling list of projected raster tiles...')
    arcpy.env.workspace = projected_folder
    projected_tile_list = arcpy.ListRasters('*', 'ALL')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Process will form composite from {len(tile_list)} raster tiles...')
    print(f'Raster list completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Start timing function
    iteration_start = time.time()
    print('Creating composite from tiles...')
    # Mosaic raster tiles to new raster
    arcpy.MosaicToNewRaster_management(projected_tile_list,
                                       mosaic_location,
                                       mosaic_name,
                                       composite_projection,
                                       '16_BIT_SIGNED',
                                       cell_size,
                                       '1',
                                       'MAXIMUM',
                                       'FIRST')
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success
    print(f'Raster composite completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Delete intermediate dataset
    out_process = 'Successful creating composite DEM.'
    return out_process

# Define function to reproject raster and store integer result
def reproject_integer(**kwargs):
    """
    Description: creates a DEM from individual DEM tiles
    Inputs: 'cell_size' -- a cell size for the output DEM
            'input_projection' -- the machine number for the input projection
            'output_projection' -- the machine number for the output projection
            'geographic_transformation -- the string representation of the appropriate geographic transformation (blank if none required)
            'input_array' -- an array containing the input raster and the snap raster
            'output_array' -- the output should be an array with a full feature class and a clipped feature class
    """

    # Import packages
    import arcpy
    from arcpy.sa import Int
    from arcpy.sa import Raster
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Parse key word argument inputs
    cell_size = kwargs['cell_size']
    input_projection = kwargs['input_projection']
    output_projection = kwargs['output_projection']
    geographic_transformation = kwargs['geographic_transformation']
    input_raster = kwargs['input_array'][0]
    snap_raster = kwargs['input_array'][1]
    output_raster = kwargs['output_array'][0]

    # Define the initial projection
    initial_projection = arcpy.SpatialReference(input_projection)
    # Define the target projection
    composite_projection = arcpy.SpatialReference(output_projection)
    # Set snap raster
    arcpy.env.snapRaster = snap_raster

    # Start timing function
    iteration_start = time.time()
    print(f'Reprojecting input raster...')
    # Define intermediate and output raster
    reprojected_raster = os.path.splitext(input_raster)[0] + '_reprojected.tif'
    # Define initial projection
    arcpy.DefineProjection_management(input_raster, initial_projection)
    # Reproject raster
    arcpy.ProjectRaster_management(input_raster,
                                    reprojected_raster,
                                    composite_projection,
                                    'BILINEAR',
                                    cell_size,
                                    geographic_transformation)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(f'Finished reprojecting input raster...')
    print(f'Projection completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Start timing function
    iteration_start = time.time()
    print(f'Converting raster to 16 bit integer...')
    # Round to integer and store as 16 bit signed raster
    integer_raster = Int(Raster(reprojected_raster) + 0.5)
    arcpy.CopyRaster_management(integer_raster, output_raster, '', '', '-32768', 'NONE', 'NONE', '16_BIT_SIGNED',
                                'NONE', 'NONE', 'TIFF', 'NONE')
    # Delete intermediate raster
    arcpy.Delete_management(reprojected_raster)
    # End timing
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    # Report success for iteration
    print(f'Finished converting to 16 bit integer...')
    print(
        f'Conversion completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('----------')

    # Delete intermediate dataset
    out_process = 'Successful reprojecting and converting raster.'
    return out_process


# Iterate through each major grid
def create_buffered_tiles(**kwargs):
    """
    Description: creates a DEM from individual DEM tiles
    Inputs: 'tile_name' -- a field name in the grid index that stores the tile name
            'distance' -- a string representing a number and units for buffer distance
            'input_array' -- an array containing the input grid index and a clip area
            'output_geodatabase' -- an empty geodatabase to store the output tiles
    """

    # Import packages
    import arcpy
    import datetime
    import os
    import time

    # Parse key word argument inputs
    tile_name = kwargs['tile_name']
    distance = kwargs['distance']
    grid_index = kwargs['input_array'][0]
    clip_area = kwargs['input_array'][1]
    output_geodatabase = kwargs['output_geodatabase']

    # Print initial status
    print(f'Extracting grid tiles from {os.path.split(grid_index)[1]}...')

    # Define fields for search cursor
    fields = ['SHAPE@', tile_name]
    # Initiate search cursor on grid index with defined fields
    with arcpy.da.SearchCursor(grid_index, fields) as cursor:
        # Iterate through each feature in the feature class
        for row in cursor:
            # Define an output and temporary feature class
            output_grid = os.path.join(output_geodatabase, 'Grid_' + row[1])
            temporary_grid = os.path.join(output_geodatabase, 'Grid_' + row[1] + '_Buffer')
            print(f'\tProcessing grid tile {os.path.split(output_grid)[1]}...')
            # If tile does not exist, then create tile
            if arcpy.Exists(output_grid) == 0:
                # Start timing function
                iteration_start = time.time()
                # Define feature
                feature = row[0]
                # Buffer feature by user specified distance
                arcpy.Buffer_analysis(feature, temporary_grid, distance, 'FULL', 'ROUND', 'NONE', '', 'PLANAR')
                # Clip buffered feature to clip area
                arcpy.Clip_analysis(temporary_grid, clip_area, output_grid)
                # If temporary feature class exists, then delete it
                if arcpy.Exists(temporary_grid) == 1:
                    arcpy.Delete_management(temporary_grid)
                # End timing
                iteration_end = time.time()
                iteration_elapsed = int(iteration_end - iteration_start)
                iteration_success_time = datetime.datetime.now()
                # Report success
                print(
                    f'\tOutput grid {os.path.split(output_grid)[1]} completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
                print('\t----------')
            else:
                print(f'\tOutput grid {os.path.split(output_grid)[1]} already exists...')
                print('\t----------')

    # Return final status
    out_process = 'Completed creation of grid tiles.'
    return out_process
