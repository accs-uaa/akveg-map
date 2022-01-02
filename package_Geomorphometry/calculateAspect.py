# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate aspect
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate aspect" is a function that calculates raw and linear aspect. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics.
# ---------------------------------------------------------------------------

# Define function to calculate aspect
def calculate_aspect(elevation_float, z_unit, aspect_raw, aspect_output):
    """
    Description: calculates 32-bit float raw aspect and 16-bit signed linear aspect
    Inputs: 'elevation_float' -- an input float elevation raster
            'aspect_raw' -- a file path for an output float raw aspect raster
            'aspect_output' -- a file path for an output integer linear aspect raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires float input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import SurfaceParameters
    from arcpy.sa import ATan2
    from arcpy.sa import Con
    from arcpy.sa import Cos
    from arcpy.sa import FocalStatistics
    from arcpy.sa import Mod
    from arcpy.sa import NbrRectangle
    from arcpy.sa import SetNull
    from arcpy.sa import Sin
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Determine input cell size
    cell_size = arcpy.management.GetRasterProperties(elevation_float, 'CELLSIZEX', '').getOutput(0)

    # Define neighborhood
    neighborhood = NbrRectangle(3, 3, 'CELL')

    # Calculate raw aspect in degrees
    print('\t\tCalculating raw aspect...')
    aspect_raster = SurfaceParameters(elevation_float,
                                      'ASPECT',
                                      'QUADRATIC',
                                      cell_size,
                                      'FIXED_NEIGHBORHOOD',
                                      z_unit,
                                      '',
                                      'GEODESIC_AZIMUTHS',
                                      'NORTH_POLE_ASPECT'
                                      )

    # Convert degrees to radians
    print('\t\tConverting degrees to radians...')
    aspect_radian = Raster(aspect_raster) * 0.0174533

    # Calculate linear aspect
    print('\t\tCalculating linear aspect...')
    null_aspect = SetNull(aspect_radian < 0, (7.8539514 - aspect_radian), '')
    sin_aspect = Sin(null_aspect)
    cos_aspect = Cos(null_aspect)
    sin_sum = FocalStatistics(sin_aspect, neighborhood, 'SUM', 'DATA')
    cos_sum = FocalStatistics(cos_aspect, neighborhood, 'SUM', 'DATA')
    mod_aspect = Mod(((450 - (ATan2(sin_sum, cos_sum) * 57.296)) * 100), 36000) / 100
    linear_aspect = Con((sin_sum == 0) & (cos_sum == 0), -1, mod_aspect)

    # Export rasters
    print('\t\tExporting raw aspect as 32-bit float raster...')
    arcpy.management.CopyRaster(aspect_raster,
                                aspect_raw,
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
    print('\t\tExporting linear aspect as 16-bit integer raster...')
    arcpy.management.CopyRaster(linear_aspect,
                                aspect_output,
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
