# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate exposure
# Author: Timm Nawrocki
# Last Updated: 2023-10-19
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate exposure" is a function that calculates a continuous index of solar exposure weighted by steepness of the slope. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate solar exposure index
def calculate_exposure(area_raster, aspect_float, slope_float, conversion_factor, exposure_output):
    """
    Description: calculates 16-bit signed solar exposure index
    Inputs: 'area_raster' -- a raster of the study area to set snap raster and extract area
            'aspect_float' -- an input float aspect raster in degrees
            'slope_float' -- an input float slope raster in degrees
            'conversion_factor' -- an integer to be multiplied with the output for conversion to integer raster
            'exposure_output' -- an output exposure raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input aspect and slope raster
    """

    # Import packages
    from numpy import pi
    import arcpy
    from arcpy.sa import Cos
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Int
    from arcpy.sa import Raster

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

    # Convert degrees to radians
    print('\tConverting degrees to radians...')
    aspect_radian = Raster(aspect_float) * (pi/180)

    # Calculate cosine of modified aspect
    print('\tCalculating cosine of aspect...')
    cos_aspect = Cos(aspect_radian - pi)

    # Calculate solar exposure index
    print('\tMultiplying cosine by slope...')
    exposure_raster = cos_aspect * slope_float

    # Convert to integer
    print('\tConverting to integer...')
    integer_raster = Int((exposure_raster * conversion_factor) + 0.5)

    # Extract to area raster
    print('\tExtracting raster to area...')
    extract_integer = ExtractByMask(integer_raster, area_raster)

    # Export raster
    print('\tExporting exposure raster as 16-bit signed...')
    arcpy.management.CopyRaster(extract_integer,
                                exposure_output,
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
