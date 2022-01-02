# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate slope
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate slope" is a function that calculates float and integer slope in degrees.
# ---------------------------------------------------------------------------

# Define function to calculate slope
def calculate_slope(elevation_float, z_unit, slope_float, slope_integer):
    """
    Description: calculates 32-bit float slope and 16-bit signed slope
    Inputs: 'elevation_float' -- an input float elevation raster
            'slope_raw' -- a file path for an output float slope raster
            'slope_output' -- a file path for an output integer slope raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires float input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Int
    from arcpy.sa import SurfaceParameters

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Determine input cell size
    cell_size = arcpy.management.GetRasterProperties(elevation_float, 'CELLSIZEX', '').getOutput(0)

    # Calculate raw slope
    print('\t\tCalculating raw slope...')
    slope_raster = SurfaceParameters(elevation_float,
                                     'SLOPE',
                                     'QUADRATIC',
                                     cell_size,
                                     'FIXED_NEIGHBORHOOD',
                                     z_unit,
                                     'DEGREE',
                                     'GEODESIC_AZIMUTHS',
                                     'NORTH_POLE_ASPECT'
                                     )

    # Convert float to integer
    integer_raster = Int(slope_raster + 0.5)

    # Export rasters
    print('\t\tExporting slope as 32-bit float raster...')
    arcpy.management.CopyRaster(slope_raster,
                                slope_float,
                                '',
                                '0',
                                '-2147483648',
                                'NONE',
                                'NONE',
                                '32_BIT_FLOAT',
                                'NONE',
                                'NONE',
                                'TIFF',
                                'NONE',
                                'CURRENT_SLICE',
                                'NO_TRANSPOSE')
    print('\t\tExporting slope as 16-bit integer raster...')
    arcpy.management.CopyRaster(integer_raster,
                                slope_integer,
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
