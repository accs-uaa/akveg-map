# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create modeling grids
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Create modeling grids" creates individual raster versions of the 50 x 50 km grids for use as modeling domains in prediction.
# ---------------------------------------------------------------------------

# Import packages
import os
import geopandas as gpd
import rasterio
from rasterio import features
import time
from akutils import *

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
source_geodatabase = os.path.join(drive, root_folder, 'AKVEG_Regions.gdb')
output_folder = os.path.join(drive, root_folder, 'Data_Input/grid_050')

# Define input files
grid_input = 'AlaskaYukon_050_Tiles_3338'

#### PROCESS MODELING GRIDS
####____________________________________________________

# Read grid feature class
grid_feature = gpd.read_file(source_geodatabase, layer=grid_input)
grid_feature['out_value'] = 1

# Define pixel_size and NoData value of new raster
pixel_size = 10
nodata = 255

# Export a raster for each grid
count = 1
for grid_code in grid_feature['grid_code']:
    # Define output file
    grid_output = os.path.join(output_folder, f'{grid_code}_10m_3338.tif')

    # Convert grid if grid raster does not already exist
    if os.path.exists(grid_output) == 0:
        print(f'Converting grid {count} out of {len(grid_feature)}...')
        iteration_start = time.time()

        # Parse target feature and geometry
        target_feature = grid_feature.query(f'grid_code=="{grid_code}"')
        geometry = [shapes for shapes in target_feature.geometry]

        # Prepare raster shape variables
        xmin, ymin, xmax, ymax = target_feature.total_bounds
        width = int((xmax - xmin) // pixel_size)
        height = int((ymax - ymin) // pixel_size)
        transform = rasterio.transform.from_origin(xmin, ymax, pixel_size, pixel_size)

        # Define shapes
        shapes = ((geom, value) for geom, value in zip(target_feature.geometry, target_feature.out_value))

        # Create raster in memory
        burned = features.rasterize(
            shapes=shapes,
            out_shape=(width, height),
            transform=transform,
            all_touched=True,
            dtype='uint8'
        )

        # Write raster to destination
        with rasterio.open(
            grid_output,
            mode='w',
            driver='GTiff',
            dtype='uint8',
            height=height,
            width=width,
            count=1,
            crs=target_feature.crs,
            transform=transform,
            compress='lzw',
            nodata=nodata,
            tiled=True,
            blockxsize=256,
            blockysize=256
        ) as dst:
            dst.write_band(1, burned)
        end_timing(iteration_start)

    else:
        # If grid raster already exists, continue to next grid
        print(f'Grid {count} of {len(grid_feature)} already exists.')
        print('----------')

    # Increase count
    count += 1
