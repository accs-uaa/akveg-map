import ee
import logging
import time
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging to see the progress in the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RepairContext:
    def __init__(self, limit=None):
        self.limit = limit
        self.success_count = 0

    def should_stop(self):
        return self.limit is not None and self.success_count >= self.limit

    def record_success(self):
        self.success_count += 1

def repair_single_asset(asset_id):
    """
    Forces Google Earth Engine to re-index a single COG-backed image asset.
    Because Earth Engine's createAsset endpoint is extremely strict about the 
    payload signature for external COGs, we use a minimal payload to register 
    the file, and then safely restore the properties via updateAsset.
    """
    try:
        # Fetch the current asset metadata
        info = ee.data.getAsset(asset_id)
        
        if info.get('type') != 'IMAGE':
            logging.warning(f"Asset {asset_id} is not an IMAGE. Skipping.")
            return False

        # Drill down into the metadata structure to find the GCS URIs
        tilesets = info.get('tilesets', [])
        if not tilesets:
            logging.debug(f"No tilesets found for {asset_id}. Likely an ingested asset, not COG-backed.")
            return False
        
        sources = tilesets[0].get('sources', [])
        if not sources:
            return False
            
        current_uris = sources[0].get('uris', [])
        
        if current_uris:
            # CRITICAL FIX: Split on '#' and keep only the base gs:// path.
            base_uri = current_uris[0].split('#')[0]
            
            # Extract metadata to preserve
            clean_props = {}
            if 'properties' in info:
                for k, v in info['properties'].items():
                    if not k.startswith('system:'):
                        clean_props[k] = v
                        
            start_time = info.get('startTime')
            end_time = info.get('endTime')

            # 1. Rename the existing asset to a backup (Safety Mechanism)
            backup_id = f"{asset_id}_backup_{int(time.time())}"
            try:
                ee.data.renameAsset(asset_id, backup_id)
                logging.info(f"Backed up original asset to {backup_id}")
            except Exception as e:
                logging.error(f"Failed to backup (rename) {asset_id}: {e}")
                return False

            # 2. Recreate the asset (With Metadata)
            recreation_success = False
            manifest = {
                'type': 'IMAGE',
                'name': asset_id,
                'gcs_location': {'uris': [base_uri]},
                'properties': clean_props
            }
            if start_time:
                manifest['startTime'] = start_time
            if end_time:
                manifest['endTime'] = end_time
            
            logging.info(f"Attempting to register COG from: {base_uri}")
            
            for attempt in range(3):
                try:
                    # Try creating with full metadata
                    ee.data.createAsset(manifest)
                    recreation_success = True
                    break
                except Exception as e:
                    logging.warning(f"API creation attempt {attempt + 1} failed: {e}")
                    time.sleep(2)
                        
            if not recreation_success:
                logging.error(f"Failed to recreate {asset_id}. Restoring backup...")
                try:
                    ee.data.renameAsset(backup_id, asset_id)
                    logging.info(f"Restored backup for {asset_id}")
                except Exception as restore_e:
                    logging.error(f"CRITICAL: Failed to restore backup {backup_id} to {asset_id}: {restore_e}")
                return False

            # 3. Delete the backup if creation succeeded
            try:
                ee.data.deleteAsset(backup_id)
            except Exception as e:
                logging.warning(f"Failed to delete backup {backup_id}: {e}")

            logging.info(f"Successfully recreated and re-indexed: {asset_id}")
            return True
            
        else:
            logging.warning(f"No gs:// URIs found for {asset_id}.")
            return False

    except Exception as e:
        logging.error(f"Failed to process {asset_id}: {e}")
        return False

def repair_image_collection(ic_path, context=None):
    """
    Iterates through an ImageCollection and repairs all COG-backed images inside it.
    Uses ee.data.listAssets which is safer and faster for large collections 
    compared to evaluating aggregate_array() on the server.
    """
    logging.info(f"Starting repair for ImageCollection: {ic_path}")
    
    try:
        # 1. List all assets first to enable parallel processing
        all_images = []
        page_token = None
        
        while True:
            params = {'parent': ic_path}
            if page_token:
                params['pageToken'] = page_token
                
            response = ee.data.listAssets(params)
            assets = response.get('assets', [])
            
            for asset in assets:
                if asset['type'] == 'IMAGE':
                    all_images.append(asset['name'])
                    
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        
        logging.info(f"Found {len(all_images)} images in {ic_path}. Starting parallel repair...")

        # 2. Define worker function
        def process_asset(asset_id):
            if context and context.should_stop():
                return False
            success = repair_single_asset(asset_id)
            if success and context:
                context.record_success()
            return success

        # 3. Execute in parallel
        # Using 10 workers to balance speed vs API rate limits (each repair = 3 API calls)
        success_count = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_asset, asset_id) for asset_id in all_images]
            
            for future in as_completed(futures):
                if context and context.should_stop():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                if future.result():
                    success_count += 1

        logging.info(f"Completed repair for {ic_path}. Repaired: {success_count}/{len(all_images)}")
        
    except Exception as e:
        logging.error(f"Failed to process ImageCollection {ic_path}: {e}")

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
    parser = argparse.ArgumentParser(description="Repair COG-backed assets in GEE.")
    parser.add_argument("--limit", type=int, help="Limit the number of successful repairs.")
    parser.add_argument("--images", action="store_true", help="Process standalone Images.")
    parser.add_argument("--collections", action="store_true", help="Process ImageCollections.")
    args = parser.parse_args()

    # Initialize the Earth Engine Python API
    try:
        ee.Initialize()
    except Exception as e:
        logging.warning("Standard initialization failed. Attempting to authenticate...")
        ee.Authenticate()
        ee.Initialize()
        
    # ==========================================
    # CONFIGURATION & EXECUTION
    # ==========================================
    
    context = RepairContext(limit=args.limit)

    # Determine what to run (default to both if neither specified)
    run_images = args.images
    run_collections = args.collections
    if not run_images and not run_collections:
        run_images = True
        run_collections = True

    # === CRAWLER ENABLED ===
    ROOT_ASSET_PATH = 'projects/akveg-map/assets'
    logging.info(f"Starting automated discovery in {ROOT_ASSET_PATH}...")
    
    collections, standalone_images = discover_assets(ROOT_ASSET_PATH)
    
    logging.info(f"Discovery complete. Found {len(collections)} ImageCollections and {len(standalone_images)} standalone Images.")
    
    if run_images:
        logging.info("--- Repairing Standalone Images ---")
        for img in standalone_images:
            if context.should_stop():
                break
            if repair_single_asset(img):
                context.record_success()
        
    if run_collections:
        logging.info("--- Repairing ImageCollections ---")
        for ic in collections:
            if context.should_stop():
                break
            repair_image_collection(ic, context=context)
        
    # === RUN A PILOT TEST INSTEAD ===
    # test_asset = 'projects/akveg-map/assets/covariates_v20240711/CoastDist_10m_3338'
    # test_asset = 'projects/akveg-map/assets/covariates_v20240711/Elevation_10m_3338'
    # test_asset = 'projects/akveg-map/assets/covariates_v20240711/Position_10m_3338'
    # test_asset = 'projects/akveg-map/assets/covariates_v20240711/RadiationAspect_10m_3338'
    # test_asset = 'projects/akveg-map/assets/covariates_v20240711/Slope_10m_3338'
    # test_asset = 'projects/akveg-map/assets/covariates_v20240711/HeatLoad_10m_3338'
    # test_asset = 'projects/akveg-map/assets/covariates_v20240711/Relief_10m_3338'
    # logging.info(f"Running pilot test on single asset: {test_asset}")
    # repair_single_asset(test_asset)
    
    logging.info("All repair operations finished.")