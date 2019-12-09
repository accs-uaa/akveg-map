# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Mean Slope
# Author: Timm Nawrocki
# Last Updated: 2019-12-07
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Mean Slope" is a function that calculates mean slope using a 3x3 cell window. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to calculate mean slope
def mean_slope(raw_slope, slope_output):
    """
    Description: calculates 32-bit float mean slope
    Inputs: 'raw_slope' -- an input raster digital elevation model
            'exposure_output' -- an output exposure raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input slope raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import FocalStatistics
    from arcpy.sa import NbrRectangle
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Define a neighborhood variable
    neighborhood = NbrRectangle(3, 3, "CELL")

    # Calculate mean slope from raw slope
    print('\t\tCalculating mean slope...')
    out_raster = FocalStatistics(Raster(raw_slope), neighborhood, 'MEAN', 'DATA')
    out_raster.save(slope_output)
