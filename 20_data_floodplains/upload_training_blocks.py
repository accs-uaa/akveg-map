# upload_training_blocks.py
# run from ee conda env
# conda activate ee
import os
import subprocess
import glob
import time

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# 1. Local path to your folder containing the .tif files
# LOCAL_DIR = "/data/gis/gis_projects/2024/24-261_AKVEG_Riparian_BLM/label_rasters/v20260130"
LOCAL_DIR = "/data/gis/gis_projects/2024/24-261_AKVEG_Riparian_BLM/label_rasters/v20260211b"

# 2. Your Google Cloud Storage Bucket (must exist)
# Format: gs://your-bucket-name/optional-subfolder
# GCS_BUCKET = "gs://akveg-data/surficial_features/floodplain_label_rasters/v20260130"
GCS_BUCKET = "gs://akveg-data/surficial_features/floodplain_label_rasters/v20260211b"

# 3. Target GEE Asset ID for the Collection
# Format: projects/your-project/assets/collection_name
# OR: users/your_username/collection_name
GEE_COLLECTION = "projects/akveg-map/assets/surficial_features/floodplain_label_rasters/v20260211b"

# 4. Path to the 'earthengine' CLI tool if not in system PATH
# Usually just 'earthengine' works if installed via pip
EE_CLI = "earthengine"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def run_command(cmd):
    """Runs a shell command and prints output."""
    try:
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        exit(1)

def ensure_parent_folders(full_asset_id):
    """
    Recursively checks and creates parent folders for a given asset ID.
    Supports projects/PROJECT/assets/... and users/USERNAME/...
    """
    parts = full_asset_id.split('/')
    
    # Identify where the relative path starts
    # Case 1: projects/my-proj/assets/folder1/folder2/collection
    if parts[0] == 'projects' and 'assets' in parts:
        try:
            # Start after 'assets'
            root_idx = parts.index('assets') + 1
        except ValueError:
            root_idx = 3 # Fallback
    # Case 2: users/username/folder1/folder2/collection
    elif parts[0] == 'users':
        root_idx = 2
    else:
        # Fallback for unknown structures, just try to handle from root
        root_idx = 0 

    # Reconstruct path and create folders up to the parent of the final collection
    # We slice up to -1 because the last part is the collection itself
    current_path = "/".join(parts[:root_idx])
    
    for folder in parts[root_idx:-1]:
        current_path = f"{current_path}/{folder}"
        
        # Check if folder exists
        check = subprocess.run([EE_CLI, "asset", "info", current_path], 
                             capture_output=True, text=True)
        
        if check.returncode != 0:
            print(f"Parent folder missing. Creating: {current_path}")
            # Try creating folder
            run_command([EE_CLI, "create", "folder", current_path])

def check_collection_exists(asset_id):
    """Checks if the GEE collection exists, creates if not."""
    
    # First, ensure the folder structure leading up to it exists
    ensure_parent_folders(asset_id)

    print(f"Checking if collection {asset_id} exists...")
    result = subprocess.run([EE_CLI, "asset", "info", asset_id], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Collection not found. Creating {asset_id}...")
        run_command([EE_CLI, "create", "collection", asset_id])
    else:
        print("Collection exists.")

# ==============================================================================
# MAIN WORKFLOW
# ==============================================================================

def main():
    # 1. Get list of TIF files
    tif_files = glob.glob(os.path.join(LOCAL_DIR, "*.tif"))
    if not tif_files:
        print(f"No .tif files found in {LOCAL_DIR}")
        exit(1)
        
    print(f"Found {len(tif_files)} files to process.")

    # 2. Ensure GEE Collection exists
    check_collection_exists(GEE_COLLECTION)

    # 3. Loop through files
    for local_file in tif_files:
        filename = os.path.basename(local_file)
        asset_name = os.path.splitext(filename)[0]
        
        # Define paths
        gcs_path = f"{GCS_BUCKET}/{filename}"
        gee_asset_id = f"{GEE_COLLECTION}/{asset_name}"

        print(f"\n--- Processing {filename} ---")

        # A. Upload to GCS using gsutil
        # '-n' flag skips upload if file already exists in GCS (resumable)
        print("Uploading to GCS...")
        run_command(["gsutil", "cp", "-n", local_file, gcs_path])

        # B. Ingest into GEE
        # We use --pyramiding_policy=MODE because these are BINARY classes.
        # If we used MEAN (default), pixels would blend into floats (0.4) at zoom.
        print(f"Starting ingestion task for {gee_asset_id}...")
        
        # Check if asset already exists to prevent duplicate tasks
        check_asset = subprocess.run([EE_CLI, "asset", "info", gee_asset_id], 
                                   capture_output=True)
        
        if check_asset.returncode == 0:
            print(f"Skipping: Asset {gee_asset_id} already exists.")
            continue

        upload_cmd = [
            EE_CLI, "upload", "image",
            "--asset_id", gee_asset_id,
            "--pyramiding_policy", "MODE",  # CRITICAL for masks
            gcs_path
        ]
        
        run_command(upload_cmd)
        
    print("\nAll tasks submitted! Check the 'Tasks' tab in Code Editor or run 'earthengine task list'.")

if __name__ == "__main__":
    main()