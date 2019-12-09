# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Integrated Moisture Index
# Author: Timm Nawrocki
# Last Updated: 2019-12-06
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Compound Topographic Index" is a function that calculates compound topographic index. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to calculate integrated moisture index
def integrated_moisture(elevation_input, flow_accumulation, zFactor, imi_output):
    """
    Description: calculates 32-bit float integrated moisture index
    Inputs: elevation_input' -- an input raster digital elevation model
            'flow_accumulation' -- an input flow accumulation raster with the same spatial reference as the elevation raster
            'zFactor' -- a unit scaling factor for calculations that involve comparisons of xy to z
            'imi_output' -- an output compound topographic index raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires input elevation,
    """

    # Import packages
    import arcpy
    from arcpy.sa import Curvature
    from arcpy.sa import Hillshade
    from arcpy.sa import Plus
    from arcpy.sa import Times
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Adjust flow accumulation
    print('\t\tScaling flow accumulation...')
    adjusted_accumulation = Times(Raster(flow_accumulation), 0.35)

    # Calculate and adjust curvature
    print('\t\tCalculating curvature...')
    curvature = Curvature(Raster(elevation_input), zFactor)
    adjusted_curvature = Times(curvature, 0.15)

    # Calculate and adjust hillshade
    print('\t\tCalculating hillshade...')
    hillshade = Hillshade(Raster(elevation_input), "#", "#", "#", zFactor)
    adjusted_hillshade = Times(hillshade, 0.5)

    # Calculate integrated moisture index
    out_raster = Plus(Plus(adjusted_accumulation, adjusted_curvature), adjusted_hillshade)
    out_raster.save(imi_output)
