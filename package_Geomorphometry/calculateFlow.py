# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate flow accumulation
# Author: Timm Nawrocki
# Last Updated: 2022-01-01
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate flow accumulation" is a function that calculates flow accumulation from a float elevation raster.
# ---------------------------------------------------------------------------

# Define function to calculate flow accumulation
def calculate_flow(elevation_float, flow_accumulation):
    """
    Description: calculates 32-bit float flow direction and accumulation rasters
    Inputs: 'elevation_float' -- an input float elevation raster
            'flow_accumulation' -- a file path for an output float flow direction raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires float input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import FlowAccumulation
    from arcpy.sa import FlowDirection
    from arcpy.sa import Raster

    # Set overwrite option
    arcpy.env.overwriteOutput = True

    # Calculate flow direction
    print('\t\tCalculating flow direction...')
    direction_raster = FlowDirection(Raster(elevation_float), 'NORMAL', '', 'DINF')

    # Calculate flow accumulation
    print('\t\tCalculating flow accumulation...')
    accumulation_raster = FlowAccumulation(direction_raster, '', 'FLOAT', 'DINF')

    # Export final raster
    print('\t\tExporting flow accumulation raster as 32-bit float...')
    arcpy.management.CopyRaster(accumulation_raster,
                                flow_accumulation,
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
