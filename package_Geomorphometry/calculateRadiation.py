# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic radiation
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate topographic radiation" is a function that calculates a continuous index of topographic radiation using a 5x5 cell window from the coolest and wettest NNE aspects to the hottest and dryest SSW aspects. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate topographic radiation
def calculate_radiation(aspect_raw, conversion_factor, radiation_output):
    """
    Description: calculates 16-bit signed topographic radiation
    Inputs: 'aspect_raw' -- an input raw aspect raster
            'conversion_factor' -- an integer to be multiplied with the output for conversion to integer raster
            'radiation_output' -- an output topographic radiation raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input raw aspect raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import Cos
    from arcpy.sa import Int
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Convert degrees to radians
    print('\t\tConverting degrees to radians...')
    aspect_radian = Raster(aspect_raw) * 0.0174533

    # Calculate topographic radiation
    print('\t\tCalculating topographic radiation aspect index...')
    radiation_raster = (1 - Cos(aspect_radian - 0.523599)) / 2

    # Convert negative aspect values
    print('\t\tConverting negative aspect values...')
    conditional_raster = Con(Raster(aspect_radian) < 0, 0.5, radiation_raster)

    # Convert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int((conditional_raster * conversion_factor) + 0.5)

    # Export raster
    print('\t\tExporting radiation raster as 16-bit signed...')
    arcpy.management.CopyRaster(integer_raster,
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
