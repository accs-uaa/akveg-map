"""
Migrate GeoTIFFs to Cloud Optimized GeoTIFF (COG) using Google Cloud Batch.

Usage Example:
    # Explicitly specifying input and output:
    python3 migrate_to_cog_batch.py \
      --input gs://akveg-data/covariates_v20240711_premigration/ \
      --output-folder gs://akveg-data/covariates_v20240711/

    # Or relying on auto-detection (removes "_premigration" suffix):
    python3 migrate_to_cog_batch.py \
      --input gs://akveg-data/covariates_v20240711_premigration/

    # Test run on a single image:
    python3 migrate_to_cog_batch.py \
      --input gs://akveg-data/covariates_v20240711_premigration/ --limit 1
"""
import os
import subprocess
import json
import datetime
import argparse
import sys
import time

# --- CONFIGURATION ---
PROJECT_ID = "akveg-map" 
REGION = "us-central1"

# GDAL container image
GDAL_IMAGE = "ghcr.io/osgeo/gdal:ubuntu-small-3.9.0"
CLOUD_SDK_IMAGE = "gcr.io/google.com/cloudsdktool/cloud-sdk:slim"

def run_command(cmd):
    """Utility to run shell commands"""
    try:
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def create_batch_job_config(input_uri, output_uri, job_id):
    """
    Generates the JSON config for a Google Cloud Batch job.
    """
    # Define local paths for processing to decouple I/O from CPU operations
    local_input = "/mnt/share/input.tif"
    local_output = "/mnt/share/output.tif"
    
    # Runnable 1: Download input using gsutil (fast sequential read)
    download_cmd = f"gsutil -q cp '{input_uri}' {local_input}"
    
    # Runnable 2: GDAL Translate (Local Disk -> Local Disk)
    # -of COG: Creates Cloud Optimized GeoTIFF
    # -co NUM_THREADS=ALL_CPUS: Uses all cores for compression/overview generation
    container_command = (
        f"gdal_translate {local_input} {local_output} "
        f"-of COG -co COMPRESS=DEFLATE -co PREDICTOR=2 -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS"
    )
    
    # Runnable 3: Upload output using gsutil (fast sequential write)
    upload_cmd = f"gsutil -q cp {local_output} '{output_uri}'"

    # Mount a unique directory from the host's writable /var/tmp to the container
    # /var/tmp is on the stateful partition (boot disk) of the COS VM.
    mount_options = f"--privileged -v /var/tmp/{job_id}:/mnt/share"

    job_config = {
        "taskGroups": [{
            "taskSpec": {
                "runnables": [
                    {
                        "container": {
                            "imageUri": CLOUD_SDK_IMAGE,
                            "commands": ["/bin/sh", "-c", download_cmd],
                            "options": mount_options
                        }
                    },
                    {
                        "container": {
                            "imageUri": GDAL_IMAGE,
                            "commands": ["/bin/sh", "-c", container_command],
                            "options": mount_options
                        }
                    },
                    {
                        "container": {
                            "imageUri": CLOUD_SDK_IMAGE,
                            "commands": ["/bin/sh", "-c", upload_cmd],
                            "options": mount_options
                        }
                    }
                ],
                "computeResource": {
                    "cpuMilli": "8000",
                    "memoryMib": "30000"
                },
                "maxRunDuration": "86400s" # 24 hours
            }
        }],
        "allocationPolicy": {
            "instances": [{
                "policy": {
                    "machineType": "e2-standard-8",
                    "provisioningModel": "STANDARD", 
                    "bootDisk": {
                        "sizeGb": "500"
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
    parser = argparse.ArgumentParser(description="Migrate GeoTIFFs to COG using Google Cloud Batch.")
    
    parser.add_argument("--input", required=True,
                        help="GCS path to input file or folder (e.g. gs://bucket/path/ or gs://bucket/file.tif).")
    
    parser.add_argument("--output-folder", 
                        help="Optional GCS output folder. If not provided, appends '_migrated' to input folder name.")
    
    parser.add_argument("--limit", type=int, help="Limit the number of jobs to submit (useful for testing).")

    args = parser.parse_args()

    input_path = args.input
    is_single_file = input_path.lower().endswith('.tif')
    
    files_to_process = []
    
    if is_single_file:
        files_to_process.append(input_path)
    else:
        # It's a folder or pattern
        if not input_path.endswith('/') and '*' not in input_path:
            input_path += '/'
            
        print(f"Scanning GCS for tiles matching: {input_path}")
        try:
            search_pattern = input_path
            if not '*' in search_pattern and search_pattern.endswith('/'):
                search_pattern += "*.tif"
                
            result = subprocess.check_output(f"gsutil ls {search_pattern}", shell=True).decode()
            files_to_process = [f for f in result.strip().split('\n') if f.lower().endswith('.tif')]
        except subprocess.CalledProcessError:
            print(f"No files found matching {input_path}")
            return

    # Determine default output folder if not provided
    if not args.output_folder:
        if is_single_file:
            base_dir = os.path.dirname(input_path)
        else:
            base_dir = os.path.dirname(search_pattern.replace('*', ''))
        
        if base_dir.endswith('/'):
            base_dir = base_dir[:-1]
        
        if "_premigration" in base_dir:
            args.output_folder = base_dir.replace("_premigration", "")
        else:
            print("Error: Input path does not contain '_premigration' and no --output-folder provided.")
            print("Please specify --output-folder explicitly.")
            sys.exit(1)

    if not args.output_folder.endswith('/'):
        args.output_folder += '/'

    print(f"Found {len(files_to_process)} files to process.")
    print(f"Output folder: {args.output_folder}")
    
    # Check for existing files to skip
    existing_files = set()
    try:
        print(f"Scanning output folder for existing files: {args.output_folder}")
        out_result = subprocess.check_output(f"gsutil ls {args.output_folder}", shell=True).decode()
        existing_files = {os.path.basename(f.strip()) for f in out_result.strip().split('\n') if f.strip()}
        print(f"Found {len(existing_files)} existing files.")
    except subprocess.CalledProcessError:
        print("Output folder does not exist or is empty.")

    submitted_count = 0
    for i, input_uri in enumerate(files_to_process):
        filename = os.path.basename(input_uri)
        
        if filename in existing_files:
            print(f"[{i+1}/{len(files_to_process)}] Skipping {filename} (already exists)")
            continue

        if args.limit is not None and submitted_count >= args.limit:
            print(f"Limit of {args.limit} job(s) reached. Stopping submission.")
            break

        output_uri = os.path.join(args.output_folder, filename)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_name = filename.lower().replace('_', '-').replace('.', '-').replace(' ', '-')[:30]
        job_id = f"mig-cog-{safe_name}-{timestamp}-{i}"

        print(f"[{i+1}/{len(files_to_process)}] Submitting Batch Job: {job_id}")
        config = create_batch_job_config(input_uri, output_uri, job_id)
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
        
        if os.path.exists(config_filename):
            os.remove(config_filename)
            
        submitted_count += 1
        time.sleep(1)

    print("\nAll jobs submitted.")

if __name__ == "__main__":
    main()