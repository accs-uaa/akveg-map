# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate Topographic Properties
# Author: Timm Nawrocki
# Last Updated: 2019-12-07
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Calculate Topographic Properties" is a function that calculates multiple topographic properties from an elevation raster using the Geomorphometry and Gradient Metrics Toolbox 2.0.
# ---------------------------------------------------------------------------

# Define a function to calculate aspect, compound topographic index, heat load index, integrated moisture index, roughness, site exposure, slope, surface area ratio, and surface relief ratio
def calculate_topographic_properties(**kwargs):
    """
    Description: calculates topographic properties from an elevation raster
    Inputs: 'z_unit' -- a string value of either 'Meter' or 'Foot' representing the vertical unit of the elevation raster
            'input_array' -- an array containing the grid raster (must be first) and the elevation raster
            'output_array' -- an array containing the output rasters for aspect, compound topographic index, heat load index, integrated moisture index, roughness, site exposure, slope, surface area ratio, and surface relief ratio (in that order)
    Returned Value: Returns a raster dataset on disk for each topographic property
    Preconditions: requires an input DEM that can be created through other scripts in this repository
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import IsNull
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Raster
    from arcpy.sa import Int
    from arcpy.sa import FlowDirection
    from arcpy.sa import FlowAccumulation
    from arcpy.sa import Slope
    from arcpy.sa import Aspect
    from package_Geomorphometry import compound_topographic
    from package_Geomorphometry import getZFactor
    from package_Geomorphometry import linear_aspect
    from package_Geomorphometry import mean_slope
    from package_Geomorphometry import roughness
    from package_Geomorphometry import site_exposure
    from package_Geomorphometry import surface_area
    from package_Geomorphometry import surface_relief
    from package_Geomorphometry import topographic_position
    from package_Geomorphometry import topographic_radiation
    import datetime
    import os
    import time

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Use two thirds of cores on processes that can be split.
    arcpy.env.parallelProcessingFactor = "66%"

    # Parse key word argument inputs
    z_unit = kwargs['z_unit']
    grid_raster = kwargs['input_array'][0]
    elevation_input = kwargs['input_array'][1]
    aspect_output = kwargs['output_array'][0]
    cti_output = kwargs['output_array'][1]
    roughness_output = kwargs['output_array'][2]
    exposure_output = kwargs['output_array'][3]
    slope_output = kwargs['output_array'][4]
    area_output = kwargs['output_array'][5]
    relief_output = kwargs['output_array'][6]
    position_output = kwargs['output_array'][7]
    radiation_output = kwargs['output_array'][8]

    # Set snap raster
    arcpy.env.snapRaster = grid_raster

    # Define folder structure
    grid_title = os.path.splitext(os.path.split(grid_raster)[1])[0]
    raster_folder = os.path.split(elevation_input)[0]
    intermediate_folder = os.path.join(raster_folder, 'intermediate')
    # Create intermediate folder if it does not already exist
    if os.path.exists(intermediate_folder) == 0:
        os.mkdir(intermediate_folder)

    # Define intermediate datasets
    flow_direction_raster = os.path.join(intermediate_folder, 'flow_direction.tif')
    flow_accumulation_raster = os.path.join(intermediate_folder, 'flow_accumulation.tif')
    raw_slope_raster = os.path.join(intermediate_folder, 'raw_slope.tif')
    raw_aspect_raster = os.path.join(intermediate_folder, 'raw_aspect.tif')

    # Get the z factor appropriate to the xy and z units
    zFactor = getZFactor(elevation_input, z_unit)

    #### CALCULATE INTERMEDIATE DATASETS

    # Calculate flow direction if it does not already exist
    if os.path.exists(flow_direction_raster) == 0:
        # Start timing function
        iteration_start = time.time()
        # Calculate flow direction
        print(f'\tCalculating flow direction for {grid_title}...')
        flow_direction = FlowDirection(elevation_input, 'NORMAL', '', 'D8')
        flow_direction.save(flow_direction_raster)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tFlow direction already exists for {grid_title}.')
        print('\t----------')

    # Calculate flow accumulation if it does not already exist
    if os.path.exists(flow_accumulation_raster) == 0:
        # Start timing function
        iteration_start = time.time()
        # Calculate flow accumulation
        print(f'\tCalculating flow accumulation for {grid_title}...')
        flow_accumulation = FlowAccumulation(flow_direction, '', 'FLOAT', 'D8')
        flow_accumulation.save(flow_accumulation_raster)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tFlow accumulation already exists for {grid_title}.')
        print('\t----------')

    # Calculate raw slope in degrees if it does not already exist
    if os.path.exists(raw_slope_raster) == 0:
        # Start timing function
        iteration_start = time.time()
        # Calculate slope
        print(f'\tCalculating raw slope for {grid_title}...')
        raw_slope = Slope(elevation_input, "DEGREE", zFactor)
        raw_slope.save(raw_slope_raster)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tRaw slope already exists for {grid_title}.')
        print('\t----------')

    # Calculate raw aspect if it does not already exist
    if os.path.exists(raw_aspect_raster) == 0:
        # Start timing function
        iteration_start = time.time()
        # Calculate aspect
        print(f'\tCalculating raw aspect for {grid_title}...')
        raw_aspect = Aspect(elevation_input, 'PLANAR', z_unit)
        raw_aspect.save(raw_aspect_raster)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tRaw aspect already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE LINEAR ASPECT

    # Calculate linear aspect if it does not already exist
    if os.path.exists(aspect_output) == 0:
        print(f'\tCalculating linear aspect for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an initial linear aspect calculation using the linear aspect function
        aspect_intermediate = os.path.splitext(aspect_output)[0] + '_intermediate.tif'
        linear_aspect(raw_aspect_raster, aspect_intermediate)
        # Round to integer and store as 16 bit signed raster
        print(f'\t\tConverting values to integers...')
        integer_aspect = Int(Raster(aspect_intermediate) + 0.5)
        # Fill missing data (no aspect) with values of -1
        print(f'\t\tFilling values of no aspect...')
        conditional_aspect = Con(IsNull(integer_aspect), -1, integer_aspect)
        # Extract filled raster to grid mask
        print(f'\t\tExtracting filled raster to grid...')
        extract_aspect = ExtractByMask(conditional_aspect, grid_raster)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(extract_aspect,
                                    aspect_output,
                                    '',
                                    '',
                                    '-32768',
                                    'NONE',
                                    'NONE',
                                    '16_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(aspect_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tLinear aspect already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE COMPOUND TOPOGRAPHIC INDEX

    # Calculate compound topographic index if it does not already exist
    if os.path.exists(cti_output) == 0:
        print(f'\tCalculating compound topographic index for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an intermediate compound topographic index calculation
        cti_intermediate = os.path.splitext(cti_output)[0] + '_intermediate.tif'
        compound_topographic(elevation_input,
                             flow_accumulation_raster,
                             raw_slope_raster,
                             cti_intermediate)
        # Convert to integer values
        print(f'\t\tConverting values to integers...')
        integer_compound = Int((Raster(cti_intermediate)*100) + 0.5)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(integer_compound,
                                    cti_output,
                                    '',
                                    '',
                                    '-32768',
                                    'NONE',
                                    'NONE',
                                    '16_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(cti_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tCompound topographic index already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE ROUGHNESS

    # Calculate roughness if it does not already exist
    if os.path.exists(roughness_output) == 0:
        print(f'\tCalculating roughness for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an intermediate compound topographic index calculation
        roughness_intermediate = os.path.splitext(roughness_output)[0] + '_intermediate.tif'
        roughness(elevation_input,
                  roughness_intermediate)
        # Convert to integer values
        print(f'\t\tConverting values to integers...')
        integer_roughness = Int(Raster(roughness_intermediate) + 0.5)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(integer_roughness,
                                    roughness_output,
                                    '',
                                    '',
                                    '-32768',
                                    'NONE',
                                    'NONE',
                                    '16_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(roughness_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tRoughness already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE SITE EXPOSURE

    # Calculate site exposure if it does not already exist
    if os.path.exists(exposure_output) == 0:
        print(f'\tCalculating site exposure for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an intermediate compound topographic index calculation
        exposure_intermediate = os.path.splitext(exposure_output)[0] + '_intermediate.tif'
        site_exposure(raw_aspect_raster,
                      raw_slope_raster,
                      exposure_intermediate)
        # Convert to integer values
        print(f'\t\tConverting values to integers...')
        integer_exposure = Int((Raster(exposure_intermediate) * 100) + 0.5)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(integer_exposure,
                                    exposure_output,
                                    '',
                                    '',
                                    '-32768',
                                    'NONE',
                                    'NONE',
                                    '16_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(exposure_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tSite exposure already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE MEAN SLOPE

    # Calculate mean slope if it does not already exist
    if os.path.exists(slope_output) == 0:
        print(f'\tCalculating mean slope for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an intermediate mean slope calculation
        slope_intermediate = os.path.splitext(slope_output)[0] + '_intermediate.tif'
        mean_slope(raw_slope_raster,
                   slope_intermediate)
        # Convert to integer values
        print(f'\t\tConverting values to integers...')
        integer_slope = Int(Raster(slope_intermediate) + 0.5)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(integer_slope,
                                    slope_output,
                                    '',
                                    '',
                                    '-128',
                                    'NONE',
                                    'NONE',
                                    '8_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(slope_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tMean slope already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE SURFACE AREA RATIO

    # Calculate surface area ratio if it does not already exist
    if os.path.exists(area_output) == 0:
        print(f'\tCalculating surface area ratio for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an intermediate surface area ratio calculation
        area_intermediate = os.path.splitext(area_output)[0] + '_intermediate.tif'
        surface_area(raw_slope_raster,
                     area_intermediate)
        # Convert to integer values
        print(f'\t\tConverting values to integers...')
        integer_area = Int((Raster(area_intermediate) * 10) + 0.5)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(integer_area,
                                    area_output,
                                    '',
                                    '',
                                    '-32768',
                                    'NONE',
                                    'NONE',
                                    '16_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(area_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tSurface area ratio already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE SURFACE RELIEF RATIO

    # Calculate surface relief ratio if it does not already exist
    if os.path.exists(relief_output) == 0:
        print(f'\tCalculating surface relief ratio for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an intermediate surface relief ratio calculation
        relief_intermediate = os.path.splitext(relief_output)[0] + '_intermediate.tif'
        surface_relief(elevation_input,
                       relief_intermediate)
        # Convert to integer values
        print(f'\t\tConverting values to integers...')
        integer_relief = Int((Raster(relief_intermediate) * 1000) + 0.5)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(integer_relief,
                                    relief_output,
                                    '',
                                    '',
                                    '-32768',
                                    'NONE',
                                    'NONE',
                                    '16_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(relief_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tSurface relief ratio already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE TOPOGRAPHIC POSITION

    # Calculate topographic position if it does not already exist
    if os.path.exists(position_output) == 0:
        print(f'\tCalculating topographic position for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an intermediate topographic position calculation
        position_intermediate = os.path.splitext(position_output)[0] + '_intermediate.tif'
        topographic_position(elevation_input,
                             position_intermediate)
        # Convert to integer values
        print(f'\t\tConverting values to integers...')
        integer_position = Int((Raster(position_intermediate) * 100) + 0.5)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(integer_position,
                                    position_output,
                                    '',
                                    '',
                                    '-32768',
                                    'NONE',
                                    'NONE',
                                    '16_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(position_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tTopographic position already exists for {grid_title}.')
        print('\t----------')

    #### CALCULATE TOPOGRAPHIC RADIATION

    # Calculate topographic radiation if it does not already exist
    if os.path.exists(radiation_output) == 0:
        print(f'\tCalculating topographic radiation for {grid_title}...')
        # Start timing function
        iteration_start = time.time()
        # Create an intermediate topographic position calculation
        radiation_intermediate = os.path.splitext(radiation_output)[0] + '_intermediate.tif'
        topographic_radiation(elevation_input,
                              radiation_intermediate)
        # Convert to integer values
        print(f'\t\tConverting values to integers...')
        integer_radiation = Int((Raster(radiation_intermediate) * 1000) + 0.5)
        # Extract filled raster to grid mask
        print(f'\t\tExtracting integer raster to grid...')
        extract_radiation = ExtractByMask(integer_radiation, grid_raster)
        # Copy extracted raster to output
        print(f'\t\tCreating output raster...')
        arcpy.CopyRaster_management(extract_radiation,
                                    radiation_output,
                                    '',
                                    '',
                                    '-32768',
                                    'NONE',
                                    'NONE',
                                    '16_BIT_SIGNED',
                                    'NONE',
                                    'NONE',
                                    'TIFF',
                                    'NONE')
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Delete intermediate dataset if possible
        try:
            arcpy.Delete_management(radiation_intermediate)
        except:
            print('\t\tCould not delete intermediate dataset...')
        # Report success
        print(
            f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'\tTopographic radiation already exists for {grid_title}.')
        print('\t----------')

    outprocess = f'Finished topographic properties for {grid_title}.'
    return outprocess
