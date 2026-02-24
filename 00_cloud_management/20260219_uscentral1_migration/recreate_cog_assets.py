import argparse
import logging
import os
import ee
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_assets_in_parallel(asset_list):
    """Deletes a list of assets using a ThreadPoolExecutor."""
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(ee.data.deleteAsset, asset['name']) for asset in asset_list]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Delete failed: {e}")

def delete_collection_and_contents(asset_id):
    """Deletes an ImageCollection and all its contents."""
    try:
        try:
            ee.data.getAsset(asset_id)
        except ee.EEException:
            logging.info(f"Asset {asset_id} does not exist. Skipping delete.")
            return

        logging.info(f"Scanning contents of {asset_id} for deletion...")
        all_assets = []
        page_token = None
        while True:
            params = {'parent': asset_id}
            if page_token:
                params['pageToken'] = page_token
            response = ee.data.listAssets(params)
            if 'assets' in response:
                all_assets.extend(response['assets'])
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        
        if all_assets:
            logging.info(f"Deleting {len(all_assets)} child assets...")
            delete_assets_in_parallel(all_assets)
        
        logging.info(f"Deleting collection {asset_id}...")
        ee.data.deleteAsset(asset_id)
        logging.info("Delete complete.")

    except Exception as e:
        logging.error(f"Error during collection delete: {e}")
        raise

def create_image_collection(asset_id):
    """Creates an empty ImageCollection."""
    logging.info(f"Creating ImageCollection {asset_id}...")
    try:
        ee.data.createAsset({'type': 'IMAGE_COLLECTION', 'name': asset_id})
        logging.info("Collection created.")
    except ee.EEException as e:
        logging.warning(f"Failed to create collection (might exist): {e}")

def list_gcs_blobs(bucket_name, prefix):
    """Lists all TIF blobs in a GCS bucket/prefix."""
    logging.info(f"Listing files in gs://{bucket_name}/{prefix}...")
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    
    tif_files = []
    for blob in blobs:
        if blob.name.endswith('.tif'):
            tif_files.append(f"gs://{bucket_name}/{blob.name}")
    
    logging.info(f"Found {len(tif_files)} TIF files.")
    return tif_files

def create_cog_asset(uri, collection_id):
    """Worker function to create a single COG asset."""
    filename = os.path.basename(uri)
    asset_name = os.path.splitext(filename)[0]
    asset_id = f"{collection_id}/{asset_name}"
    
    request = {
        'type': 'IMAGE',
        'name': asset_id,
        'gcs_location': {'uris': [uri]},
        'properties': {'source_uri': uri}
    }
    
    try:
        ee.data.createAsset(request)
        return True
    except ee.EEException as e:
        logging.error(f"Failed to create asset {asset_id}: {e}")
        return False

def ingest_cogs(tif_list, collection_id):
    """Ingests list of GCS URIs into the GEE Collection in parallel."""
    logging.info(f"Starting parallel ingestion of {len(tif_list)} assets...")
    
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all tasks
        futures = [executor.submit(create_cog_asset, uri, collection_id) for uri in tif_list]
        
        # Monitor progress
        for i, future in enumerate(futures):
            if i > 0 and i % 50 == 0:
                logging.info(f"Processed {i}/{len(tif_list)} assets...")
            
            if future.result():
                success_count += 1
                
    logging.info(f"Ingestion complete. Successfully created {success_count}/{len(tif_list)} assets.")

def ingest_single_image(asset_id, uri):
    """Ingests a single COG asset."""
    logging.info(f"Creating single asset {asset_id} from {uri}...")
    request = {
        'type': 'IMAGE',
        'name': asset_id,
        'gcs_location': {'uris': [uri]},
        'properties': {'source_uri': uri}
    }
    try:
        ee.data.createAsset(request)
        logging.info(f"Successfully created {asset_id}")
    except ee.EEException as e:
        logging.error(f"Failed to create asset {asset_id}: {e}")

def parse_gcs_uri(uri):
    """Splits gs://bucket/path/to/file into bucket and path."""
    if not uri.startswith("gs://"):
        raise ValueError("URI must start with gs://")
    parts = uri[5:].split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix

def main():
    parser = argparse.ArgumentParser(description="Recreate COG-backed assets in GEE.")
    parser.add_argument("--asset_id", required=True, help="GEE Asset ID")
    parser.add_argument("--uri", required=True, help="GCS URI or Folder URI")
    parser.add_argument("--type", choices=['IMAGE', 'IMAGE_COLLECTION'], required=True, help="Asset type")
    parser.add_argument("--force", action='store_true', help="Delete existing asset before creating")
    
    args = parser.parse_args()
    
    try:
        ee.Initialize()
    except Exception:
        ee.Authenticate()
        ee.Initialize()
        
    args.asset_id = args.asset_id.rstrip('/')

    if args.type == 'IMAGE_COLLECTION':
        if args.force:
            delete_collection_and_contents(args.asset_id)
        
        create_image_collection(args.asset_id)
        
        bucket, prefix = parse_gcs_uri(args.uri)
        # If URI points to a file, use its parent folder
        if prefix.lower().endswith('.tif'):
            prefix = os.path.dirname(prefix)
        if prefix and not prefix.endswith('/'):
            prefix += '/'
            
        tifs = list_gcs_blobs(bucket, prefix)
        ingest_cogs(tifs, args.asset_id)
        
    elif args.type == 'IMAGE':
        if args.force:
            try:
                ee.data.deleteAsset(args.asset_id)
                logging.info(f"Deleted existing asset {args.asset_id}")
            except ee.EEException:
                pass
        ingest_single_image(args.asset_id, args.uri)

if __name__ == "__main__":
    main()