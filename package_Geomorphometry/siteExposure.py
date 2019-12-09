# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Site Exposure
# Author: Timm Nawrocki
# Last Updated: 2019-12-06
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Site Exposure" is a function that calculates a continuous index of site exposure weighted by steepness of the slope. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to calculate site exposure
def site_exposure(raw_aspect, raw_slope, exposure_output):
    """
    Description: calculates 32-bit float site exposure
    Inputs: 'raw_aspect' -- an input raw aspect raster
            'raw_slope' -- an input raster digital elevation model
            'exposure_output' -- an output exposure raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input aspect and slope raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Cos
    from arcpy.sa import Divide
    from arcpy.sa import Minus
    from arcpy.sa import Raster
    from arcpy.sa import Times

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Calculate cosine of modified aspect
    print('\t\tCalculating cosine of modified aspect...')
    cosine = Cos(Divide(Times(3.142, Minus(Raster(raw_aspect), 180)), 180))

    # Calculate site exposure index and save output
    print('\t\tCalculating site exposure index...')
    out_raster = Times(Raster(raw_slope), cosine)
    out_raster.save(exposure_output)
