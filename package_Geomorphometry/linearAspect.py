# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Linear Aspect
# Author: Timm Nawrocki
# Last Updated: 2019-12-05
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Linear Aspect" is a function that calculates aspect as a linear variable using a 3x3 cell window. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to calculate linear aspect
def linear_aspect(raw_aspect, aspect_output):
    """
    Description: calculates 32-bit float linear aspect
    Inputs: 'raw_aspect' -- an input raw aspect raster
            'aspect_output' -- an output linear aspect raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input DEM
    """

    # Import packages
    import arcpy
    from arcpy.sa import ATan2
    from arcpy.sa import Con
    from arcpy.sa import Cos
    from arcpy.sa import FocalStatistics
    from arcpy.sa import Mod
    from arcpy.sa import NbrRectangle
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    from arcpy.sa import Sin

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Define a neighborhood variable
    neighborhood = NbrRectangle(3, 3, "CELL")

    # Calculate aspect transformations
    print('\t\tTransforming raw aspect to linear aspect...')
    setNull_aspect = SetNull(Raster(raw_aspect) < 0, (450.0 - Raster(raw_aspect)) / 57.296)
    sin_aspect = Sin(setNull_aspect)
    cos_aspect = Cos(setNull_aspect)
    sum_sin = FocalStatistics(sin_aspect, neighborhood, "SUM", "DATA")
    sum_cos = FocalStatistics(cos_aspect, neighborhood, "SUM", "DATA")
    mod_aspect = Mod(((450 - (ATan2(sum_sin, sum_cos) * 57.296)) * 100), 36000) / 100 # The *100 and 36000(360*100) / 100 allow for two decimal points since Fmod appears to be gone
    out_raster = Con((sum_sin == 0) & (sum_cos == 0), -1, mod_aspect)

    # Save output raster file
    out_raster.save(aspect_output)
