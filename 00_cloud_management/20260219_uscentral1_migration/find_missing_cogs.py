"""
Script to compare GCS COGs with GEE Assets (Folder or ImageCollection) to identify and ingest missing assets.

Usage Examples:
    # Just list missing assets
    python3 find_missing_cogs.py \
        --gcs_uri gs://akveg-data/covariates_v20240711/ \
        --gee_asset projects/akveg-map/assets/covariates_v20240711

    # List and save to CSV
    python3 find_missing_cogs.py \
        --gcs_uri gs://akveg-data/covariates_v20240711/ \
        --gee_asset projects/akveg-map/assets/covariates_v20240711 \
        --output_csv missing_covariates.csv

    # Identify and immediately ingest missing assets
    python3 find_missing_cogs.py \
        --gcs_uri gs://akveg-data/covariates_v20240711/ \
        --gee_asset projects/akveg-map/assets/covariates_v20240711 \
        --ingest
"""
import argparse
import logging
import os
import csv
import ee
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_gcs_tifs(gcs_uri):
    """Lists all .tif files in a GCS bucket/prefix."""
    if not gcs_uri.startswith("gs://"):
        raise ValueError("GCS URI must start with gs://")
    
    parts = gcs_uri[5:].split("/", 1)
    bucket_name = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    
    # Ensure prefix ends with / if it's a folder-like path and not a file
    if prefix and not prefix.endswith('/') and not prefix.lower().endswith('.tif'):
        prefix += '/'

    logging.info(f"Listing GCS blobs in gs://{bucket_name}/{prefix}...")
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    
    tif_map = {} # basename_no_ext -> full_uri
    count = 0
    for blob in blobs:
        if blob.name.lower().endswith('.tif'):
            filename = os.path.basename(blob.name)
            key = os.path.splitext(filename)[0]
            tif_map[key] = f"gs://{bucket_name}/{blob.name}"
            count += 1
            
    logging.info(f"Found {count} .tif files in GCS.")
    return tif_map

def get_gee_assets(asset_path):
    """Lists all images in a GEE asset path (Folder or ImageCollection)."""
    logging.info(f"Listing GEE assets in {asset_path}...")
    asset_map = {}
    
    try:
        page_token = None
        while True:
            params = {'parent': asset_path}
            if page_token:
                params['pageToken'] = page_token
            
            response = ee.data.listAssets(params)
            assets = response.get('assets', [])
            
            for asset in assets:
                if asset['type'] == 'IMAGE':
                    # asset['name'] is projects/proj/assets/path/assetId
                    basename = os.path.basename(asset['name'])
                    asset_map[basename] = asset['name']
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break
                
    except ee.EEException as e:
        logging.error(f"Error listing GEE assets: {e}")
        return None

    logging.info(f"Found {len(asset_map)} images in GEE.")
    return asset_map

def create_cog_asset(uri, parent_path, extra_props=None, time_dict=None):
    """Creates a single COG asset."""
    filename = os.path.basename(uri)
    asset_name = os.path.splitext(filename)[0]
    asset_id = f"{parent_path}/{asset_name}"
    
    properties = {'source_uri': uri}
    if extra_props:
        properties.update(extra_props)

    request = {
        'type': 'IMAGE',
        'name': asset_id,
        'gcs_location': {'uris': [uri]},
        'properties': properties
    }
    
    if time_dict:
        request.update(time_dict)
    
    try:
        ee.data.createAsset(request)
        return True
    except ee.EEException as e:
        logging.error(f"Failed to create asset {asset_id}: {e}")
        return False

def ingest_missing_assets(missing_items, parent_path, extra_props=None, time_dict=None):
    """Ingests missing assets in parallel."""
    logging.info(f"Starting ingestion of {len(missing_items)} assets...")
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        # missing_items is list of (key, uri)
        futures = [executor.submit(create_cog_asset, uri, parent_path, extra_props, time_dict) for key, uri in missing_items]
        
        for i, future in enumerate(futures):
            if i > 0 and i % 10 == 0:
                logging.info(f"Processed {i}/{len(missing_items)}...")
            
            if future.result():
                success_count += 1
                
    logging.info(f"Ingestion complete. Successfully created {success_count}/{len(missing_items)} assets.")

def main():
    parser = argparse.ArgumentParser(description="Compare GCS COGs and GEE Assets to find missing ones.")
    parser.add_argument("--gcs_uri", required=True, help="GCS URI (e.g., gs://bucket/folder)")
    parser.add_argument("--gee_asset", required=True, help="GEE Asset Path (e.g., projects/my-proj/assets/my-collection)")
    parser.add_argument("--output_csv", help="Optional path to save missing assets CSV.")
    parser.add_argument("--ingest", action="store_true", help="Ingest missing assets immediately.")
    
    args = parser.parse_args()

    # Ensure no trailing slash in GEE asset path (important for constructing child paths)
    args.gee_asset = args.gee_asset.rstrip('/')

    # Initialize EE
    try:
        ee.Initialize()
    except Exception:
        logging.info("Authenticating...")
        ee.Authenticate()
        ee.Initialize()

    # 1. Get GCS files
    gcs_tifs = get_gcs_tifs(args.gcs_uri)
    
    # 2. Get GEE assets
    gee_assets = get_gee_assets(args.gee_asset)
    
    if gee_assets is None:
        logging.error("Could not list GEE assets. Check if the folder or collection exists.")
        return

    # 3. Compare and Select Template
    missing_in_gee = []
    extra_in_gee = []
    
    # Find items in GCS but not in GEE
    for key, uri in sorted(gcs_tifs.items()):
        if key not in gee_assets:
            missing_in_gee.append((key, uri))

    # Find items in GEE but not in GCS (potential orphans)
    for key in sorted(gee_assets.keys()):
        if key not in gcs_tifs:
            extra_in_gee.append(key)

    # Select a sample asset for properties
    # Prefer one that exists in both GCS and GEE to ensure it's current
    sample_asset_id = None
    common_keys = set(gcs_tifs.keys()) & set(gee_assets.keys())
    
    if common_keys:
        sample_key = next(iter(common_keys))
        sample_asset_id = gee_assets[sample_key]
        logging.info(f"Selected template asset (present in both): {sample_asset_id}")
    elif gee_assets:
        # Fallback: take any GEE asset
        sample_asset_id = next(iter(gee_assets.values()))
        logging.warning(f"Selected template asset (only in GEE): {sample_asset_id}")

    # Fetch template properties if available
    extra_props = {}
    time_dict = {}
    if sample_asset_id:
        try:
            logging.info(f"Fetching template properties from {sample_asset_id}...")
            info = ee.data.getAsset(sample_asset_id)
            if 'properties' in info:
                extra_props = {k: v for k, v in info['properties'].items() if not k.startswith('system:')}
            if 'startTime' in info:
                time_dict['startTime'] = info['startTime']
            if 'endTime' in info:
                time_dict['endTime'] = info['endTime']
            logging.info(f"Template properties: {list(extra_props.keys())}")
        except Exception as e:
            logging.warning(f"Failed to fetch template asset: {e}")

    logging.info(f"Comparison Complete.")
    logging.info(f"Total GCS TIFs: {len(gcs_tifs)}")
    logging.info(f"Total GEE Images: {len(gee_assets)}")
    logging.info(f"Missing in GEE: {len(missing_in_gee)}")
    logging.info(f"Extra in GEE (orphans): {len(extra_in_gee)}")
    
    if extra_in_gee:
        print("\nSample of extra assets in GEE (orphans - present in GEE but missing in GCS):")
        for key in extra_in_gee[:10]:
            print(f"  {gee_assets[key]}")
        if len(extra_in_gee) > 10:
            print(f"  ... and {len(extra_in_gee) - 10} more.")

        if args.output_csv:
            base, ext = os.path.splitext(args.output_csv)
            orphans_csv = f"{base}_orphans{ext}"
            try:
                with open(orphans_csv, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['asset_name', 'gee_asset_id'])
                    for key in extra_in_gee:
                        writer.writerow([key, gee_assets[key]])
                logging.info(f"Written orphan assets list to {orphans_csv}")
            except Exception as e:
                logging.error(f"Failed to write orphans CSV: {e}")

    if missing_in_gee:
        if args.output_csv:
            try:
                with open(args.output_csv, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['asset_name', 'gcs_uri', 'target_asset_id'])
                    for key, uri in missing_in_gee:
                        target_id = f"{args.gee_asset}/{key}"
                        writer.writerow([key, uri, target_id])
                logging.info(f"Written missing assets list to {args.output_csv}")
            except Exception as e:
                logging.error(f"Failed to write CSV: {e}")
        else:
            # Print first 10 if no CSV
            print("\nSample of missing assets:")
            for key, uri in missing_in_gee[:10]:
                print(f"  {key} -> {uri}")
            if len(missing_in_gee) > 10:
                print(f"  ... and {len(missing_in_gee) - 10} more.")

        if args.ingest:
            ingest_missing_assets(missing_in_gee, args.gee_asset, extra_props, time_dict)
    else:
        logging.info("No missing assets found. Everything is in sync!")

if __name__ == "__main__":
    main()