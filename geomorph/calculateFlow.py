# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate flow accumulation
# Author: Timm Nawrocki
# Last Updated: 2023-10-19
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate flow accumulation" is a function that calculates flow accumulation from a float elevation raster.
# ---------------------------------------------------------------------------

# Define function to calculate flow accumulation
def calculate_flow(area_raster, elevation_float, flow_direction, flow_accumulation):
    """
    Description: calculates 32-bit float flow direction and accumulation rasters
    Inputs: 'area_raster' -- a raster of the study area to set snap raster and extract area
            'elevation_float' -- an input float elevation raster
            'flow_accumulation' -- a file path for an output float flow direction raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires float input elevation raster
    """

    # Import packages
    import arcpy
    from arcpy.sa import DeriveContinuousFlow
    from arcpy.sa import FlowAccumulation
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

    # Calculate flow direction
    print('\tCalculating flow direction...')
    direction_raster = DeriveContinuousFlow(Raster(elevation_float), '', flow_direction, 'MFD', 'NORMAL')

    # Calculate flow accumulation
    print('\tCalculating flow accumulation...')
    accumulation_raster = FlowAccumulation(direction_raster, '', 'FLOAT', 'MFD')

    # Export final raster
    print('\tExporting flow direction raster as 32-bit float...')
    arcpy.management.CopyRaster(direction_raster,
                                flow_direction,
                                '',
                                '',
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
    print('\tExporting flow accumulation raster as 32-bit float...')
    arcpy.management.CopyRaster(accumulation_raster,
                                flow_accumulation,
                                '',
                                '',
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
