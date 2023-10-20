# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate slope
# Author: Timm Nawrocki
# Last Updated: 2023-10-19
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate slope" is a function that calculates float and integer slope in degrees.
# ---------------------------------------------------------------------------

# Define function to calculate slope
def calculate_slope(area_raster, elevation_float, z_unit, slope_float, slope_integer):
    """
    Description: calculates 32-bit float slope and 16-bit signed slope
    Inputs: 'area_raster' -- a raster of the study area to set snap raster and extract area
            'elevation_float' -- an input float elevation raster
            'z-unit' -- a string of the elevation unit
            'slope_raw' -- a file path for an output float slope raster in degrees
            'slope_output' -- a file path for an output integer slope raster in degrees
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires float input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Int
    from arcpy.sa import Raster
    from arcpy.sa import SurfaceParameters

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

    # Calculate raw slope
    print('\tCalculating raw slope...')
    slope_raster = SurfaceParameters(elevation_float,
                                     'SLOPE',
                                     'QUADRATIC',
                                     cell_size,
                                     'FIXED_NEIGHBORHOOD',
                                     z_unit,
                                     'DEGREE',
                                     'GEODESIC_AZIMUTHS',
                                     '')

    # Convert to integer
    print('\tConverting to integer...')
    integer_raster = Int(slope_raster + 0.5)

    # Extract to area raster
    print('\tExtracting raster to area...')
    extract_integer = ExtractByMask(integer_raster, area_raster)

    # Export rasters
    print('\tExporting slope as 32-bit float raster...')
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
    print('\tExporting slope as 16-bit integer raster...')
    arcpy.management.CopyRaster(extract_integer,
                                slope_integer,
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
