# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate integer elevation
# Author: Timm Nawrocki
# Last Updated: 2022-01-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate integer elevation" is a function that calculates integer elevation from float elevation.
# ---------------------------------------------------------------------------

# Define function to calculate integer elevation
def calculate_integer_elevation(area_raster, elevation_float, elevation_integer):
    """
    Description: calculates 16-bit signed elevation
    Inputs: 'area_raster' -- a raster of the study area to set snap raster and extract area
            'elevation_float' -- an input float elevation raster
            'elevation_integer' -- a file path for an output integer elevation raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires float input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import ExtractByMask
    from arcpy.sa import Int
    from arcpy.sa import Raster

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

    # Round to integer
    print(f'\t\tConverting values to integers...')
    integer_raster = Int(Raster(elevation_float) + 0.5)

    # Extract to area raster
    print('\t\tExtracting raster to area...')
    extract_integer = ExtractByMask(integer_raster, area_raster)

    # Copy extracted raster to output
    print(f'\t\tExporting integer elevation as 16-bit signed raster...')
    arcpy.management.CopyRaster(extract_integer,
                                elevation_integer,
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
