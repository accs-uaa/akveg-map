# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate surface area ratio
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate surface area ratio" is a function that calculates surface area ratio. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate surface area ratio
def calculate_surface_area(slope_float, conversion_factor, area_output):
    """
    Description: calculates 16-bit signed surface area ratio
    Inputs: 'slope_float' -- an input float slope raster
            'conversion_factor' -- an integer to be multiplied with the output for conversion to integer raster
            'area_output' -- an output surface area ratio raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input float slope raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Cos
    from arcpy.sa import Float
    from arcpy.sa import Int
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Determine input cell size
    cell_x = arcpy.management.GetRasterProperties(slope_float, 'CELLSIZEX', '').getOutput(0)
    cell_y = arcpy.management.GetRasterProperties(slope_float, 'CELLSIZEY', '').getOutput(0)

    # Calculate cell area
    cell_area = cell_x * cell_y

    # Convert degrees to radians
    print('\t\tConverting degrees to radians...')
    slope_radian = Raster(slope_float) * 0.0174533

    # Calculate surface area ratio
    print('\t\tCalculating surface area ratio...')
    area_raster = Float(cell_area) / Cos(slope_radian)

    # Convert to integer
    print('\t\tConverting to integer...')
    integer_raster = Int((area_raster * conversion_factor) + 0.5)

    # Export raster
    print('\t\tExporting area raster as 16-bit signed...')
    arcpy.management.CopyRaster(integer_raster,
                                area_output,
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
