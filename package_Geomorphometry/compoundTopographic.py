# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compound Topographic Index
# Author: Timm Nawrocki
# Last Updated: 2019-12-05
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Compound Topographic Index" is a function that calculates compound topographic index. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to calculate compound topographic index
def compound_topographic(elevation_input, flow_accumulation, raw_slope, cti_output):
    """
    Description: calculates 32-bit float compound topographic index
    Inputs: 'elevation_input' -- an input raster digital elevation model
            'flow_accumulation' -- an input flow accumulation raster with the same spatial reference as the elevation raster
            'raw_slope' -- an input raw slope raster in degrees with the same spatial reference as the elevation raster
            'cti_output' -- an output compound topographic index raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires input elevation, flow accumulation, and raw slope raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import Divide
    from arcpy.sa import Ln
    from arcpy.sa import Plus
    from arcpy.sa import Raster
    from arcpy.sa import Times
    from arcpy.sa import Tan

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Get spatial properties for the input elevation raster
    description = arcpy.Describe(elevation_input)
    cell_size = description.meanCellHeight

    # Convert degree slope to radian slope
    print('\t\tConverting degree slope to radians...')
    slope_radian = Divide(Times(Raster(raw_slope), 1.570796), 90)

    # Calculate slope tangent
    print('\t\tCalculating slope tangent...')
    slope_tangent = Con(slope_radian > 0, Tan(slope_radian), 0.001)

    # Correct flow accumulation
    print('\t\tModifying flow accumulation...')
    accumulation_corrected = Times(Plus(Raster(flow_accumulation), 1), cell_size)

    # Calculate compound topographic index as natural log of corrected flow accumulation divided by slope tangent
    print('\t\tCalculating compound topographic index...')
    out_raster = Ln(Divide(accumulation_corrected, slope_tangent))
    out_raster.save(cti_output)
