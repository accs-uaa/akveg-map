# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Delete assets on GEE
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Delete assets on GEE" deletes a set of assets within a folder or image collection on Google Earth Engine (GEE).
# ---------------------------------------------------------------------------

# Import packages
import ee
from google.auth.transport.requests import AuthorizedSession

#### SET UP GEE ENVIRONMENT
####____________________________________________________

# Specify cloud project
ee_project = 'akveg-map'

# Authenticate with Earth Engine
print('Requesting information from server...')
ee.Authenticate()
ee.Initialize(project=ee_project)

# Specify the cloud project you want associated with Earth Engine requests.
session = AuthorizedSession(
  ee.data.get_persistent_credentials().with_quota_project(ee_project)
)

# Get list of assets
asset_list_path = {'id': 'projects/akveg-map/assets/s2_sr_2019_2023_median_midsummer_v20240724'}
asset_list = ee.data.getList(asset_list_path)

# Print asset list
print("Asset list:")
for asset in asset_list:
    print(asset['id'])

#### CONDUCT DELETE OPERATIONS ON GEE
####____________________________________________________

# Delete assets
for asset in asset_list:
    asset_path = asset['id']
    try:
        ee.data.deleteAsset(asset_path)
        print("Asset deleted:", asset_path)
    except Exception as e:
        print("Failed to delete asset:", asset_path)
        print("Error:", e)
