import os
# Set defaults to prevent CPU hogging before libraries load.
# This ensures that even if threadpoolctl is missing, we don't use all cores.
os.environ.setdefault("OMP_NUM_THREADS", "8")
os.environ.setdefault("MKL_NUM_THREADS", "8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "8")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "8")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "8")

import glob
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window, bounds as window_bounds
from sklearn.linear_model import LinearRegression
import argparse
import shutil
import subprocess

try:
    from threadpoolctl import threadpool_limits
except ImportError:
    threadpool_limits = None

"""
210_pansharpen_gram_schmidt.py

Description:
    Step 3 of VHR Workflow.
    Performs Gram-Schmidt Pansharpening on TOA Reflectance images.
    
    Inputs:
        - Multispectral TOA (*_ortho_ms_toa.tif)
        - Panchromatic TOA (*_ortho_pan_toa.tif)
    Output:
        - Pansharpened TOA (*_ortho_ps_toa.tif)
    
    Features:
    - Fuses reflectance data (0-10,000) directly.
    - Memory Safe (chunked processing).
    - Sensor Agnostic.
    
    Usage Example:
        python 210_pansharpen_gram_schmidt.py \
            --input "/path/to/01_ortho_toa" \
            --output "/path/to/02_pansharpen" \
            --overwrite
"""

def get_band_indices(band_count, force_standard_bands):
    """
    Determines which bands to process based on input count and user preference.
    """
    # Case A: 8-Band WorldView-2/3
    # Indices: Blue=2, Green=3, Red=5, NIR1=7
    if band_count == 8 and force_standard_bands:
        print("  > Mode: Reducing 8-band WorldView to Standard 4-Band (B, G, R, NIR1)")
        return [2, 3, 5, 7]
    return list(range(1, band_count + 1))

def find_pair(ms_file, pan_folder):
    """
    Finds matching Pan TOA file for MS TOA file.
    Expects pattern: *_ortho_ms_toa.tif -> *_ortho_pan_toa.tif
    """
    base_name = os.path.basename(ms_file)
    dir_name = os.path.dirname(ms_file)
    
    # 1. Swap suffix
    base_candidate = base_name.replace("_ortho_ms_toa.tif", "_ortho_pan_toa.tif")
    
    # 2. Swap Sensor Codes (M1BS -> P1BS)
    strategies = [
        lambda x: x,
        lambda x: x.replace("M1BS", "P1BS"),
        lambda x: x.replace("-M", "-P"),
        lambda x: x.replace("_M", "_P"),
        lambda x: x.replace("M1BS", "P1BS").replace("-M", "-P")
    ]
    
    for strategy in strategies:
        candidate = strategy(base_candidate)
        
        # Check target folder first
        full_path = os.path.join(pan_folder, candidate)
        if os.path.exists(full_path):
            return full_path
        # Check source folder
        full_path_input = os.path.join(dir_name, candidate)
        if os.path.exists(full_path_input):
            return full_path_input
                
    return None

def find_metadata_file(image_path):
    """Finds associated metadata XML/IMD"""
    base = os.path.splitext(image_path)[0]
    # Handle _toa suffix removal if needed to find original xml
    # But 205 copied xml to match _toa name, so check exact match first
    for ext in ['.xml', '.XML', '.imd', '.IMD']:
        if os.path.exists(base + ext):
            return base + ext
    return None

def add_overviews_and_stats(filepath, threads=1):
    """
    Adds internal overviews and calculates approximate stats for quick visualization.
    """
    print(f"  Adding overviews and stats for {os.path.basename(filepath)}...")
    
    try:
        # Internal Overviews
        subprocess.check_call([
            "gdaladdo", 
            "-r", "average", 
            "--config", "COMPRESS_OVERVIEW", "DEFLATE",
            "--config", "PREDICTOR_OVERVIEW", "2",
            "--config", "GDAL_NUM_THREADS", str(threads),
            filepath, 
            "2", "4", "8", "16"
        ])
        
        # Stats
        subprocess.check_call(
            ["gdalinfo", "-stats", filepath], 
            stdout=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"    Warning: Could not add overviews/stats: {e}")

def resample_output(filepath, resolution, resampling="cubic", threads=1):
    """Resamples the output file to a specific resolution using gdalwarp."""
    print(f"  Resampling output to {resolution}m...")
    temp_file = filepath.replace(".tif", "_temp_res.tif")
    try:
        subprocess.check_call([
            "gdalwarp", filepath, temp_file,
            "-tr", str(resolution), str(resolution),
            "-wo", f"NUM_THREADS={threads}",
            "-co", f"NUM_THREADS={threads}",
            "-r", resampling,
            "-co", "COMPRESS=DEFLATE", "-co", "PREDICTOR=2", "-co", "BIGTIFF=YES"
        ])
        shutil.move(temp_file, filepath)
    except Exception as e:
        print(f"    Error resampling: {e}")
        if os.path.exists(temp_file): os.remove(temp_file)

def pansharpen_gram_schmidt(pan_path, ms_path, out_path, force_standard_bands=False, resampling=Resampling.bilinear, threads=8):
    """
    Robust Gram-Schmidt Pansharpening.
    """
    print(f"Processing Pair:\n MS: {os.path.basename(ms_path)}\n Pan: {os.path.basename(pan_path)}")
    
    # --- PASS 1: Global Statistics (Weight Calculation) ---
    print(f"  Pass 1: Calculating spectral weights...")

    # Use threadpoolctl to limit BLAS/OpenMP threads during regression and numpy ops
    if threadpool_limits:
        context = threadpool_limits(limits=threads, user_api='blas')
    else:
        from contextlib import nullcontext
        context = nullcontext()

    with context, rasterio.open(pan_path) as pan_src, rasterio.open(ms_path) as ms_src:
        
        band_indices = get_band_indices(ms_src.count, force_standard_bands)
        n_bands = len(band_indices)
        
        # Subsample for stats
        dfactor = max(1, int(pan_src.width / 2000))
        
        pan_sub = pan_src.read(
            1, 
            out_shape=(pan_src.height // dfactor, pan_src.width // dfactor),
            resampling=Resampling.bilinear
        ).flatten()
        
        ms_sub = ms_src.read(
            band_indices,
            out_shape=(n_bands, pan_src.height // dfactor, pan_src.width // dfactor),
            resampling=resampling
        )
        ms_sub_flat = ms_sub.reshape(n_bands, -1).T
        
        # Filter NoData (using 0 as nodata)
        # Must ensure both Pan and ALL MS bands are valid to avoid skewing regression
        valid_mask = (pan_sub > 0) & np.all(ms_sub_flat > 0, axis=1)
        if valid_mask.sum() == 0:
            print(f"Skipping {pan_path}: Image appears to be empty.")
            return False

        pan_sub_clean = pan_sub[valid_mask]
        ms_sub_clean = ms_sub_flat[valid_mask]
        
        # Regression
        reg = LinearRegression().fit(ms_sub_clean, pan_sub_clean)
        weights = reg.coef_
        intercept = reg.intercept_
        
        # Calculate Injection Gains (Gram-Schmidt Mode)
        # Instead of using weights directly (which penalizes bands with low Pan correlation),
        # we use the covariance between each band and the synthetic intensity.
        # Gain_i = cov(MS_i, I) / var(I)
        I_clean = reg.predict(ms_sub_clean)
        var_I = np.var(I_clean)
        
        gains = []
        if var_I < 1e-6:
            gains = [1.0] * n_bands
        else:
            for b in range(n_bands):
                cov = np.cov(ms_sub_clean[:, b], I_clean)[0, 1]
                gains.append(cov / var_I)
        
        print(f"  > Weights: {np.round(weights, 3)}")
        print(f"  > Gains:   {np.round(gains, 3)}")

        # --- PASS 2: Processing ---
        print(f"  Pass 2: Fusing...")
        
        profile = pan_src.profile.copy()
        
        # Sanitize profile to avoid inheriting single-band metadata for multi-band output
        # This prevents issues like "Bad value for ExtraSamples" in GDAL
        for key in ['photometric', 'interleave', 'alpha', 'extra_samples']:
            profile.pop(key, None)
            
        profile.update({
            'count': n_bands,
            'dtype': 'uint16',
            'compress': 'deflate',    # Updated to Deflate
            'predict': 2,             # Added Predictor
            'bigtiff': 'YES',
            'tiled': True,
            'interleave': 'pixel',
            'nodata': 0,
            'blockxsize': 512,
            'blockysize': 512
        })
        
        with rasterio.open(out_path, 'w', **profile) as dst:
            
            for _, window in pan_src.block_windows(1):
                
                # A. Read High-Res Pan
                pan_chunk = pan_src.read(1, window=window).astype(np.float32)
                pan_mask = (pan_chunk > 0)
                if not np.any(pan_mask): continue
                
                # B. Read MS (Upsample)
                # Handle spatial alignment
                win_bounds = rasterio.windows.bounds(window, pan_src.transform)
                ms_window = ms_src.window(*win_bounds)
                
                ms_chunk = ms_src.read(
                    band_indices,
                    window=ms_window,
                    out_shape=(n_bands, window.height, window.width),
                    resampling=resampling,
                    boundless=True
                ).astype(np.float32)
                
                # Create combined mask (Pan valid AND MS valid)
                # MS might be 0 due to boundless padding or nodata
                ms_mask = np.all(ms_chunk > 0, axis=0)
                valid_chunk_mask = pan_mask & ms_mask
                
                # C. Synthetic Pan
                ms_reshaped = ms_chunk.reshape(n_bands, -1)
                synth_pan_flat = np.dot(weights, ms_reshaped) + intercept
                synth_pan = synth_pan_flat.reshape(window.height, window.width)
                
                # D. Detail Injection
                detail = pan_chunk - synth_pan
                sharpened_chunk = np.zeros_like(ms_chunk)
                
                for b in range(n_bands):
                    sharpened_chunk[b] = ms_chunk[b] + (detail * gains[b])
                
                # E. Write
                # Clip to 1-65535 to ensure valid dark pixels don't become NoData (0)
                sharpened_chunk = np.clip(sharpened_chunk, 1, 65535)
                sharpened_chunk[:, ~valid_chunk_mask] = 0 # Clean edges
                
                dst.write(sharpened_chunk.astype(np.uint16), window=window)

    print(f"  Saved: {os.path.basename(out_path)}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Step 3: Pansharpen TOA Imagery")
    parser.add_argument("--input", required=True, help="Folder containing Ortho TOA files")
    parser.add_argument("--output", required=True, help="Output folder")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output")
    parser.add_argument("--force-standard", action="store_true", help="Force 4-band output")
    parser.add_argument("--output-resolution", type=float, help="Override output resolution (meters)")
    parser.add_argument("--resampling", default="bilinear", help="Resampling method (nearest, bilinear, cubic, cubic_spline, etc). Default: bilinear")
    parser.add_argument("--threads", type=int, default=8, help="Number of threads for processing (default: 8)")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    # Search for TOA MS files
    ms_files = glob.glob(os.path.join(args.input, "*_ortho_ms_toa.tif"))
    
    # Resolve resampling enum for Rasterio
    try:
        res_enum = getattr(Resampling, args.resampling)
    except AttributeError:
        # Handle GDAL vs Rasterio naming (e.g. cubicspline vs cubic_spline)
        if args.resampling == "cubicspline":
            res_enum = Resampling.cubic_spline
        else:
            print(f"Warning: Invalid resampling '{args.resampling}' for internal processing. Defaulting to bilinear.")
            res_enum = Resampling.bilinear

    if not ms_files:
        print("No *_ortho_ms_toa.tif files found.")
        return

    for ms_file in ms_files:
        pan_file = find_pair(ms_file, args.input)
        
        if not pan_file:
            print(f"Warning: No Pan pair found for {os.path.basename(ms_file)}")
            continue
            
        base_name = os.path.basename(ms_file).replace("_ortho_ms_toa.tif", "_ortho_ps_toa.tif")
        out_path = os.path.join(args.output, base_name)
        
        if os.path.exists(out_path) and not args.overwrite:
            print(f"Skipping {base_name}, exists.")
            continue

        try:
            success = pansharpen_gram_schmidt(pan_file, ms_file, out_path, args.force_standard, resampling=res_enum, threads=args.threads)
            
            # Resample if requested
            if success and args.output_resolution:
                resample_output(out_path, args.output_resolution, resampling=args.resampling, threads=args.threads)

            # Copy metadata (optional but helpful)
            if success:
                meta_src = find_metadata_file(ms_file)
                if meta_src:
                    meta_dst = os.path.splitext(out_path)[0] + os.path.splitext(meta_src)[1]
                    shutil.copy2(meta_src, meta_dst)
            
            # ADD OVERVIEWS AND STATS
            if success:
                add_overviews_and_stats(out_path, threads=args.threads)
                    
        except Exception as e:
            print(f"ERROR processing {base_name}: {e}")

if __name__ == "__main__":
    main()