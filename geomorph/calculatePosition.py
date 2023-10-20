# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic position
# Author: Timm Nawrocki
# Last Updated: 2023-10-19
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate topographic position" is a function that calculates a continuous index of topographic position using a user-defined window, ideally of multiple kilometers. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate topographic position
def calculate_position(area_raster, elevation_float, position_width, position_output):
    """
    Description: calculates 16-bit signed topographic position
    Inputs: 'area_raster' -- a raster of the study area to set snap raster and extract area
            'elevation_float' -- an input float elevation raster
            'position_width' -- a length in meters to define the axis length for a neighborhood square
            'position_output' -- a file path for an output topographic position raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
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

    # Determine neighborhood size
    axis_length = int(position_width / float(cell_size))

    # Define a neighborhood variable
    neighborhood = NbrRectangle(axis_length, axis_length, 'CELL')

    # Calculate focal mean
    print('\tCalculating focal mean...')
    focal_mean = FocalStatistics(elevation_float, neighborhood, 'MEAN', 'DATA')

    # Calculate topographic position
    print('\tCalculating topographic position...')
    position_raster = Raster(elevation_float) - focal_mean

    # Convert to integer
    print('\tConverting to integer...')
    integer_raster = Int(position_raster + 0.5)

    # Extract to area raster
    print('\tExtracting raster to area...')
    extract_integer = ExtractByMask(integer_raster, area_raster)

    # Export raster
    print('\tExporting position raster as 16-bit signed...')
    arcpy.management.CopyRaster(extract_integer,
                                position_output,
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
