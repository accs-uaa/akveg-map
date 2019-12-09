# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Topographic Position
# Author: Timm Nawrocki
# Last Updated: 2019-12-07
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Topographic Position" is a function that calculates a continuous index of topographic position using a 5x5 cell window. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to topographic position
def topographic_position(elevation_input, position_output):
    """
    Description: calculates 32-bit float topographic position
    Inputs: 'elevation_input' -- an input raster digital elevation model
            'relief_output' -- an output surface relief ratio raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import FocalStatistics
    from arcpy.sa import NbrRectangle
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Define a neighborhood variable
    neighborhood = NbrRectangle(5, 5, "CELL")

    # Calculate local mean
    print('\t\tCalculating local mean...')
    local_mean = FocalStatistics(elevation_input, neighborhood, 'MEAN', 'DATA')

    # Calculate topographic position
    print('\t\tCalculating topographic position...')
    out_raster = Raster(elevation_input) - local_mean
    out_raster.save(position_output)