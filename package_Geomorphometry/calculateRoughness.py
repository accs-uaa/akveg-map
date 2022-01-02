# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate roughness
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate roughness" is a function that calculates roughness as the square of focal standard deviation using a 5x5 cell window. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate roughness
def calculate_roughness(elevation_float, conversion_factor, roughness_output):
    """
    Description: calculates 16-bit signed roughness
    Inputs: 'elevation_float' -- an input float elevation raster
            'conversion_factor' -- an integer to be multiplied with the output for conversion to integer raster
            'roughness_output' -- a file path for an output roughness raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import FocalStatistics
    from arcpy.sa import Int
    from arcpy.sa import NbrRectangle
    from arcpy.sa import Raster
    from arcpy.sa import Square

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Define a neighborhood variable
    neighborhood = NbrRectangle(5, 5, 'CELL')

    # Calculate the elevation standard deviation
    print('\t\tCalculating standard deviation of elevation...')
    standard_deviation = FocalStatistics(Raster(elevation_float), neighborhood, 'STD', 'DATA')

    # Calculate the square of standard deviation
    print('\t\tCalculating squared standard deviation...')
    roughness_raster = Square(standard_deviation)

    # Covert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int((roughness_raster * conversion_factor) + 0.5)

    # Export raster
    print('\t\tExporting wetness raster as 16 bit signed...')
    arcpy.management.CopyRaster(integer_raster,
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
