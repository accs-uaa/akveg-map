import os
import glob
import subprocess
import shutil
import argparse
from pathlib import Path

"""
200_ortho_pgc_warp.py

Description:
    Orthorectifies Maxar NTF/TIF imagery using gdalwarp with RPCs and a reference DEM.
    Critically, it copies the source metadata (XML/IMD) to the output filename
    so that downstream TOA calibration scripts can find the coefficients.
    
    This replaces the complex pgc_ortho.py wrapper with a direct gdalwarp call
    that mimics the PGC geometric approach.

Usage Example:
    python 200_ortho_pgc_warp.py \
        --input "/data/gis/raster_base/Alaska/AKVegMap/EVWHS/navy_north_slope/unzipped/050300601010_01" \
        --output "/data/gis/raster_base/Alaska/AKVegMap/EVWHS/navy_north_slope/processed_output/01_ortho" \
        --dem "/data/gis/gis_base/DEM/ifsar/wgs1984_ellipsoid_height/alaska_ifsar_dsm_20200925_plus_us_noaa_g2009.tif" \
        --epsg 3338 \
        --threads 20 \
        --overwrite
"""

def find_metadata_file(image_path):
    """
    Finds the associated XML or IMD file for a given image.
    Prioritizes XML, then IMD.
    """
    base = os.path.splitext(image_path)[0]
    # Check for .xml, .XML, .imd, .IMD
    # Also handle the case where image is .NTF but metadata is .XML
    for ext in ['.xml', '.XML', '.imd', '.IMD']:
        if os.path.exists(base + ext):
            return base + ext
    return None

def add_overviews_and_stats(filepath, threads=1):
    """
    Adds internal overviews and calculates approximate stats for quick visualization.
    """
    print(f"  Adding overviews and stats for {os.path.basename(filepath)}...")
    
    # 1. Overviews (Internal, fast levels only)
    # 2, 4, 8, 16 is usually enough for quick checking. 
    # Use -r average for better visual quality or nearest for speed.
    try:
        subprocess.check_call([
            "gdaladdo", 
            "-r", "average", 
            "--config", "COMPRESS_OVERVIEW", "DEFLATE",
            "--config", "PREDICTOR_OVERVIEW", "2",
            "--config", "GDAL_NUM_THREADS", str(threads),
            "-ro", # open read-only (though actually we are modifying it, this flag sometimes safer with separate .ovr, but we want internal if possible. gdaladdo defaults to internal if GTiff)
            filepath, 
            "2", "4", "8", "16"
        ])
    except subprocess.CalledProcessError:
        print("    Error creating overviews.")

    # 2. Approximate Stats
    # gdalinfo -stats uses -approx_stats logic often by default on large files unless -mm is used, 
    # but explicit -stats triggers calculation.
    # Note: gdalinfo prints to stdout, we just want the side effect of the PAM .aux.xml being created/updated
    try:
        subprocess.call(
            ["gdalinfo", "-stats", filepath], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
    except Exception:
        print("    Error calculating stats.")

def run_ortho(input_file, output_file, dem_path, epsg=None, resolution=None, resampling="cubic", overwrite=False, threads=16):
    """
    Runs gdalwarp to orthorectify the image.
    """
    
    # 1. Construct gdalwarp command
    # -rpc: Use RPCs from input
    # -to RPC_DEM=...: The critical PGC flag to use the DEM for RPC correction
    # -dstnodata 0: Ensure background is 0
    # -co COMPRESS=DEFLATE: Better compression for final archive
    # -co PREDICTOR=2: Horizontal differencing (good for imagery)
    # -co BIGTIFF=IF_NEEDED: Prevent 4GB limit errors
    # -multi: Enable multithreaded I/O
    # -wo NUM_THREADS=...: Use specified cores for warping
    # -wm 2048: Use 2GB of RAM for warping buffer
    
    cmd = [
        "gdalwarp",
        "-rpc", 
        "-to", f"RPC_DEM={dem_path}",
        "-dstnodata", "0",
        "-multi",
        "-wo", f"NUM_THREADS={threads}",
        "-wm", "2048",
        "-co", "COMPRESS=DEFLATE",
        "-co", "PREDICTOR=2",
        "-co", "BIGTIFF=IF_NEEDED",
        "-co", "TILED=YES",
        "-co", f"NUM_THREADS={threads}",
        "-co", "PHOTOMETRIC=MINISBLACK",
        "-r", resampling,
        input_file,
        output_file
    ]

    # Add Target SRS if provided (e.g. EPSG:3338)
    if epsg:
        cmd.extend(["-t_srs", f"EPSG:{epsg}"])

    # Add resolution override if provided (e.g., ensure MS is 2m, Pan is 0.5m)
    if resolution:
        cmd.extend(["-tr", str(resolution), str(resolution)])

    # Pass overwrite flag to gdalwarp
    if overwrite:
        cmd.append("-overwrite")

    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error orthorectifying {input_file}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Orthorectify Maxar Imagery (PGC Style)")
    parser.add_argument("--input", required=True, help="Input folder containing NTF/TIF files")
    parser.add_argument("--output", required=True, help="Output folder for Orthos")
    parser.add_argument("--dem", required=True, help="Path to the DEM (Mosaic or VRT)")
    parser.add_argument("--epsg", help="Target EPSG code (e.g. 3338). Defaults to WGS84 if not set.", default=None)
    parser.add_argument("--threads", type=int, default=16, help="Number of threads to use for gdalwarp. Default is 16.")
    parser.add_argument("--res-pan", type=float, help="Output resolution for PAN images (meters)")
    parser.add_argument("--res-ms", type=float, help="Output resolution for MS images (meters)")
    parser.add_argument("--resampling", default="cubic", help="Resampling method (nearest, bilinear, cubic, cubicspline, lanczos, average). Default: cubic")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Find images (recursive)
    extensions = ["*.ntf", "*.NTF", "*.tif", "*.TIF"]
    images = []
    for ext in extensions:
        images.extend(list(Path(args.input).rglob(ext)))

    print(f"Found {len(images)} images to process.")

    for img_path in images:
        img_path = str(img_path)
        
        # Skip existing orthos, overviews, or intermediate files
        if "ortho" in img_path or "ovr" in img_path or "aux" in img_path:
            continue

        filename = os.path.basename(img_path)
        
        # Determine output filename suffix based on type
        lower_name = filename.lower()
        if "pan" in lower_name or "-p" in lower_name:
             out_name = os.path.splitext(filename)[0] + "_ortho_pan.tif"
             res = args.res_pan # Use override or None (native)
        elif "ms" in lower_name or "-m" in lower_name:
             out_name = os.path.splitext(filename)[0] + "_ortho_ms.tif"
             res = args.res_ms # Use override or None (native)
        else:
             # Default fallback
             out_name = os.path.splitext(filename)[0] + "_ortho.tif"
             res = None

        out_path = os.path.join(args.output, out_name)

        # Skip if exists
        if os.path.exists(out_path) and not args.overwrite:
            print(f"Skipping {out_name}, already exists.")
            continue

        # ORTHO
        success = run_ortho(img_path, out_path, args.dem, epsg=args.epsg, resolution=res, resampling=args.resampling, overwrite=args.overwrite, threads=args.threads)

        # COPY METADATA
        if success:
            meta_src = find_metadata_file(img_path)
            if meta_src:
                meta_ext = os.path.splitext(meta_src)[1]
                meta_dst = os.path.splitext(out_path)[0] + meta_ext
                shutil.copy2(meta_src, meta_dst)
                print(f"Copied metadata to {meta_dst}")
            else:
                print(f"WARNING: No XML/IMD found for {filename}. TOA step will fail for this image.")
            
            # ADD OVERVIEWS AND STATS
            add_overviews_and_stats(out_path, threads=args.threads)

if __name__ == "__main__":
    main()