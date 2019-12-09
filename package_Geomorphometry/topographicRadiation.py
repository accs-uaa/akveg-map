# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Topographic Radation Aspect Index
# Author: Timm Nawrocki
# Last Updated: 2019-12-07
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Topographic Radiation Aspect Index" is a function that calculates a continuous index of topographic radiation using a 5x5 cell window from the coolest and wettest NNE aspects to the hottest and dryest SSW aspects. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to topographic radiation
def topographic_radiation(raw_aspect, radiation_output):
    """
    Description: calculates 32-bit float topographic radiation
    Inputs: 'raw_aspect' -- an input raw aspect raster
            'radiation_output' -- an output topographic radiation raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input raw aspect raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import Cos
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Calculate topographic radiation aspect index
    print('\t\tCalculating topographic radiation aspect index...')
    numerator = 1 - Cos((3.142 / 180) * (Raster(raw_aspect) - 30))
    radiation_index = numerator / 2

    # Convert negative aspect values
    print('\t\tConverting negative aspect values...')
    out_raster = Con(Raster(raw_aspect) < 0, 0.5, radiation_index)
    out_raster.save(radiation_output)
