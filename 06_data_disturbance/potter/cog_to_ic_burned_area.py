# cog_to_ic_burned_area.py
# Scans GCS for burned area probability COGs and registers them to a GEE ImageCollection.
# Input pattern: gs://fisl_tundra_fire/burned_area_product/pred_probs/6000/{year}/{tile}.tif

import ee
import os
import json
import pandas as pd
from google.cloud import storage
from google.auth.transport.requests import AuthorizedSession
from datetime import datetime, timezone

# --- CONFIGURATION ---
EE_PROJECT = 'akveg-map'
GCS_PROJECT = 'akveg-map'  # Project used for GCS listing API quotas
GCS_BUCKET = 'fisl_tundra_fire'
GCS_PREFIX = 'burned_area_product/pred_probs/6000/'

# Output Image Collection
EE_COLLECTION = 'projects/fisl-tundra-fire/assets/potter_fire_v20260211'

# --- SETUP ---
try:
    ee.Initialize(project=EE_PROJECT)
except Exception:
    ee.Authenticate()
    ee.Initialize(project=EE_PROJECT)

session = AuthorizedSession(ee.data.get_persistent_credentials().with_quota_project(EE_PROJECT))

def get_tif_list(project_name, bucket_name, prefix):
    """Lists all TIF files in a GCS bucket with a given prefix (recursive)."""
    print(f"Listing files in gs://{bucket_name}/{prefix}...")
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(bucket_name)
    
    # list_blobs is recursive by default if delimiter is not set
    blobs = bucket.list_blobs(prefix=prefix)
    tif_list = []
    for blob in blobs:
        if blob.name.endswith('.tif'):
            tif_list.append(f"gs://{bucket_name}/{blob.name}")
    
    return pd.DataFrame(tif_list, columns=['tif'])

def create_collection_if_not_exists(collection_id):
    """Creates the ImageCollection if it doesn't exist."""
    try:
        ee.data.getAsset(collection_id)
        print(f"Collection {collection_id} already exists.")
    except ee.EEException:
        print(f"Creating collection {collection_id}...")
        ee.data.createAsset({'type': 'IMAGE_COLLECTION'}, collection_id)

def gcs_cogs_to_collection(cogs_df, collection_path):
    """
    Uploads COGs to GEE ImageCollection with metadata parsing.
    Expected path format: .../6000/{year}/{tile}.tif
    """
    print(f"Starting registration to {collection_path}...")
    
    for cog_uri in cogs_df['tif']:
        # Parse path
        # Example: gs://fisl_tundra_fire/burned_area_product/pred_probs/6000/2001/91.tif
        parts = cog_uri.split('/')
        filename = parts[-1]
        year_str = parts[-2]
        
        # Validation
        if not year_str.isdigit():
            print(f"Skipping {cog_uri}: Could not parse year from '{year_str}'")
            continue
            
        tile_id = filename.replace('.tif', '')
        year = int(year_str)
        
        # Asset ID: y2001_t91
        asset_name = f"y{year}_t{tile_id}"
        asset_id = f"{collection_path}/{asset_name}"
        
        # Time properties (Jan 1st of year to Jan 1st of next year)
        dt_start = datetime(year, 1, 1, tzinfo=timezone.utc)
        dt_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        
        properties = {
            'year': year,
            'tile_id': tile_id,
            'source_uri': cog_uri
        }

        request = {
            'type': 'IMAGE',
            'gcs_location': {'uris': [cog_uri]},
            'properties': properties,
            'startTime': dt_start.isoformat(),
            'endTime': dt_end.isoformat()
        }

        # Construct URL using the project from the asset ID to ensure correct parent
        if asset_id.startswith('projects/'):
            project_part = asset_id.split('/assets/')[0]
            prefix = f"{project_part}/assets/"
            relative_asset_id = asset_id[len(prefix):] if asset_id.startswith(prefix) else asset_id
            url = f'https://earthengine.googleapis.com/v1alpha/{project_part}/assets?assetId={relative_asset_id}'
        else:
            url = f'https://earthengine.googleapis.com/v1alpha/projects/{EE_PROJECT}/assets?assetId={asset_id}'
        
        print(f"Registering {asset_name}...")
        response = session.post(url=url, data=json.dumps(request))
        
        if response.status_code != 200:
            if response.status_code == 409:
                 print(f"  -> Asset already exists.")
            else:
                print(f"  -> Error {response.status_code}: {response.text}")

def main():
    create_collection_if_not_exists(EE_COLLECTION)
    
    df = get_tif_list(GCS_PROJECT, GCS_BUCKET, GCS_PREFIX)
    print(f"Found {len(df)} files.")
    
    if len(df) > 0:
        gcs_cogs_to_collection(df, EE_COLLECTION)
    else:
        print("No files found. Please check bucket and prefix.")

if __name__ == "__main__":
    main()