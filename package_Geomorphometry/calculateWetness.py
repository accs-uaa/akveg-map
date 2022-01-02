# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic wetness
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate topographic wetness" is a function that calculates an index of topographic wetness. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate compound topographic index
def calculate_wetness(elevation_float, flow_accumulation, slope_float, conversion_factor, wetness_output):
    """
    Description: calculates 16-bit signed topographic wetness
    Inputs: 'elevation_float' -- an input float elevation raster
            'flow_accumulation' -- an input flow accumulation raster
            'slope_float' -- an input float slope raster in degrees
            'conversion_factor' -- an integer to be multiplied with the output for conversion to integer raster
            'wetness_output' -- a file path for an output topographic wetness raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires input elevation, flow accumulation, and raw slope raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import Int
    from arcpy.sa import Ln
    from arcpy.sa import Raster
    from arcpy.sa import Tan

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Determine input cell size
    cell_size = arcpy.management.GetRasterProperties(elevation_float, 'CELLSIZEX', '').getOutput(0)

    # Convert degrees to radians
    print('\t\tConverting degrees to radians...')
    slope_radian = Raster(slope_float) * 0.0174533

    # Calculate slope tangent
    print('\t\tCalculating slope tangent...')
    slope_tangent = Con(slope_radian > 0, Tan(slope_radian), 0.001)

    # Correct flow accumulation
    print('\t\tModifying flow accumulation...')
    accumulation_corrected = (Raster(flow_accumulation) + 1) * cell_size

    # Calculate compound topographic index as natural log of corrected flow accumulation divided by slope tangent
    print('\t\tCalculating compound topographic index...')
    wetness_raster = Ln(accumulation_corrected / slope_tangent)

    # Convert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int((wetness_raster * conversion_factor) + 0.5)

    # Export raster
    print('\t\tExporting wetness raster as 16-bit signed...')
    arcpy.management.CopyRaster(integer_raster,
                                wetness_output,
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
