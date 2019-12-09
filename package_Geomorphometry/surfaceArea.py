# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Surface Area Ratio
# Author: Timm Nawrocki
# Last Updated: 2019-12-07
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Surface Area Ratio" is a function that calculates surface area ratio. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to surface area ratio
def surface_area(raw_slope, area_output):
    """
    Description: calculates 32-bit float surface area ratio
    Inputs: 'raw_slope' -- an input raw slope raster
            'roughness_output' -- an output roughness raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Cos
    from arcpy.sa import Float
    from arcpy.sa import Raster
    import math

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Getting info on raster
    description = arcpy.Describe(raw_slope)
    cell_size = description.meanCellHeight

    # Set the cell size environment
    arcpy.env.cellSize = cell_size

    # Calculate cell area
    cell_area = cell_size * cell_size

    # Modify raw slope
    print('\t\tModifying raw slope...')
    modifier = math.pi / 180
    modified_slope = Raster(raw_slope) * modifier

    # Calculate surface area ratio
    print('\t\tCalculating surface area ratio...')
    out_raster = Float(cell_area) / Cos(modified_slope)
    out_raster.save(area_output)
