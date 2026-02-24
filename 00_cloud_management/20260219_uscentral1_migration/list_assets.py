"""
Script to recursively discover GEE assets and identify COG-backed ones.

Usage Examples:
    # List all assets in default project and print to console
    python3 list_assets.py

    # List assets in specific folder
    python3 list_assets.py projects/my-project/assets/my-folder

    # Export COG-backed assets to CSVs for batch processing
    python3 list_assets.py --csv_images standalone_cogs.csv --csv_collections collection_cogs.csv

    # List and validate that GCS files exist
    python3 list_assets.py --validate
"""
import ee
import logging
import argparse
import csv
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_cog_uri(asset_id):
    """
    Inspects an asset to see if it is COG-backed.
    Returns the first GCS URI if found, otherwise None.
    """
    try:
        info = ee.data.getAsset(asset_id)
        if info.get('type') != 'IMAGE':
            return None
            
        tilesets = info.get('tilesets', [])
        if tilesets:
            sources = tilesets[0].get('sources', [])
            if sources:
                uris = sources[0].get('uris', [])
                if uris:
                    return uris[0].split('#')[0]
    except Exception as e:
        logging.debug(f"Error inspecting {asset_id}: {e}")
    return None

def check_collection_cog(collection_id):
    """
    Checks if an ImageCollection appears to be COG-backed by inspecting its first image.
    Returns:
        - URI string if COG-backed
        - "EMPTY" if collection is empty
        - None if images exist but are not COG-backed
    """
    try:
        params = {'parent': collection_id, 'pageSize': 1}
        response = ee.data.listAssets(params)
        assets = response.get('assets', [])
        
        if not assets:
            return "EMPTY"
            
        first_asset = assets[0]
        if first_asset['type'] == 'IMAGE':
            return get_cog_uri(first_asset['name'])
            
    except Exception as e:
        logging.warning(f"Error checking collection {collection_id}: {e}")
        return None

def validate_collection_full(collection_id, storage_client):
    """
    Validates all images in a collection.
    Returns (total_count, missing_count, sample_uri).
    """
    images = []
    try:
        page_token = None
        while True:
            params = {'parent': collection_id}
            if page_token:
                params['pageToken'] = page_token
            response = ee.data.listAssets(params)
            for asset in response.get('assets', []):
                if asset['type'] == 'IMAGE':
                    images.append(asset['name'])
            page_token = response.get('nextPageToken')
            if not page_token:
                break
    except Exception as e:
        logging.error(f"Error listing collection {collection_id}: {e}")
        return 0, 0, None

    if not images:
        return 0, 0, None

    missing_count = 0
    sample_uri = None
    
    def check_asset(asset_id):
        uri = get_cog_uri(asset_id)
        is_missing = False
        if uri:
            if not validate_gcs_uri(uri, storage_client):
                is_missing = True
        return uri, is_missing

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_asset = {executor.submit(check_asset, img): img for img in images}
        for future in as_completed(future_to_asset):
            try:
                uri, is_missing = future.result()
                if uri and not sample_uri:
                    sample_uri = uri
                if is_missing:
                    missing_count += 1
            except Exception as e:
                logging.warning(f"Error checking asset: {e}")

    return len(images), missing_count, sample_uri

def validate_gcs_uri(uri, storage_client):
    """Checks if the GCS object exists."""
    if not uri or not uri.startswith("gs://"):
        return False
    try:
        parts = uri[5:].split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1]
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.exists()
    except Exception as e:
        logging.warning(f"Validation error for {uri}: {e}")
        return False

def discover_assets(parent_path):
    """
    Recursively discovers all ImageCollections and standalone Images
    within a given Earth Engine asset folder.
    """
    found_collections = []
    found_standalone_images = []
    
    logging.info(f"Scanning folder: {parent_path}...")
    
    try:
        page_token = None
        while True:
            params = {'parent': parent_path}
            if page_token:
                params['pageToken'] = page_token
            
            response = ee.data.listAssets(params)
            assets = response.get('assets', [])
            
            for asset in assets:
                asset_id = asset['name']
                asset_type = asset['type']
                
                if asset_type == 'FOLDER':
                    # Recursively search subfolders
                    sub_ics, sub_imgs = discover_assets(asset_id)
                    found_collections.extend(sub_ics)
                    found_standalone_images.extend(sub_imgs)
                elif asset_type == 'IMAGE_COLLECTION':
                    found_collections.append(asset_id)
                elif asset_type == 'IMAGE':
                    found_standalone_images.append(asset_id)
                    
            page_token = response.get('nextPageToken')
            if not page_token:
                break
                
    except Exception as e:
        logging.error(f"Error accessing {parent_path}: {e}")
        
    return found_collections, found_standalone_images

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively list Images and ImageCollections in GEE.")
    parser.add_argument("root_path", nargs='?', default='projects/akveg-map/assets', 
                        help="Root asset path to scan (default: projects/akveg-map/assets)")
    parser.add_argument("--csv_images", help="Optional path to export COG standalone images to a CSV file.")
    parser.add_argument("--csv_collections", help="Optional path to export COG image collections to a CSV file.")
    parser.add_argument("--validate", action="store_true", help="Check if GCS files exist for COG assets.")
    
    args = parser.parse_args()

    # Initialize the Earth Engine Python API
    try:
        ee.Initialize()
    except Exception as e:
        logging.warning("Standard initialization failed. Attempting to authenticate...")
        ee.Authenticate()
        ee.Initialize()

    storage_client = None
    if args.validate:
        storage_client = storage.Client()
        
    logging.info(f"Starting automated discovery in {args.root_path}...")
    
    collections, standalone_images = discover_assets(args.root_path)
    
    cog_collections = []
    cog_images = []

    print("\n" + "="*120)
    print(f"IMAGE COLLECTIONS ({len(collections)})")
    print(f"{'Asset ID':<60} | {'Status':<10} | {'Miss/Total':<12} | {'Sample COG URI'}")
    print("="*120)
    for ic in sorted(collections):
        if args.validate:
            total, missing, uri = validate_collection_full(ic, storage_client)
            if total == 0:
                status = "EMPTY"
                counts = "0/0"
                display_uri = "-"
            elif uri:
                status = "COG"
                if missing > 0:
                    status = "MISSING"
                counts = f"{missing}/{total}"
                display_uri = uri
            else:
                status = "INGESTED"
                counts = f"0/{total}"
                display_uri = "-"
        else:
            # Quick check (first asset only)
            uri = check_collection_cog(ic)
            counts = "-"
            if uri == "EMPTY":
                status = "EMPTY"
                display_uri = "-"
            elif uri:
                status = "COG"
                display_uri = uri
            else:
                status = "INGESTED"
                display_uri = "-"
        
        if status in ["COG", "MISSING"]:
             cog_collections.append({'asset_id': ic, 'type': 'IMAGE_COLLECTION', 'uri': display_uri, 'status': status})
             
        print(f"{ic:<60} | {status:<10} | {counts:<12} | {display_uri}")
        
    print("\n" + "="*120)
    print(f"STANDALONE IMAGES ({len(standalone_images)})")
    print(f"{'Asset ID':<60} | {'Status':<10} | {'Miss/Total':<12} | {'COG URI'}")
    print("="*120)
    for img in sorted(standalone_images):
        uri = get_cog_uri(img)
        counts = "-"
        if uri:
            status = "COG"
            display_uri = uri
            if args.validate:
                counts = "0/1"
                if not validate_gcs_uri(uri, storage_client):
                    status = "MISSING"
                    counts = "1/1"
                    logging.warning(f"Image {img} URI missing: {uri}")
            cog_images.append({'asset_id': img, 'type': 'IMAGE', 'uri': uri, 'status': status})
        else:
            status = "INGESTED"
            display_uri = "-"
        print(f"{img:<60} | {status:<10} | {counts:<12} | {display_uri}")
        
    logging.info(f"Discovery complete. Found {len(collections)} ImageCollections and {len(standalone_images)} standalone Images.")

    if args.csv_collections:
        try:
            with open(args.csv_collections, 'w', newline='') as csvfile:
                fieldnames = ['asset_id', 'type', 'uri', 'status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in cog_collections:
                    writer.writerow(item)
            logging.info(f"Exported {len(cog_collections)} COG collections to {args.csv_collections}")
        except Exception as e:
            logging.error(f"Failed to write collections CSV: {e}")

    if args.csv_images:
        try:
            with open(args.csv_images, 'w', newline='') as csvfile:
                fieldnames = ['asset_id', 'type', 'uri', 'status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in cog_images:
                    writer.writerow(item)
            logging.info(f"Exported {len(cog_images)} COG images to {args.csv_images}")
        except Exception as e:
            logging.error(f"Failed to write images CSV: {e}")

    if args.validate:
        missing_ic = sum(1 for c in cog_collections if c.get('status') == 'MISSING')
        missing_img = sum(1 for i in cog_images if i.get('status') == 'MISSING')
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print(f"Missing ImageCollections: {missing_ic}")
        print(f"Missing Images:           {missing_img}")
        print("="*60)