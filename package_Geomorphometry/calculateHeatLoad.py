# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate heat load index
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate heat load index" is a function that calculates an index of solar heat. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate heat load index
def calculate_heat_load(elevation_float, slope_float, aspect_raw, conversion_factor, heatload_output):
    """
    Description: calculates 16-bit signed topographic wetness
    Inputs: 'elevation_float' -- an input float elevation raster
            'slope_float' -- an input float slope raster in degrees
            'aspect_raw' -- an input float aspect raster in degrees
            'conversion_factor' -- an integer to be multiplied with the output for conversion to integer raster
            'heatload_output' -- a file path for an output heat load index raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires input elevation, slope, and aspects rasters
    """

    # Import packages
    import arcpy
    from arcpy.sa import Abs
    from arcpy.sa import Cos
    from arcpy.sa import Exp
    from arcpy.sa import Int
    from arcpy.sa import Raster
    from arcpy.sa import Sin
    import math

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Calculate middle latitude of extent
    print('\t\tCalculating raster properties...')
    grid_extent = Raster(elevation_float).extent
    middle_latitude = (grid_extent.YMin + grid_extent.YMax) / 2
    middle_radian = middle_latitude * 0.0174533
    cos_latitude = math.cos(middle_radian)
    sin_latitude = math.sin(middle_radian)

    # Convert degrees to radians
    print('\t\tConverting degrees to radians...')
    slope_radian = Raster(slope_float) * 0.0174533
    aspect_radian = Raster(aspect_raw) * 0.0174533

    # Calculate heat load index
    print('\t\tCalculating heat load index...')
    modified_aspect = Abs(3.141593 - Abs(aspect_radian - 3.926991))
    cos_slope = Cos(slope_radian)
    sin_slope = Sin(slope_radian)
    cos_aspect = Cos(modified_aspect)
    sin_aspect = Sin(modified_aspect)
    heat_load = Exp(-1.467 + 1.582 * cos_latitude * cos_slope - 1.5 * cos_aspect * sin_slope * sin_latitude - 0.262 * sin_latitude * sin_slope + 0.607 * sin_aspect * sin_slope)

    # Convert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int((heat_load * conversion_factor) + 0.5)

    # Export raster
    print('\t\tExporting heat load raster as 16-bit signed...')
    arcpy.management.CopyRaster(integer_raster,
                                heatload_output,
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
