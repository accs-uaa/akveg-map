# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge Elevation Datasets
# Author: Timm Nawrocki
# Created on: 2019-10-29
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Merge Elevation Datasets" creates a composite from multiple sources based on order of priority. All sources must be in the same projection with the same cell size and grid.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from arcpy.sa import ExtractByMask
import pandas as pd
import os
from beringianGeospatialProcessing import arcpy_geoprocessing

# Set root directory
drive = 'K:/'
root_directory = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define input datasets
raster_csv = os.path.join(drive, 'ACCS_Work/Data/elevation/NorthAmericanBeringia_10m/Raster_Inputs.csv')
major_grids = os.path.join(root_directory, 'Analysis_GridMajor.gdb')
snap_raster = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/areaOfInterest_Initial.tif')

# Read raster file paths from csv
raster_df = pd.read_csv(raster_csv)
raster_paths = list(raster_df.file_path)
raster_names = list(raster_df.name)

# Define folder paths
major_folder = os.path.join(root_directory, 'Data_Input/majorGrid')
elevation_inputs = os.path.join(drive, 'ACCS_Work/Data/elevation/NorthAmericanBeringia_10m/inputs')
elevation_outputs = os.path.join(drive, 'ACCS_Work/Data/elevation/NorthAmerican')

# Set overwrite option
arcpy.env.overwriteOutput = True

# Set snap raster
arcpy.env.snapRaster = snap_raster

# List grid rasters
grids = arcpy.ListRasters('*', 'TIF')

# Iterate through each buffered grid and extract each elevation input
for grid in grids:
    for raster in raster_paths:
        output_folder = os.path.join()
        try:
            outExtract = ExtractByMask(raster, grid)
            arcpy.CopyRaster_management(outExtract, )


# Extract by mask each elevation dataset to the grid
# Mosaic rasters based on order of priority


