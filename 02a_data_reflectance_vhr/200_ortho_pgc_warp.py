import os
import glob
import subprocess
import shutil
import argparse
from pathlib import Path

"""
200_ortho_pgc_wrap.py

Description:
    Orthorectifies Maxar NTF/TIF imagery using gdalwarp with RPCs and a reference DEM.
    Critically, it copies the source metadata (XML/IMD) to the output filename
    so that downstream TOA calibration scripts can find the coefficients.
    
    This replaces the complex pgc_ortho.py wrapper with a direct gdalwarp call
    that mimics the PGC geometric approach.

Usage:
    python 200_ortho_pgc_wrap.py --input /path/to/raw --output /path/to/ortho --dem /path/to/dem.tif
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

def run_ortho(input_file, output_file, dem_path, resolution=None, resampling="cubic"):
    """
    Runs gdalwarp to orthorectify the image.
    """
    
    # 1. Construct gdalwarp command
    # -rpc: Use RPCs from input
    # -to RPC_DEM=...: The critical PGC flag to use the DEM for RPC correction
    # -dstnodata 0: Ensure background is 0
    # -co COMPRESS=LZW: Save space
    # -co BIGTIFF=IF_NEEDED: Prevent 4GB limit errors
    
    cmd = [
        "gdalwarp",
        "-rpc", 
        "-to", f"RPC_DEM={dem_path}",
        "-dstnodata", "0",
        "-co", "COMPRESS=LZW",
        "-co", "BIGTIFF=IF_NEEDED",
        "-co", "TILED=YES",
        "-r", resampling,
        input_file,
        output_file
    ]

    # Add resolution override if provided (e.g., ensure MS is 2m, Pan is 0.5m)
    if resolution:
        cmd.extend(["-tr", str(resolution), str(resolution)])

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
        # Heuristic: Multispectral often has '-M' or '-ms', Pan has '-P' or '-pan'
        lower_name = filename.lower()
        if "pan" in lower_name or "-p" in lower_name:
             out_name = os.path.splitext(filename)[0] + "_ortho_pan.tif"
             res = None # Keep native for Pan (approx 0.5m)
        elif "ms" in lower_name or "-m" in lower_name:
             out_name = os.path.splitext(filename)[0] + "_ortho_ms.tif"
             res = None # Keep native for MS (approx 2.0m)
        else:
             # Default fallback
             out_name = os.path.splitext(filename)[0] + "_ortho.tif"
             res = None

        out_path = os.path.join(args.output, out_name)

        # Skip if exists
        if os.path.exists(out_path):
            print(f"Skipping {out_name}, already exists.")
            continue

        # ORTHO
        success = run_ortho(img_path, out_path, args.dem, resolution=res)

        # COPY METADATA
        # This is vital for Step 220 (TOA) to work
        # We rename the metadata to match the output TIF so Step 220 can find it automatically
        if success:
            meta_src = find_metadata_file(img_path)
            if meta_src:
                meta_ext = os.path.splitext(meta_src)[1]
                # Naming convention: if output is image_ortho_ms.tif, meta is image_ortho_ms.xml
                meta_dst = os.path.splitext(out_path)[0] + meta_ext
                shutil.copy2(meta_src, meta_dst)
                print(f"Copied metadata to {meta_dst}")
            else:
                print(f"WARNING: No XML/IMD found for {filename}. TOA step will fail for this image.")

if __name__ == "__main__":
    main()