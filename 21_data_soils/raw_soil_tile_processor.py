# soil_processor.py
# Version: 1.1.2
import os
import re
import subprocess
import json
import datetime
from pathlib import Path
from collections import defaultdict

# --- CONFIGURATION ---
PROJECT_ID = "akveg-map" 
REGION = "us-central1"

# GCS paths for input tiles and output mosaics
GCS_INPUT_PATH = "gs://akveg-data/aksdb_products_v20260214/rf11_taxa/"
GCS_OUTPUT_PATH = "gs://akveg-data/aksdb_products_v20260214/rf11_taxa_cog_mosaics/"

# GDAL container image
GDAL_IMAGE = "ghcr.io/osgeo/gdal:ubuntu-small-3.9.0"

# Soil orders to exclude. 
# Histosols is excluded as it was already completed in the stress test.
EXCLUDE_SOILS = ["Histosols"]

def run_command(cmd):
    """Utility to run shell commands"""
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def create_batch_job_config(soil_order, input_uris):
    """
    Generates the JSON config for a Google Cloud Batch job.
    """
    gdal_inputs = " ".join([uri.replace("gs://", "/vsigs/") for uri in input_uris])
    
    # Output name pattern: {SoilOrder}_Probability_Alaska_rf11.tif
    filename = f"{soil_order}_Probability_Alaska_rf11.tif"
    output_gcs = f"{GCS_OUTPUT_PATH}{filename}".replace("gs://", "/vsigs/")
    
    # GDAL command: Build Virtual Raster -> Translate to u8 COG
    # -vrtnodata 255: Maps empty areas and 64-bit NoData to 255.
    # -ot Byte: Converts to 8-bit.
    # -a_nodata 255: Tags output so GIS software recognizes 255 as transparency.
    container_command = (
        f"gdalbuildvrt -vrtnodata 255 /tmp/mosaic.vrt {gdal_inputs} && "
        f"gdal_translate /tmp/mosaic.vrt {output_gcs} "
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
                    "provisioningModel": "STANDARD", # Standard VMs to avoid preemption resets
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

def submit_to_batch():
    """
    Main workflow:
    1. Scan GCS for all .tif files.
    2. Group by Soil Order.
    3. Filter out excluded soil orders.
    4. Submit jobs for the remaining taxa.
    """
    print(f"Scanning GCS for all tiles: {GCS_INPUT_PATH}*.tif")
    
    try:
        result = subprocess.check_output(f"gsutil ls {GCS_INPUT_PATH}*.tif", shell=True).decode()
        all_files = [f for f in result.strip().split('\n') if f]
    except Exception as e:
        print(f"No files found in input path: {e}")
        return

    pattern = re.compile(r"([^/]+)_([A-Za-z]+)\.tif$")
    soil_groups = defaultdict(list)

    # Normalize excluded list to lowercase for robust comparison
    excluded_lower = [s.lower() for s in EXCLUDE_SOILS]

    for file_uri in all_files:
        match = pattern.search(file_uri)
        if match:
            soil_order = match.group(2)
            # Check if this soil order is in our exclusion list
            if soil_order.lower() in excluded_lower:
                continue
            soil_groups[soil_order].append(file_uri)

    if not soil_groups:
        print("No remaining soil types found to process.")
        return

    print(f"Found {len(soil_groups)} soil types to process. Submitting jobs...")

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")

    for soil, uris in soil_groups.items():
        # Tag job ID with 'std' to signify Standard provisioning
        job_id = f"mosaic-std-{soil.lower()}-{timestamp}"
        print(f"-> Submitting STANDARD job for {soil} ({len(uris)} tiles)...")
        
        config = create_batch_job_config(soil, uris)
        config_filename = f"config_{soil}.json"
        
        with open(config_filename, "w") as f:
            json.dump(config, f)

        submit_cmd = (
            f"gcloud batch jobs submit {job_id} "
            f"--location {REGION} "
            f"--config {config_filename} "
            f"--project {PROJECT_ID}"
        )
        
        run_command(submit_cmd)
        os.remove(config_filename)

    print("\nStatewide STANDARD submission complete.")

if __name__ == "__main__":
    submit_to_batch()