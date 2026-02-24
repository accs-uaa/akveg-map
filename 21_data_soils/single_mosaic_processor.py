# single_mosaic_processor.py
# Refactored from raw_soil_tile_processor.py
# Version: 1.0.0

"""
Usage Examples:

```bash
# 1. Test Run (Explicit arguments for V14 test case)
python3 single_mosaic_processor.py \
  --input-path "gs://akveg-data/aksdb_products_v20260214/rf11_histic-histel-histosol-combined/" \
  --pattern "*V14*.tif" \
  --output-path "gs://akveg-data/aksdb_products_v20260214/rf11_taxa_cog_mosaics/" \
  --output-filename "histic-histel-histosol_V14_Probability_Combined_rf11_db1.tif"

# 2. Statewide Run (Explicit arguments for full run)
python3 single_mosaic_processor.py \
  --input-path "gs://akveg-data/aksdb_products_v20260214/rf11_histic-histel-histosol-combined/" \
  --pattern "*.tif" \
  --output-path "gs://akveg-data/aksdb_products_v20260214/rf11_taxa_cog_mosaics/" \
  --output-filename "histic-histel-histosol_Probability_Combined_rf11_db1.tif"

# 3. Custom Run (different input/output)
python3 single_mosaic_processor.py \
  --input-path "gs://my-bucket/input/" \
  --pattern "*.tif" \
  --output-path "gs://my-bucket/output/" \
  --output-filename "my_mosaic.tif"
```
"""

import os
import subprocess
import json
import datetime
import argparse
import sys

# --- CONFIGURATION ---
PROJECT_ID = "akveg-map" 
REGION = "us-central1"

# GDAL container image
GDAL_IMAGE = "ghcr.io/osgeo/gdal:ubuntu-small-3.9.0"

def run_command(cmd):
    """Utility to run shell commands"""
    try:
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def create_batch_job_config(input_uris, output_uri):
    """
    Generates the JSON config for a Google Cloud Batch job.
    """
    # Convert gs:// paths to /vsigs/ for GDAL
    gdal_inputs = " ".join([uri.replace("gs://", "/vsigs/") for uri in input_uris])
    gdal_output = output_uri.replace("gs://", "/vsigs/")
    
    # GDAL command: Build Virtual Raster -> Translate to u8 COG
    # -vrtnodata 255: Maps empty areas and 64-bit NoData to 255.
    # -ot Byte: Converts to 8-bit.
    # -a_nodata 255: Tags output so GIS software recognizes 255 as transparency.
    # Using /tmp/mosaic.vrt as intermediate
    container_command = (
        f"gdalbuildvrt -vrtnodata 255 /tmp/mosaic.vrt {gdal_inputs} && "
        f"gdal_translate /tmp/mosaic.vrt {gdal_output} "
        f"-ot Byte -of COG -co COMPRESS=DEFLATE -co PREDICTOR=2 -co BIGTIFF=YES "
        f"-a_nodata 255 "
        f"--config CPL_VSIL_USE_TEMP_FILE_FOR_RANDOM_WRITE YES"
    )

    job_config = {
        "taskGroups": [{
            "taskSpec": {
                "runnables": [{
                    "container": {
                        "imageUri": GDAL_IMAGE,
                        "commands": ["/bin/sh", "-c", container_command],
                        "options": "--privileged"
                    }
                }],
                "computeResource": {
                    "cpuMilli": "4000",
                    "memoryMib": "16384"
                },
                "maxRunDuration": "86400s" # 24 hours
            }
        }],
        "allocationPolicy": {
            "instances": [{
                "policy": {
                    "machineType": "e2-standard-4",
                    "provisioningModel": "STANDARD", 
                    "bootDisk": {
                        "sizeGb": "100"
                    }
                }
            }]
        },
        "logsPolicy": {
            "destination": "CLOUD_LOGGING"
        }
    }
    return job_config

def main():
    parser = argparse.ArgumentParser(description="Submit a single mosaic job to Google Cloud Batch.")
    
    # Default settings based on user request
    parser.add_argument("--input-path", 
                        default="gs://akveg-data/aksdb_products_v20260214/rf11_histic-histel-histosol-combined/",
                        help="GCS path to input tiles (include trailing slash).")
    
    parser.add_argument("--pattern", 
                        default="*V14*.tif", 
                        help="Wildcard pattern for input files (e.g., *.tif or *V14*.tif).")
    
    parser.add_argument("--output-path", 
                        default="gs://akveg-data/aksdb_products_v20260214/rf11_taxa_cog_mosaics/",
                        help="GCS path for output mosaic (include trailing slash).")
    
    parser.add_argument("--output-filename", 
                        default="histic-histel-histosol_Probability_Combined_rf11_db1.tif",
                        help="Filename for the output mosaic.")

    args = parser.parse_args()

    # Ensure output filename has extension
    if not args.output_filename.lower().endswith('.tif'):
        args.output_filename += ".tif"

    # Construct full search path and output URI
    search_path = os.path.join(args.input_path, args.pattern)
    output_uri = os.path.join(args.output_path, args.output_filename)

    print(f"Scanning GCS for tiles matching: {search_path}")
    try:
        # Use gsutil to list files
        result = subprocess.check_output(f"gsutil ls {search_path}", shell=True).decode()
        input_files = [f for f in result.strip().split('\n') if f]
    except subprocess.CalledProcessError:
        print(f"No files found matching {search_path}")
        return

    print(f"Found {len(input_files)} tiles to process.")
    
    # Generate Job ID
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    # Sanitize filename for job ID (lowercase, replace underscores/dots with hyphens)
    safe_name = args.output_filename.lower().replace('_', '-').replace('.', '-').replace(' ', '-')[:40]
    job_id = f"mosaic-{safe_name}-{timestamp}"

    print(f"-> Submitting Batch Job: {job_id}")
    print(f"   Output: {output_uri}")

    config = create_batch_job_config(input_files, output_uri)
    config_filename = f"config_{job_id}.json"

    with open(config_filename, "w") as f:
        json.dump(config, f, indent=2)

    submit_cmd = (
        f"gcloud batch jobs submit {job_id} "
        f"--location {REGION} "
        f"--config {config_filename} "
        f"--project {PROJECT_ID}"
    )
    
    run_command(submit_cmd)
    
    # Cleanup config file
    if os.path.exists(config_filename):
        os.remove(config_filename)

    print("\nJob submitted successfully.")
    print(f"Check status with:\n  gcloud batch jobs list --filter=\"name:{job_id}\" --location {REGION} --project {PROJECT_ID}")
    print(f"Input file count: {len(input_files)}")

if __name__ == "__main__":
    main()