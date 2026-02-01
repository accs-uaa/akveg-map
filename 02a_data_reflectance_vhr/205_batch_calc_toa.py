import os
import glob
import math
import argparse
import numpy as np
import rasterio
from rasterio.enums import Resampling
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess

"""
205_batch_calc_toa.py

Description:
    Step 2 of VHR Workflow.
    Converts Orthorectified DN imagery (Pan and MS) to TOA Reflectance.
    
    This runs BEFORE pansharpening to ensure spectral calibration is applied 
    to the raw data channels.
    
    Logic:
    - Detects if image is PAN (1 band), MS-4 (4 bands), or MS-8 (8 bands).
    - Parses Maxar XML for calibration factors (absCalFactor, effectiveBandwidth).
    - Applies Solar Irradiance and Sun Angle corrections.
    - Scales output to 0-10,000 (UInt16).

    Usage Example:
        python 205_batch_calc_toa.py \
            --input "/path/to/01_ortho" \
            --output "/path/to/01_ortho_toa" \
            --overwrite
"""

# Solar Irradiance (Thuillier 2003) - W/m^2/um
# Legacy from old docs
# ESUN_DICT = {
#     "WV02": {"PAN": 1580.8, "BLUE": 1924.6, "GREEN": 1843.1, "RED": 1574.4, "NIR": 1043.8, "NIR1": 1043.8, 
#              "COASTAL": 1758.2, "YELLOW": 1843.3, "REDEDGE": 1610.7, "NIR2": 869.7},
#     "WV03": {"PAN": 1583.5, "BLUE": 1974.2, "GREEN": 1856.4, "RED": 1559.5, "NIR": 1071.6, "NIR1": 1071.6,
#              "COASTAL": 1743.8, "YELLOW": 1842.3, "REDEDGE": 1611.5, "NIR2": 861.2},
#     "GE01": {"PAN": 1610.7, "BLUE": 1960.3, "GREEN": 1853.3, "RED": 1505.1, "NIR": 1039.4, "NIR1": 1039.4},
#     "QB02": {"PAN": 1381.7, "BLUE": 1924.5, "GREEN": 1843.0, "RED": 1574.4, "NIR": 1043.8}
# }

# Soliar Irradiance from PGC
# Source: Maxar Absolute Radiometric Calibration White Paper (and the 2016v0 release PDF)
# "Note that the calibration uses Thuillier 2003 solar curve."
ESUN_DICT = {
    "WV02": {
        "PAN": 1571.36,
        "BLUE": 2007.27,
        "GREEN": 1829.62,
        "RED": 1538.85,
        "NIR": 1053.21,
        "NIR1": 1053.21,
        "COASTAL": 1773.81,
        "YELLOW": 1701.85,
        "REDEDGE": 1346.09,
        "NIR2": 856.599
    },
    "WV03": {
        "PAN": 1574.41,
        "BLUE": 2004.61,
        "GREEN": 1830.18,
        "RED": 1535.33,
        "NIR": 1055.94,
        "NIR1": 1055.94,
        "COASTAL": 1757.89,
        "YELLOW": 1712.07,
        "REDEDGE": 1348.08,
        "NIR2": 858.77
    },
    "GE01": {
        "PAN": 1610.73,
        "BLUE": 1993.18,
        "GREEN": 1828.83,
        "RED": 1491.49,
        "NIR": 1022.58,
        "NIR1": 1022.58
    },
    "QB02": {
        "PAN": 1370.92,
        "BLUE": 1949.59,
        "GREEN": 1823.64,
        "RED": 1553.78,
        "NIR": 1102.85
    }
}

def get_band_map(band_count):
    """Returns the band name mapping based on band count."""
    if band_count == 1:
        return {0: "PAN"}
    elif band_count == 4:
        return {0: "BLUE", 1: "GREEN", 2: "RED", 3: "NIR"}
    elif band_count == 8:
        return {
            0: "COASTAL", 1: "BLUE", 2: "GREEN", 3: "YELLOW",
            4: "RED", 5: "REDEDGE", 6: "NIR", 7: "NIR2"
        }
    else:
        return {}

def parse_metadata(xml_path):
    """Parses Maxar XML/IMD to extract calibration coefficients."""
    meta = {}
    is_xml_format = True
    
    # Check header
    with open(xml_path, 'r', errors='ignore') as f:
        if not f.readline().strip().startswith("<"):
            is_xml_format = False

    if is_xml_format:
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            def find_val(tags):
                for t in tags:
                    res = root.find(f".//{t}")
                    if res is not None: return res.text
                return None
                
            meta['satId'] = find_val(["SATID", "satId"])
            
            sun_el = find_val(["MEANSUNEL", "meanSunEl"])
            if sun_el: meta['meanSunEl'] = float(sun_el)
            
            earth_sun = find_val(["EARTHSUNDIST", "earthSunDist"])
            if earth_sun: meta['earthSunDist'] = float(earth_sun)
            
            t_str = find_val(["FIRSTLINETIME", "firstLineTime"])
            if t_str:
                t_str = t_str.replace("T", " ").replace("Z", "")
                if "." in t_str and len(t_str.split(".")[1]) > 6:
                     t_str = t_str.split(".")[0] + "." + t_str.split(".")[1][:6]
                meta['acq_time'] = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S.%f")

            meta['bands'] = {}
            # Map XML codes to standard names
            # N is usually NIR1.
            band_codes = {'C': 'COASTAL', 'B': 'BLUE', 'G': 'GREEN', 'Y': 'YELLOW', 'R': 'RED', 
                          'RE': 'REDEDGE', 'N': 'NIR', 'N1': 'NIR', 'N2': 'NIR2', 'P': 'PAN'}
            
            for elem in root.iter():
                tag = elem.tag.upper()
                # Handle BAND_C, BAND_P, etc.
                if tag.startswith("BAND_") or tag.startswith("BANDID"):
                    code = tag.split("_")[-1] if "_" in tag else None
                    if not code and "BANDID" in tag: code = elem.text
                    
                    if code in band_codes:
                        bname = band_codes[code]
                        abs_cal = elem.find("ABSCALFACTOR")
                        eff_bw = elem.find("EFFECTIVEBANDWIDTH")
                        esun = elem.find("SOLARIRRADIANCE")
                        
                        # Sometimes values are siblings in flat XML
                        if abs_cal is None:
                             # Fallback for flat structure
                             pass 
                        
                        if abs_cal is not None and eff_bw is not None:
                             data = {
                                'absCalFactor': float(abs_cal.text),
                                'effectiveBandwidth': float(eff_bw.text)
                             }
                             if esun is not None:
                                 data['solarIrradiance'] = float(esun.text)
                             meta['bands'][bname] = data
        except Exception as e:
            print(f"XML Parsing Error: {e}")
            raise e
    else:
        # IMD Parser
        params = {}
        with open(xml_path, 'r') as f:
            for line in f:
                if "=" in line:
                    k, v = line.split("=", 1)
                    params[k.strip().upper()] = v.strip().replace('"', '').replace(';', '')
        
        meta['satId'] = params.get('SATID')
        meta['meanSunEl'] = float(params.get('MEANSUNEL', 45.0))
        if 'EARTHSUNDISTANCE' in params:
            meta['earthSunDist'] = float(params.get('EARTHSUNDISTANCE'))
        t_str = params.get('FIRSTLINETIME')
        if t_str:
             t_str = t_str.replace("T", " ").replace("Z", "")
             meta['acq_time'] = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S.%f")
             
        meta['bands'] = {}
        band_codes = {'C': 'COASTAL', 'B': 'BLUE', 'G': 'GREEN', 'Y': 'YELLOW', 'R': 'RED', 
                      'RE': 'REDEDGE', 'N': 'NIR', 'N1': 'NIR', 'N2': 'NIR2', 'P': 'PAN'}
        
        for key, val in params.items():
            parts = key.split('.')
            if len(parts) > 1 and parts[0].startswith("BAND_"):
                code = parts[0].split("_")[1]
                if code in band_codes:
                    bname = band_codes[code]
                    if bname not in meta['bands']: meta['bands'][bname] = {}
                    if parts[1] == 'ABSCALFACTOR': meta['bands'][bname]['absCalFactor'] = float(val)
                    elif parts[1] == 'EFFECTIVEBANDWIDTH': meta['bands'][bname]['effectiveBandwidth'] = float(val)
                    elif parts[1] == 'SOLARIRRADIANCE': meta['bands'][bname]['solarIrradiance'] = float(val)
                        
    return meta

def calc_earth_sun_dist(dt):
    doy = dt.timetuple().tm_yday
    return 1 - 0.01672 * math.cos(0.9856 * (doy - 4) * (math.pi / 180))

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

def calculate_toa(dn_path, xml_path, out_path, res_pan=None, res_ms=None, resampling=Resampling.bilinear):
    print(f"Calibrating: {os.path.basename(dn_path)}")
    
    try:
        meta = parse_metadata(xml_path)
    except Exception as e:
        print(f"  Failed to parse Metadata {xml_path}: {e}")
        return False
    
    if not meta.get('satId'):
        print("  Missing SatID.")
        return False

    sat_id = meta['satId']
    # Handle aliases
    if sat_id == "WorldView-3": sat_id = "WV03"
    if sat_id == "WorldView-2": sat_id = "WV02"
    if sat_id == "GeoEye-1": sat_id = "GE01"

    sun_el = meta['meanSunEl']
    sun_zenith = 90.0 - sun_el
    if 'earthSunDist' in meta:
        d_au = meta['earthSunDist']
    else:
        d_au = calc_earth_sun_dist(meta['acq_time'])
    
    if sat_id not in ESUN_DICT:
        print(f"  WARNING: Satellite {sat_id} not in ESUN lookup. Defaulting to WV03.")
        esun_table = ESUN_DICT["WV03"]
    else:
        esun_table = ESUN_DICT[sat_id]

    with rasterio.open(dn_path) as src:
        profile = src.profile.copy()
        profile.update(dtype='uint16', nodata=0, compress='deflate', predict=2, bigtiff='IF_NEEDED')
        
        # Sanitize profile to avoid inheriting bad metadata from previous steps
        for key in ['photometric', 'interleave', 'alpha', 'extra_samples']:
            profile.pop(key, None)
        
        # Determine target resolution and update profile if needed
        target_res = None
        if src.count == 1 and res_pan:
            target_res = res_pan
        elif src.count >= 4 and res_ms:
            target_res = res_ms
            
        if target_res:
            scale = src.res[0] / target_res
            new_width = int(src.width * scale)
            new_height = int(src.height * scale)
            new_transform = src.transform * src.transform.scale(
                (src.width / new_width), (src.height / new_height))
            profile.update(width=new_width, height=new_height, transform=new_transform)

        # Determine mapping based on file band count
        band_map = get_band_map(src.count)
        
        with rasterio.open(out_path, 'w', **profile) as dst:
            for i in range(1, src.count + 1):
                band_idx = i - 1
                band_name = band_map.get(band_idx, "UNKNOWN")
                
                # Special handling for Maxar XML naming vs our dict
                # If we have NIR1 in XML but NIR in map, etc.
                cal_data = meta['bands'].get(band_name)
                # Fallback: if map says NIR but XML says N, try to align
                if not cal_data and band_name == "NIR": cal_data = meta['bands'].get("NIR1")
                
                if not cal_data:
                    print(f"  Warning: Band {i} ({band_name}) calibration not found in XML. Writing 0s.")
                    dst.write(np.zeros((profile['height'], profile['width']), dtype='uint16'), i)
                    continue
                
                abs_cal = cal_data['absCalFactor']
                eff_bw = cal_data['effectiveBandwidth']
                
                # Use metadata ESUN if available, else fallback to dict
                if 'solarIrradiance' in cal_data:
                    esun = cal_data['solarIrradiance']
                else:
                    esun = esun_table.get(band_name, 1500.0)
                    if band_name == "NIR": esun = esun_table.get("NIR1", 1000.0)

                # Read DN
                if target_res:
                    dn = src.read(i, out_shape=(profile['height'], profile['width']), resampling=resampling).astype('float32')
                else:
                    dn = src.read(i).astype('float32')
                
                valid_mask = dn > 0
                
                # Radiance
                # Maxar absCalFactor is band-integrated radiance per count.
                # Must divide by effective bandwidth to get spectral radiance.
                L = dn * (abs_cal / eff_bw)
                
                # Reflectance
                theta_rad = math.radians(sun_zenith)
                denom = esun * math.cos(theta_rad)
                rho = (L * (d_au**2) * math.pi) / denom
                
                # Scale 0-10000
                rho_scaled = np.clip(rho * 10000, 0, 65535).astype('uint16')
                rho_scaled[~valid_mask] = 0
                
                dst.write(rho_scaled, i)
                
    print(f"  Saved TOA: {os.path.basename(out_path)}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Step 2: Batch Calculate TOA Reflectance (0-10000)")
    parser.add_argument("--input", required=True, help="Folder containing Ortho DN files (MS and Pan)")
    parser.add_argument("--output", required=True, help="Output folder")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--res-pan", type=float, help="Override output resolution for PAN (meters)")
    parser.add_argument("--res-ms", type=float, help="Override output resolution for MS (meters)")
    parser.add_argument("--resampling", default="bilinear", help="Resampling method (nearest, bilinear, cubic, cubic_spline, lanczos, average). Default: bilinear")
    parser.add_argument("--threads", type=int, default=1, help="Number of threads for overviews (default: 1)")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    # Process both Pan and MS
    search_patterns = ["*_ortho_ms.tif", "*_ortho_pan.tif", "*_ortho.tif"]
    images = []
    for p in search_patterns:
        images.extend(glob.glob(os.path.join(args.input, p)))
    
    # Deduplicate
    images = list(set(images))

    # Resolve resampling enum
    try:
        res_enum = getattr(Resampling, args.resampling)
    except AttributeError:
        print(f"Warning: Invalid resampling '{args.resampling}'. Defaulting to bilinear.")
        res_enum = Resampling.bilinear
    
    if not images:
        print("No ortho files found to calibrate.")
        return

    for img_path in images:
        # Skip intermediate overviews
        if ".ovr" in img_path: continue

        # Naming: _ortho_ms.tif -> _ortho_ms_toa.tif
        base_name = os.path.basename(img_path)
        if "_ortho_" in base_name:
            out_name = base_name.replace(".tif", "_toa.tif")
        else:
            out_name = os.path.splitext(base_name)[0] + "_toa.tif"
            
        out_path = os.path.join(args.output, out_name)
        
        if os.path.exists(out_path) and not args.overwrite:
            print(f"Skipping {out_name}, exists.")
            continue
            
        # Find Metadata (should be named like input due to step 200)
        xml_path = None
        base = os.path.splitext(img_path)[0]
        for ext in ['.xml', '.XML', '.imd', '.IMD']:
            if os.path.exists(base + ext):
                xml_path = base + ext
                break
        
        if not xml_path:
            print(f"Skipping {base_name}: Metadata not found.")
            continue
            
        success = calculate_toa(img_path, xml_path, out_path, args.res_pan, args.res_ms, resampling=res_enum)
        
        # Copy metadata forward (optional, but good practice)
        if success:
            dst_meta = os.path.splitext(out_path)[0] + os.path.splitext(xml_path)[1]
            try:
                import shutil
                shutil.copy2(xml_path, dst_meta)
            except: pass
            
            # ADD OVERVIEWS AND STATS
            add_overviews_and_stats(out_path, threads=args.threads)

if __name__ == "__main__":
    main()