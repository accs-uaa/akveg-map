# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Ingest climate covariate data
# Author: Timm Nawrocki
# Last Updated: 2026-01-20
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Ingest climate covariate data" creates COG-backed assets for a folder of geotiffs in GEE.
# ---------------------------------------------------------------------------

# Import packages
import ee
import os
import re
from google.cloud import storage

#### SET UP GEE ENVIRONMENT
####____________________________________________________

# Define paths
ee_project = 'akveg-map'
storage_bucket = 'akveg-data'
storage_prefix = 'covariates_v20260118'

# Authenticate with Earth Engine
print('Requesting information from server...')
ee.Authenticate()
ee.Initialize(project=ee_project)

# Get list of files from Google Cloud Storage
client = storage.Client(project=ee_project)
blobs = client.list_blobs(storage_bucket, prefix=storage_prefix)

# Filter the list to geotiffs in the storage bucket
reg = re.compile(r'^' + storage_prefix + r'/.*\.tif$')
geotiff_list = [blob.name for blob in blobs if reg.search(blob.name)]
print(f"Found {len(geotiff_list)} geotiffs in GCS.")

# Ensure the parent ImageCollection exists in GEE
parent_asset_id = f'projects/{ee_project}/assets/{storage_prefix}'
try:
    ee.data.getAsset(parent_asset_id)
    print(f"Parent asset found: {parent_asset_id}")
except ee.EEException:
    print(f"Parent asset not found. Creating ImageCollection: {parent_asset_id}")
    ee.data.createAsset(
        {'type': 'IMAGE_COLLECTION'},
        parent_asset_id
    )

# Get list of existing GEE assets to avoid duplicates
existing_assets = []
# We use a try/except here in case the folder was just created and is empty
try:
    assets_response = ee.data.listAssets({'parent': parent_asset_id})
    if 'assets' in assets_response:
        for asset in assets_response['assets']:
            # Extract just the filename part for comparison
            existing_assets.append(os.path.basename(asset['name']) + '.tif')
except ee.EEException as e:
    print(f"Error listing assets (folder might be empty): {e}")

#### INGEST COGS INTO GEE
####____________________________________________________

# Send ingestion request for each geotiff
for geotiff in geotiff_list:
    # Define file name
    file_name = os.path.basename(geotiff)
    # Define the target asset ID
    asset_name = os.path.splitext(file_name)[0]
    full_asset_id = f'{parent_asset_id}/{asset_name}'

    # Ingest asset if it does not already exist
    if file_name not in existing_assets:
        print(f'Ingesting {file_name} as a COG-backed asset...')

        # Request body using the Python Client syntax
        request = {
            'type': 'IMAGE',
            'gcs_location': {
                'uris': [f'gs://{storage_bucket}/{geotiff}']
            },
            'properties': {
                'source': 'https://github.com/accs-uaa/akveg-map',
                'original_filename': file_name
            },
            'startTime': '2026-01-01T00:00:00Z',
            'endTime': '2026-12-31T15:01:23Z',
        }

        try:
            # Use the native library method instead of manual requests
            ee.data.createAsset(request, full_asset_id)
            print(f'Successfully created: {full_asset_id}')
        except ee.EEException as e:
            print(f'Failed to create {file_name}: {e}')

    else:
        print(f'{file_name} already exists. Skipping.')
