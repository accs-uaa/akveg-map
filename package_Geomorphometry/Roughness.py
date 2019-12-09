# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Roughness
# Author: Timm Nawrocki
# Last Updated: 2019-12-06
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Roughness" is a function that calculates roughness as the square of focal standard deviation using a 5x5 cell window. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to calculate roughness
def roughness(elevation_input, roughness_output):
    """
    Description: calculates 32-bit float roughness
    Inputs: 'elevation_input' -- an input raster digital elevation model
            'roughness_output' -- an output roughness raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import FocalStatistics
    from arcpy.sa import NbrRectangle
    from arcpy.sa import Raster
    from arcpy.sa import Square

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Define a neighborhood variable
    neighborhood = NbrRectangle(5, 5, "CELL")

    # Calculate the elevation standard deviation
    print('\t\tCalculating standard deviation...')
    standard_deviation = FocalStatistics(Raster(elevation_input), neighborhood, 'STD', 'DATA')

    # Calculate the square of standard deviation
    print('\t\tCalculating squared standard deviation...')
    out_raster = Square(standard_deviation)
    out_raster.save(roughness_output)
