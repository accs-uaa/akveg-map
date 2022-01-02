# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate surface relief ratio
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate surface relief ratio" is a function that calculates surface relief ratio using a 5x5 cell window. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate surface relief ratio
def calculate_surface_relief(elevation_float, conversion_factor, relief_output):
    """
    Description: calculates 16-bit signed surface relief ratio
    Inputs: 'elevation_float' -- an input float elevation raster
            'relief_output' -- an output surface relief ratio raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import Float
    from arcpy.sa import FocalStatistics
    from arcpy.sa import Int
    from arcpy.sa import NbrRectangle

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Define a neighborhood variable
    neighborhood = NbrRectangle(5, 5, "CELL")

    # Calculate focal minimum
    print('\t\tCalculating focal minimum...')
    focal_minimum = FocalStatistics(elevation_float, neighborhood, 'MINIMUM', 'DATA')

    # Calculate focal maximum
    print('\t\tCalculating focal maximum...')
    focal_maximum = FocalStatistics(elevation_float, neighborhood, 'MAXIMUM', 'DATA')

    # Calculate focal mean
    print('\t\tCalculating focal mean...')
    focal_mean = FocalStatistics(elevation_float, neighborhood, 'MEAN', 'DATA')

    # Calculate maximum drop
    print('\t\tCalculating maximum drop...')
    maximum_drop = Float(focal_maximum - focal_minimum)

    # Calculate standardized drop
    print('\t\tCalculating standardized drop...')
    standardized_drop = Float(focal_mean - focal_minimum) / maximum_drop

    # Calculate surface relief ratio
    print('\t\tCalculating surface relief ratio...')
    relief_raster = Con(maximum_drop == 0, 0, standardized_drop)

    # Convert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int((relief_raster * conversion_factor) + 0.5)

    # Export raster
    print('\t\tExporting relief raster as 16-bit signed...')
    arcpy.management.CopyRaster(integer_raster,
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
