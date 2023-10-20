# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate surface relief ratio
# Author: Timm Nawrocki
# Last Updated: 2023-10-19
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate surface relief ratio" is a function that calculates surface relief ratio using a 5x5 cell window. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate surface relief ratio
def calculate_surface_relief(area_raster, elevation_float, conversion_factor, relief_output):
    """
    Description: calculates 16-bit signed surface relief ratio
    Inputs: 'area_raster' -- a raster of the study area to set snap raster and extract area
            'elevation_float' -- an input float elevation raster
            'relief_output' -- an output surface relief ratio raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Con
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Float
    from arcpy.sa import FocalStatistics
    from arcpy.sa import Int
    from arcpy.sa import NbrRectangle
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Specify core usage
    arcpy.env.parallelProcessingFactor = "75%"

    # Set snap raster and extent
    arcpy.env.snapRaster = area_raster
    arcpy.env.extent = Raster(area_raster).extent

    # Set cell size environment
    cell_size = arcpy.management.GetRasterProperties(area_raster, 'CELLSIZEX', '').getOutput(0)
    arcpy.env.cellSize = int(cell_size)

    # Define a neighborhood variable
    neighborhood = NbrRectangle(5, 5, "CELL")

    # Calculate focal minimum
    print('\tCalculating focal minimum...')
    focal_minimum = FocalStatistics(elevation_float, neighborhood, 'MINIMUM', 'DATA')

    # Calculate focal maximum
    print('\tCalculating focal maximum...')
    focal_maximum = FocalStatistics(elevation_float, neighborhood, 'MAXIMUM', 'DATA')

    # Calculate focal mean
    print('\tCalculating focal mean...')
    focal_mean = FocalStatistics(elevation_float, neighborhood, 'MEAN', 'DATA')

    # Calculate maximum drop
    print('\tCalculating maximum drop...')
    maximum_drop = Float(focal_maximum - focal_minimum)

    # Calculate standardized drop
    print('\tCalculating standardized drop...')
    standardized_drop = Float(focal_mean - focal_minimum) / maximum_drop

    # Calculate surface relief ratio
    print('\tCalculating surface relief ratio...')
    relief_raster = Con(maximum_drop == 0, 0, standardized_drop)

    # Convert to integer
    print('\tConverting to integer...')
    integer_raster = Int((relief_raster * conversion_factor) + 0.5)

    # Extract to area raster
    print('\tExtracting raster to area...')
    extract_integer = ExtractByMask(integer_raster, area_raster)

    # Export raster
    print('\tExporting relief raster as 16-bit signed...')
    arcpy.management.CopyRaster(extract_integer,
                                relief_output,
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
