import os
import sys
import fiona
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.enums import Resampling
import numpy as np

# --- DEBUG: Verify Start ---
print("--- Script Starting ---")

# --- CONFIGURATION ---
# Path to your File Geodatabase (Linux format)
# GDB_PATH = "/data/gis/gis_projects/2024/24-261_AKVEG_Riparian_BLM/AKVEG_Floodplains_20251215.gdb"
GDB_PATH = "/data/gis/gis_projects/2024/24-261_AKVEG_Riparian_BLM/AKVEG_Floodplains_20260114.gdb"

# Reference raster for pixel alignment (The Sentinel-2 Mosaic)
REFERENCE_RASTER = "/data/gis/raster_base/Alaska/AKVegMap/deliverable/20250528_mentasta_lake_24-241/adnr_fireexposure_ph1_v1.0/surficial_features/MentastaLake_FloodedVeg_Pct_10m_3338.tif"

# Output location for the rasterized labels
OUTPUT_DIR = "/data/gis/gis_projects/2024/24-261_AKVEG_Riparian_BLM/label_rasters/v20260114"

# --- VALIDATION CHECKS ---
if not os.path.exists(GDB_PATH):
    print(f"\nCRITICAL ERROR: GDB Path not found: {GDB_PATH}")
    print("Check your mount points or spelling.")
    sys.exit(1)

if not os.path.exists(REFERENCE_RASTER):
    print(f"\nCRITICAL ERROR: Reference Raster not found: {REFERENCE_RASTER}")
    sys.exit(1)

print(f"Paths verified.\nGDB: {GDB_PATH}\nRef: {REFERENCE_RASTER}")

def find_pairs_in_gdb(gdb_path):
    """
    Scans a GDB for matching 'TrainingArea' and 'Floodplains' layers.
    Assumes naming convention: [Prefix]_TrainingArea... and [Prefix]_Floodplains...
    """
    print(f"Scanning GDB layers...")
    try:
        layers = fiona.listlayers(gdb_path)
    except Exception as e:
        print(f"Error reading GDB: {e}")
        return {}

    training_layers = {}
    floodplain_layers = {}
    
    # 1. Categorize layers
    for layer in layers:
        if "TrainingArea" in layer:
            # key = "AlphabetHills" derived from "AlphabetHills_TrainingArea_3338"
            key = layer.split("_TrainingArea")[0]
            training_layers[key] = layer
        elif "Floodplains" in layer:
            # key = "AlphabetHills" derived from "AlphabetHills_Floodplains_3338"
            key = layer.split("_Floodplains")[0]
            floodplain_layers[key] = layer
            
    # 2. Match pairs
    pairs = {}
    for key, train_layer in training_layers.items():
        if key in floodplain_layers:
            pairs[key] = (train_layer, floodplain_layers[key])
        else:
            print(f"Warning: Found Training Area '{train_layer}' but no matching Floodplains layer.")
            
    print(f"Found {len(pairs)} matched pairs.")
    return pairs

def create_label_raster(area_id, gdb_path, train_layer_name, flood_layer_name, ref_path):
    print(f"Processing {area_id}...")
    
    # 1. Load Reference Info
    with rasterio.open(ref_path) as src:
        ref_meta = src.meta.copy()
        ref_transform = src.transform
        ref_crs = src.crs

    # 2. Load Vectors from GDB
    try:
        train_gdf = gpd.read_file(gdb_path, layer=train_layer_name)
        flood_gdf = gpd.read_file(gdb_path, layer=flood_layer_name)
    except Exception as e:
        print(f"Failed to load layers for {area_id}: {e}")
        return

    # Reproject if necessary
    if train_gdf.crs != ref_crs:
        train_gdf = train_gdf.to_crs(ref_crs)
    if flood_gdf.crs != ref_crs:
        flood_gdf = flood_gdf.to_crs(ref_crs)

    if train_gdf.empty:
        print(f"Skipping {area_id}: Training area is empty.")
        return

    # --- NEW: Clip Floodplains to Training Area ---
    # Ensure we only burn floodplains that are strictly inside the training area.
    # This prevents marking 'Riparian' (1) in areas that should be 'NoData' (255)
    # just because they are inside the bounding box.
    if not flood_gdf.empty:
        try:
            flood_gdf = gpd.clip(flood_gdf, train_gdf)
        except Exception as e:
            print(f"  Warning: Clip failed for {area_id} ({e}). Proceeding unclipped.")

    # 3. Determine Bounds of this specific Training Area
    minx, miny, maxx, maxy = train_gdf.total_bounds
    
    # Align bounds to the reference grid (snap to pixel grid)
    res = ref_transform[0] 
    
    minx = np.floor(minx / res) * res
    maxx = np.ceil(maxx / res) * res
    miny = np.floor(miny / res) * res
    maxy = np.ceil(maxy / res) * res
    
    width = int((maxx - minx) / res)
    height = int((maxy - miny) / res)
    
    # Create new transform for this specific chip
    new_transform = from_origin(minx, maxy, res, res)

    # 4. Rasterize
    # Initialize with 255 (NoData) and use uint8 for efficient storage
    label_arr = np.full((height, width), 255, dtype=np.uint8)
    
    # Burn Background (0) - The Training Area Extent
    train_shapes = ((geom, 0) for geom in train_gdf.geometry)
    rasterize(train_shapes, out=label_arr, transform=new_transform, default_value=0)
    
    # Burn Foreground (1) - The Floodplains
    if not flood_gdf.empty:
        flood_shapes = ((geom, 1) for geom in flood_gdf.geometry)
        rasterize(flood_shapes, out=label_arr, transform=new_transform, default_value=1)

    # 5. Save as Tiled GeoTIFF (COG compatible)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{area_id}_labels.tif")
    
    ref_meta.update({
        "driver": "GTiff",
        "height": height,
        "width": width,
        "transform": new_transform,
        "count": 1,
        "dtype": "uint8",
        "nodata": 255,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256
    })
    
    with rasterio.open(out_path, "w", **ref_meta) as dst:
        dst.write(label_arr, 1)
        
        # Write Colormap
        # 0: Tan (Upland), 1: Bluish Green (Riparian), 255: Transparent
        dst.write_colormap(1, {
            0: (210, 180, 140, 255),   # Tan
            1: (0, 168, 107, 255),     # Bluish Green
            255: (0, 0, 0, 0)          # Transparent
        })

        # Build overviews (pyramids) with mode resampling (best for discrete classes)
        dst.build_overviews([2, 4, 8, 16], Resampling.mode)
        dst.update_tags(ns='rio_overview', resampling='mode')
        
    print(f"  Saved: {out_path}")

if __name__ == "__main__":
    # 1. Scan the GDB
    pairs = find_pairs_in_gdb(GDB_PATH)
    
    # 2. Process each pair
    for area_id, (train_layer, flood_layer) in pairs.items():
        create_label_raster(area_id, GDB_PATH, train_layer, flood_layer, REFERENCE_RASTER)
    
    if pairs:
        print("\nNext Steps:")
        print(f"1. Build a VRT: gdalbuildvrt labels.vrt {OUTPUT_DIR}/*.tif")
        print("2. Use this 'labels.vrt' in your train_riparian.py config.")
    else:
        print("No matching pairs found. Check your layer naming convention.")