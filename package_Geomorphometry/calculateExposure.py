# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate exposure
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate exposure" is a function that calculates a continuous index of solar exposure weighted by steepness of the slope. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate solar exposure index
def calculate_exposure(aspect_raw, slope_float, conversion_factor, exposure_output):
    """
    Description: calculates 16-bit signed solar exposure index
    Inputs: 'raw_aspect' -- an input raw aspect raster
            'raw_slope' -- an input raster digital elevation model
            'conversion_factor' -- an integer to be multiplied with the output for conversion to integer raster
            'exposure_output' -- an output exposure raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input aspect and slope raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Cos
    from arcpy.sa import Int
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Convert degrees to radians
    print('\t\tConverting degrees to radians...')
    aspect_radian = Raster(aspect_raw) * 0.0174533

    # Calculate cosine of modified aspect
    print('\t\tCalculating cosine of aspect...')
    cos_aspect = Cos(aspect_radian - 3.31613)

    # Calculate solar exposure index
    print('\t\tMultiplying cosine by slope...')
    exposure_raster = cos_aspect * slope_float

    # Convert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int((exposure_raster * conversion_factor) + 0.5)

    # Export raster
    print('\t\tExporting exposure raster as 16 bit signed...')
    arcpy.management.CopyRaster(integer_raster,
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
