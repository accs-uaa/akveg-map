# test_soil_tile_processor.py
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

GCS_INPUT_PATH = "gs://akveg-data/aksdb_products_v20260214/rf11_taxa/"
GCS_OUTPUT_PATH = "gs://akveg-data/aksdb_products_v20260214/rf11_taxa_cog_mosaics/"
GDAL_IMAGE = "ghcr.io/osgeo/gdal:ubuntu-small-3.9.0"

def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def create_batch_job_config(soil_order, input_uris):
    gdal_inputs = " ".join([uri.replace("gs://", "/vsigs/") for uri in input_uris])
    # Labeling this as STRESS_TEST to differentiate from the small V14 test
    output_gcs = f"{GCS_OUTPUT_PATH}STRESS_TEST_{soil_order}_statewide_u8_cog.tif".replace("gs://", "/vsigs/")
    
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
                    "cpuMilli": "4000",   # Upgraded to 4 vCPUs for faster compression
                    "memoryMib": "16384"  # Upgraded to 16GB RAM for 1,110 tile management
                },
                "maxRunDuration": "28800s" # 8 hours
            }
        }],
        "allocationPolicy": {
            "instances": [{
                "policy": { 
                    "machineType": "e2-standard-4", 
                    "provisioningModel": "SPOT",
                    "bootDisk": {
                        "sizeGb": "100" # Fixed: placed inside bootDisk object
                    }
                }
            }]
        },
        "logsPolicy": { "destination": "CLOUD_LOGGING" }
    }
    return job_config

def submit_stress_test():
    # Targeting ALL Histosols tiles (~1,110 files) for a full statewide stress test
    test_glob = "*_Histosols.tif"
    print(f"Scanning GCS for FULL STRESS TEST (Histosols): {GCS_INPUT_PATH}{test_glob}")
    
    try:
        result = subprocess.check_output(f"gsutil ls {GCS_INPUT_PATH}{test_glob}", shell=True).decode()
        all_files = [f for f in result.strip().split('\n') if f]
    except Exception as e:
        print(f"No files found for stress test pattern: {e}")
        return

    soil_order = "Histosols"
    job_id = f"stress-test-histosols-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}"
    
    print(f"-> Submitting FULL STRESS TEST for {soil_order} ({len(all_files)} tiles)...")
    config = create_batch_job_config(soil_order, all_files)
    
    config_filename = f"config_stress_{soil_order}.json"
    with open(config_filename, "w") as f:
        json.dump(config, f)
        
    run_command(f"gcloud batch jobs submit {job_id} --location {REGION} --config {config_filename} --project {PROJECT_ID}")
    os.remove(config_filename)

if __name__ == "__main__":
    submit_stress_test()