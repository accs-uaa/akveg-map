# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Ingest tree model to GEE
# Author: Timm Nawrocki, Matt Macander
# Last Updated: 2026-02-26
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Ingest tree model to GEE" parses the tree strings from a text file (exported during the model training process) and initiates a task in GEE to upload the tree strings as a table asset.
# ---------------------------------------------------------------------------

# Define model targets
group = 'halgra'
version_date = '20260212'

# Import packages
import ee
import os
import time

#### SET UP ENVIRONMENT
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
input_folder = os.path.join(drive, root_folder,
                             f'Data_Output/model_results/version_{version_date}/{group}')

# Define input files
classifier_input = os.path.join(input_folder, f'{group}_classifier_treestring.txt')

# Define paths
ee_project = 'akveg-map'

# Authenticate with Earth Engine
print('Requesting information from server...')
ee.Authenticate()
ee.Initialize(project=ee_project)

# Define paths for the model asset
asset_id = f'projects/{ee_project}/assets/models/foliar_cover/{group}_classifier'

# Check if asset exists and delete if so
try:
    ee.data.getAsset(asset_id)
    print(f'Asset {asset_id} already exists. Deleting...')
    ee.data.deleteAsset(asset_id)
except ee.EEException:
    pass

#### INGEST DATA TO GEE ASSET
####____________________________________________________

def parse_lgbm_txt(file_path):
    """Parses the LGBM treestring text file into individual tree strings."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Split by the root node indicator to get individual trees
    import re
    raw_trees = re.split(r'(?=1\) root)', content)

    # Filter out empty strings and clean up whitespace
    trees = [t.strip() for t in raw_trees if t.strip()]
    return trees

# Load treestrings from text file
tree_strings = parse_lgbm_txt(classifier_input)

# Create empty features and dummy geometry
gee_features = []
dummy_geom = ee.Geometry.Point([0, 0])

# Parse the tree strings
for i, tree_str in enumerate(tree_strings):
    # Split the tree string into lines and join with # for GEE ingestion
    tree_lines = tree_str.splitlines()
    formatted_tree = "#".join(tree_lines)
    # Appends the tree strings with dummy geometry to a table
    gee_features.append(ee.Feature(dummy_geom, {
        'tree': formatted_tree,
        'tree_index': i
    }))

# Export to a table asset
collection = ee.FeatureCollection(gee_features)
task = ee.batch.Export.table.toAsset(
    collection=collection,
    description='Export_LGBM_from_Txt',
    assetId=asset_id
)
task.start()
print(f"Export task started for asset: {asset_id}")

# Monitor the task
while task.active():
    status = task.status()
    print(f"Task status: {status['state']}...")
    time.sleep(15)
final_status = task.status()
if final_status['state'] == 'COMPLETED':
    print("Export completed successfully! Model is now saved as a Table asset.")
else:
    print(f"\nTask ended with state: {final_status['state']}")
    print(f"Error Message: {final_status.get('error_message', 'No error message provided.')}")
