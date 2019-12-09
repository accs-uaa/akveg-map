# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Surface Relief Ratio
# Author: Timm Nawrocki
# Last Updated: 2019-12-07
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Surface Relief Ratio" is a function that calculates surface relief ratio using a 5x5 cell window. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to surface relief ratio
def surface_relief(elevation_input, relief_output):
    """
    Description: calculates 32-bit float surface relief ratio
    Inputs: 'elevation_input' -- an input raster digital elevation model
            'relief_output' -- an output surface relief ratio raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import Float
    from arcpy.sa import FocalStatistics
    from arcpy.sa import NbrRectangle

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Define a neighborhood variable
    neighborhood = NbrRectangle(5, 5, "CELL")

    # Calculate local minimum
    print('\t\tCalculating local minimum...')
    local_minimum = FocalStatistics(elevation_input, neighborhood, 'MINIMUM', 'DATA')

    # Calculate local maximum
    print('\t\tCalculating local maximum...')
    local_maximum = FocalStatistics(elevation_input, neighborhood, 'MAXIMUM', 'DATA')

    # Calculate local mean
    print('\t\tCalculating local mean...')
    local_mean = FocalStatistics(elevation_input, neighborhood, 'MEAN', 'DATA')

    # Calculate maximum drop
    print('\t\tCalculating maximum drop...')
    maximum_drop = Float(local_maximum - local_minimum)

    # Calculate standardized drop
    print('\t\tCalculating standardized drop...')
    standardized_drop = Float(local_mean - local_minimum) / maximum_drop

    # Calculate surface relief ratio
    print('\t\tCalculating surface relief ratio...')
    out_raster = Con(maximum_drop == 0, 0, standardized_drop)
    out_raster.save(relief_output)
