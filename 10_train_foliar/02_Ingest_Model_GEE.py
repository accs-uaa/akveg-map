# Define model targets
group = 'halgra'
version_date = '20260212'

# Import packages
import ee
import os

#### SET UP ENVIRONMENT
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
input_folder = os.path.join(drive, root_folder,
                             f'Data_Output/model_results/version_{version_date}/{group}')

# Define input files
classifier_treestring_input = os.path.join(input_folder, f'{group}_classifier_treestring_lgbm.txt')

# Define paths
ee_project = 'akveg-map'

# Authenticate with Earth Engine
print('Requesting information from server...')
ee.Authenticate()
ee.Initialize(project=ee_project)

# Define paths for the model asset
asset_id = f'projects/{ee_project}/assets/models/foliar_cover/{group}_classifier_model'

# Check if asset exists and delete if so
try:
    ee.data.getAsset(asset_id)
    print(f'Asset {asset_id} already exists. Deleting...')
    ee.data.deleteAsset(asset_id)
except ee.EEException:
    pass

#### INGEST DATA TO GEE ASSET
####____________________________________________________

# Read and parse the tree string file
print(f'Reading tree strings for classifier...')
with open(classifier_treestring_input, 'r') as f:
    content = f.read()

# Split the content into individual trees to create a list of strings
tree_strings = ["1) root " + t.strip() for t in content.split("1) root ") if t.strip()]
print(f'Found {len(tree_strings)} trees in the ensemble.')

# Instantiate the classifier in Earth Engine memory
classifier = ee.Classifier.decisionTreeEnsemble(tree_strings)

# Export the classifier to Earth Engine as a Model Asset
task_name = f'ingest_{group}_classifier_{version_date}'
export_task = ee.batch.Export.classifier.toAsset(
    classifier=classifier,
    description=task_name,
    assetId=asset_id
)

# Submit the export task
print(f'Starting model asset export. Task description: {task_name}')
export_task.start()
