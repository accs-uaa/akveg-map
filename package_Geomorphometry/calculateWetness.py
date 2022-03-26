# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic wetness
# Author: Timm Nawrocki
# Last Updated: 2022-01-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate topographic wetness" is a function that calculates an index of topographic wetness. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate compound topographic index
def calculate_wetness(area_raster, elevation_float, flow_accumulation, slope_float, conversion_factor, wetness_output):
    """
    Description: calculates 16-bit signed topographic wetness
    Inputs: 'area_raster' -- a raster of the study area to set snap raster and extract area
            'elevation_float' -- an input float elevation raster
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
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Int
    from arcpy.sa import IsNull
    from arcpy.sa import Ln
    from arcpy.sa import Nibble
    from arcpy.sa import Raster
    from arcpy.sa import SetNull
    from arcpy.sa import Tan

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(elevation_float, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Convert degrees to radians
    print('\t\tConverting degrees to radians...')
    slope_radian = Raster(slope_float) * 0.0174533

    # Calculate slope tangent
    print('\t\tCalculating slope tangent...')
    slope_tangent = Con(slope_radian > 0, Tan(slope_radian), 0.001)

    # Correct flow accumulation
    print('\t\tModifying flow accumulation...')
    accumulation_corrected = (Raster(flow_accumulation) + 1) * float(cell_size)

    # Calculate compound topographic index as natural log of corrected flow accumulation divided by slope tangent
    print('\t\tCalculating compound topographic index...')
    wetness_raster = Ln(accumulation_corrected / slope_tangent)

    # Nibble wetness raster
    print('\t\tFilling missing values...')
    null_raster = SetNull(IsNull(wetness_raster), 1, '')
    filled_raster = Nibble(wetness_raster, null_raster, 'DATA_ONLY', 'PROCESS_NODATA', '')

    # Convert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int((filled_raster * conversion_factor) + 0.5)

    # Extract to area raster
    print('\t\tExtracting raster to area...')
    extract_integer = ExtractByMask(integer_raster, area_raster)

    # Export raster
    print('\t\tExporting wetness raster as 16-bit signed...')
    arcpy.management.CopyRaster(extract_integer,
                                wetness_output,
                                '',
                                '32767',
                                '-32768',
                                'NONE',
                                'NONE',
                                '16_BIT_SIGNED',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE')
