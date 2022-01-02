# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic position
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate topographic position" is a function that calculates a continuous index of topographic position using a user-defined window, ideally of multiple kilometers. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate topographic position
def calculate_position(elevation_float, position_width, position_output):
    """
    Description: calculates 16-bit signed topographic position
    Inputs: 'elevation_float' -- an input float elevation raster
            'position_width' -- a length in meters to define the axis length for a neighborhood square
            'position_output' -- a file path for an output topographic position raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import FocalStatistics
    from arcpy.sa import Int
    from arcpy.sa import NbrRectangle
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Determine input cell size
    cell_size = arcpy.management.GetRasterProperties(elevation_float, 'CELLSIZEX', '').getOutput(0)

    # Determine neighborhood size
    axis_length = int(position_width/cell_size)

    # Define a neighborhood variable
    neighborhood = NbrRectangle(axis_length, axis_length, 'CELL')

    # Calculate focal mean
    print('\t\tCalculating focal mean...')
    focal_mean = FocalStatistics(elevation_float, neighborhood, 'MEAN', 'DATA')

    # Calculate topographic position
    print('\t\tCalculating topographic position...')
    position_raster = Raster(elevation_float) - focal_mean

    # Convert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int(position_raster + 0.5)

    # Export raster
    print('\t\tExporting position raster as 16-bit signed...')
    arcpy.management.CopyRaster(integer_raster,
                                position_output,
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
