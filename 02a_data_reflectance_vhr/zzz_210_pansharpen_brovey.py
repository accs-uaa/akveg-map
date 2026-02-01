import os
import glob
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window, bounds as window_bounds
import argparse
import shutil

"""
210_pansharpen_brovey.py

Description:
    Performs a Weighted Brovey Pansharpening on Orthorectified DN images.
    
    We use this custom Python implementation instead of OTB/GDAL scripts because:
    1. It avoids external binary dependencies.
    2. It processes in 'windows' (blocks), preventing memory crashes on large Maxar files.
    3. It handles the 16-bit DN data type correctly without accidental rescaling.
    
    Algorithm:
    1. Resample MS to Pan resolution (Bilinear).
    2. Calculate Intensity (Mean of MS bands).
    3. Calculate Ratio = Pan / Intensity.
    4. New_Band = Old_Band * Ratio.
"""

def find_pair(ms_file, pan_folder):
    """
    Tries to find the matching Pan file for a given MS file.
    Robustly handles Maxar naming conventions (M1BS -> P1BS) and suffix swaps.
    """
    base_name = os.path.basename(ms_file)
    dir_name = os.path.dirname(ms_file)
    
    # Step 1: Always swap the suffix first (this is the part we controlled in script 200)
    # e.g., "Image_ortho_ms.tif" -> "Image_ortho_pan.tif"
    base_candidate = base_name.replace("_ortho_ms.tif", "_ortho_pan.tif")
    
    # Step 2: Define strategies to transform the rest of the filename
    # Maxar files typically differ by product code (M1BS vs P1BS) 
    # and sometimes by band identifiers (-M vs -P).
    strategies = [
        lambda x: x,                                      # Strategy A: Exact match (only suffix changed)
        lambda x: x.replace("M1BS", "P1BS"),              # Strategy B: Maxar Standard (M1BS -> P1BS)
        lambda x: x.replace("-M", "-P"),                  # Strategy C: Hyphenated Short Code
        lambda x: x.replace("_M", "_P"),                  # Strategy D: Underscore Short Code
        lambda x: x.replace("M1BS", "P1BS").replace("-M", "-P") # Strategy E: Combo
    ]
    
    for strategy in strategies:
        candidate = strategy(base_candidate)
        
        # Check in the target Pan folder
        full_path = os.path.join(pan_folder, candidate)
        if os.path.exists(full_path):
            return full_path
            
        # Check in the Input folder (case where input and output are mixed or relative paths used)
        full_path_input = os.path.join(dir_name, candidate)
        if os.path.exists(full_path_input):
            return full_path_input
                
    return None

def pansharpen_image(ms_path, pan_path, out_path):
    
    print(f"Pansharpening:\n MS: {os.path.basename(ms_path)}\n Pan: {os.path.basename(pan_path)}")
    
    with rasterio.open(pan_path) as pan_src:
        pan_profile = pan_src.profile.copy()
        pan_height = pan_src.height
        pan_width = pan_src.width
        pan_crs = pan_src.crs
        pan_transform = pan_src.transform
        
    with rasterio.open(ms_path) as ms_src:
        ms_count = ms_src.count
        
        # Update profile for output (Match MS band count dynamically)
        out_profile = pan_profile.copy()
        out_profile.update(count=ms_count, dtype='uint16', compress='lzw', bigtiff='IF_NEEDED', nodata=0)

        with rasterio.open(out_path, 'w', **out_profile) as dst:
            
            # Process in blocks to save memory (e.g., 2048x2048 pixels)
            # This is critical for large Maxar strips
            block_size = 2048
            
            for i in range(0, pan_height, block_size):
                for j in range(0, pan_width, block_size):
                    # Define the window (in Pan pixel coordinates)
                    window = Window(j, i, min(block_size, pan_width - j), min(block_size, pan_height - i))
                    
                    # Read Pan (High Res)
                    with rasterio.open(pan_path) as pan_s:
                        pan_data = pan_s.read(1, window=window).astype('float32')
                    
                    # Calculate the spatial bounds of the Pan window
                    # transform maps pixels to spatial coordinates
                    win_bounds = window_bounds(window, pan_transform)
                    
                    # Map those spatial bounds to a window in the MS image (Low Res)
                    ms_window = ms_src.window(*win_bounds)
                    
                    # Read MS (Low Res) and UP-SAMPLE to Pan window on the fly
                    # We request the window calculated above (ms_window)
                    # But we force the output shape to match the Pan window dimensions (window.height, window.width)
                    # boundless=True prevents errors if the calculated window is slightly off-edge
                    ms_data = ms_src.read(
                        window=ms_window,
                        out_shape=(ms_src.count, window.height, window.width),
                        resampling=Resampling.bilinear,
                        boundless=True
                    ).astype('float32')
                    
                    # Handle Nodata / Zero Division
                    # Create a mask where valid data exists in both
                    # (Avoids artifacts at edges)
                    ms_mean = np.mean(ms_data, axis=0)
                    valid_mask = (pan_data > 0) & (ms_mean > 0)
                    
                    # Brovey Transform
                    # 1. Calculate Intensity (Simple Average of bands)
                    # Note: You can use specific weights [0.1, 0.4, 0.4, 0.1] if desired, 
                    # but simple mean is standard for basic Brovey.
                    intensity = ms_mean
                    
                    # 2. Calculate Ratio
                    ratio = np.zeros_like(intensity)
                    np.divide(pan_data, intensity, out=ratio, where=(intensity > 0))
                    
                    # 3. Multiply Bands by Ratio
                    out_data = np.zeros_like(ms_data)
                    for b in range(ms_count):
                        out_data[b] = ms_data[b] * ratio
                        
                    # 4. Clip and Cast
                    out_data = np.clip(out_data, 0, 65535).astype('uint16')
                    
                    # Apply Mask (clean edges)
                    for b in range(ms_count):
                        out_data[b][~valid_mask] = 0
                        
                    # Write block
                    dst.write(out_data, window=window)

    print(f"Saved: {out_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Pansharpen Maxar Imagery (Brovey)")
    parser.add_argument("--input", required=True, help="Folder containing Ortho MS and Pan files")
    parser.add_argument("--output", required=True, help="Output folder")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    # Find MS files
    ms_files = glob.glob(os.path.join(args.input, "*_ortho_ms.tif"))
    
    if not ms_files:
        print("No *_ortho_ms.tif files found.")
        return

    for ms_file in ms_files:
        pan_file = find_pair(ms_file, args.input)
        
        if not pan_file:
            print(f"Warning: No matching Pan file found for {os.path.basename(ms_file)}")
            continue
            
        # Define output name
        base_name = os.path.basename(ms_file).replace("_ortho_ms.tif", "_ortho_ps_dn.tif")
        out_path = os.path.join(args.output, base_name)
        
        if os.path.exists(out_path):
            print(f"Skipping {base_name}, exists.")
            continue
            
        success = pansharpen_image(ms_file, pan_file, out_path)
        
        # COPY METADATA
        # Critical for Step 220. We copy the MS metadata to the PS file.
        # This allows 220 to find the calibration coefficients.
        if success:
            base_ms = os.path.splitext(ms_file)[0]
            # Try to find the metadata file we copied in step 200
            meta_src = None
            for ext in ['.xml', '.XML', '.imd', '.IMD']:
                if os.path.exists(base_ms + ext):
                    meta_src = base_ms + ext
                    break
            
            if meta_src:
                meta_ext = os.path.splitext(meta_src)[1]
                meta_dst = os.path.splitext(out_path)[0] + meta_ext
                shutil.copy2(meta_src, meta_dst)
                print(f"Copied metadata to {meta_dst}")
            else:
                 print("Warning: Could not carry forward metadata.")

if __name__ == "__main__":
    main()