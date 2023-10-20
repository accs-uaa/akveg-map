# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate heat load index
# Author: Timm Nawrocki
# Last Updated: 2023-10-19
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate heat load index" is a function that calculates an index of solar heat. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate heat load index
def calculate_heat_load(area_raster, elevation_float, slope_float, aspect_float, conversion_factor, heatload_output):
    """
    Description: calculates 16-bit signed heat load index
    Inputs: 'area_raster' -- a raster of the study area to set snap raster and extract area
            'elevation_float' -- an input float elevation raster
            'slope_float' -- an input float slope raster in degrees
            'aspect_float' -- an input float aspect raster in degrees
            'conversion_factor' -- an integer to be multiplied with the output for conversion to integer raster
            'heatload_output' -- a file path for an output heat load index raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires input elevation, slope, and aspects rasters
    """

    # Import packages
    import math
    from numpy import pi
    import arcpy
    from arcpy.sa import Abs
    from arcpy.sa import Cos
    from arcpy.sa import Exp
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Int
    from arcpy.sa import Raster
    from arcpy.sa import Sin
    import math

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Calculate middle latitude of extent in WGS84 projection
    print('\t\tCalculating raster properties...')
    # Identify extent of elevation input
    grid_extent = Raster(elevation_float).extent
    # Project extent to WGS84
    project_extent = grid_extent.projectAs(arcpy.SpatialReference(4326))
    # Check upper and lower bounds
    lower_lat = float(project_extent.YMin)
    upper_lat = float(project_extent.YMax)
    # Calculate middle latitude
    middle_latitude = abs(((lower_lat + upper_lat) / 2) + lower_lat)
    # Convert middle latitude to radians
    middle_radian = middle_latitude * (pi/180)
    cos_latitude = math.cos(middle_radian)
    sin_latitude = math.sin(middle_radian)

    # Convert degrees to radians
    print('\tConverting degrees to radians...')
    slope_radian = Raster(slope_float) * (pi/180)
    aspect_radian = Raster(aspect_float) * (pi/180)

    # Calculate heat load index
    print('\tCalculating heat load index...')
    # Calculate modified aspect
    modified_aspect = Abs(pi - Abs(aspect_radian - 3.926991))
    # Calculate sine and cosine of slope
    cos_slope = Cos(slope_radian)
    sin_slope = Sin(slope_radian)
    # Calculate sine and cosine of modified aspect
    cos_aspect = Cos(modified_aspect)
    sin_aspect = Sin(modified_aspect)
    # Calculate intermediate values
    factor_1 = 1.582 * cos_latitude * cos_slope
    factor_2 = 1.5 * cos_aspect * sin_slope * sin_latitude
    factor_3 = 0.262 * sin_latitude * sin_slope
    factor_4 = 0.607 * sin_aspect * sin_slope
    # Calculate heat load index
    heat_load = Exp(-1.467 + factor_1 - factor_2 - factor_3 + factor_4)

    # Convert to integer
    print('\tConverting to integer...')
    integer_raster = Int((heat_load * conversion_factor) + 0.5)

    # Extract to area raster
    print('\tExtracting raster to area...')
    extract_integer = ExtractByMask(integer_raster, area_raster)

    # Export raster
    print('\tExporting heat load raster as 16-bit signed...')
    arcpy.management.CopyRaster(extract_integer,
                                heatload_output,
                                '',
                                '32767',
                                '-32768',
                                'NONE',
                                'NONE',
                                '16_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE')
