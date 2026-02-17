# imports
import ee
import re
import os
import json
import subprocess
import pandas as pd
from google.cloud import storage
from google.auth.transport.requests import AuthorizedSession

#########################################################################
# VARIABLES TO BE MODIFIED BY THE USER
#########################################################################
# determines whether the MGRS portion of the script is run
RUN_MGRS_MONTHLY = False
# determines if a new image MGRS image collection is created in GEE
CREATE_EMPTY_IC_MGRS = False
# determines whether the AKALB portion of the script is run
RUN_AKALB_PERCENTAGES = True
# determines if a new image AKALB image collection is created in GEE
CREATE_EMPTY_IC_AKALB = False

#########################################################################
# SETUP + FUNCTIONS
#########################################################################
# set project paths
ee_project = 'akveg-map'
ee_bucket = 'akveg-data'

# connect to the Google project
ee.Authenticate(auth_mode='notebook') 
ee.Initialize(project=ee_project)
session = AuthorizedSession(ee.data.get_persistent_credentials().with_quota_project(ee_project))

# function for running bash commands
def run_bash(command):
    subprocess.run(command, shell=True)

# function for getting list of tif files at a certain GCS location
def get_tif_list(project_name, bucket_name, path):
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=path)
    tif_list = [f"gs://{bucket_name}/{blob.name}" for blob in blobs if blob.name.endswith('.tif')]
    tif_list = pd.DataFrame(tif_list).rename(columns={0: 'tif'})
    return tif_list

def gcs_cogs_to_collection(cogs_df, collection_path, field_indices):
    """
    Refactored loader that dynamically builds properties.
    field_indices: dict mapping metadata key to its index in the split filename.
    Example: {'month': 4, 'tile': 5}
    """
    print(f"Starting upload to {collection_path}...")
    
    for cog in cogs_df['tif']:
        filename = os.path.split(cog)[1]
        cog_name = filename[:-4] # Remove .tif
        parts = re.split(r'[_.]', filename)
        
        # Build properties dict based on the provided mapping
        properties = {}
        for key, idx in field_indices.items():
            val = parts[idx]
            # Maintain the original "month" formatting logic (last 2 chars)
            if 'month' in key.lower():
                val = val[-2:]
            properties[key] = val

        request = {
            'type': 'IMAGE',
            'gcs_location': {'uris': [cog]},
            'properties': properties
        }

        # assetId in URL should be relative to the project structure
        url = f'https://earthengine.googleapis.com/v1alpha/projects/{ee_project}/assets?assetId={collection_path}/{cog_name}'
        
        response = session.post(url=url, data=json.dumps(request))
        
        if response.status_code == 200:
            print(f"Successfully started upload for: {cog_name}")
        else:
            print(f"Error for {cog_name}: {response.text}")

    print("Done.")

#########################################################################
# ENGINE
#########################################################################
# process monthly counts by MGRS tile
if RUN_MGRS_MONTHLY:
    if CREATE_EMPTY_IC_MGRS:
        # create a new image collection
        run_bash('earthengine set_project akveg-map')
        run_bash('COLLECTION="projects/akveg-map/assets/dynamic_world_metrics/s2_dw_monthly_counts_mgrs_v20250414b"')
        run_bash('earthengine create collection $COLLECTION')
    else:
        # clear existing image collection
        run_bash('COLLECTION="projects/akveg-map/assets/dynamic_world_metrics/s2_dw_monthly_counts_mgrs_v20250414b"')
        run_bash('earthengine ls $COLLECTION | xargs -P 20 -I {} earthengine rm {}')
    # get a list of MGRS monthly tif files in GCS
    gcs_mgrs_folder = 's2_dw_v1_metrics/s2_dw_monthly_counts_mgrs_v20250414b/'
    df_mgrs = get_tif_list(ee_project, ee_bucket, gcs_mgrs_folder)
    print(df_mgrs)
    gee_ic_mgrs = 'dynamic_world_metrics/s2_dw_monthly_counts_mgrs_v20250414b'
    gcs_cogs_to_collection(df_mgrs, gee_ic_mgrs, {'month': 4, 'tile': 5})

# process dynamic world percentages by AKALB tile
if RUN_AKALB_PERCENTAGES:
    if CREATE_EMPTY_IC_AKALB:
        # create a new image collection
        run_bash('earthengine set_project akveg-map')
        run_bash('COLLECTION="projects/akveg-map/assets/dynamic_world_metrics/s2_dw_percentages_56789_v20250414"')
        run_bash('earthengine create collection $COLLECTION')
    else:
        # clear existing image collection
        run_bash('COLLECTION="projects/akveg-map/assets/dynamic_world_metrics/s2_dw_percentages_56789_v20250414"')
        run_bash('earthengine ls $COLLECTION | xargs -P 20 -I {} earthengine rm {}')
    # get a list of AKALB percentage tif files in GCS
    gcs_akalb_folder = 's2_dw_v1_metrics/s2_dw_pct_akalb_050_v20250414/'
    df_akalb = get_tif_list(ee_project, ee_bucket, gcs_akalb_folder)
    print(df_akalb)
    gee_ic_akalb = 'dynamic_world_metrics/s2_dw_percentages_56789_v20250414'
    gcs_cogs_to_collection(df_akalb, gee_ic_akalb, {'months': 3, 'tile': 4, 'version_counts': 5})