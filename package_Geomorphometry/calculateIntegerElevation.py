# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate integer elevation
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate integer elevation" is a function that calculates integer elevation from float elevation.
# ---------------------------------------------------------------------------

# Define function to calculate integer elevation
def calculate_integer_elevation(elevation_float, elevation_integer):
    """
    Description: calculates 16-bit signed elevation
    Inputs: 'elevation_float' -- an input float elevation raster
            'elevation_integer' -- a file path for an output integer elevation raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires float input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import Int
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Round to integer
    print(f'\t\tConverting values to integers...')
    integer_raster = Int(Raster(elevation_float) + 0.5)

    # Copy extracted raster to output
    print(f'\t\tExporting integer elevation as 16-bit signed raster...')
    arcpy.management.CopyRaster(integer_raster,
                                elevation_integer,
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
