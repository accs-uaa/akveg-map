# Local Server env with Scikit-Learn

*Author*: Matt Macander, ABR

*Last Updated*: 2025-09-30

*Description*: Recipe to create conda env on local server, configured to run statistical learning scripts in the scikit-learn framework. Adapted from 01_Cloud_SpatialModeling.md

## 1. Configure project
ak-veg project and storage bucket already created

ubuntu with miniconda set up already
screen -r

```bash
conda create -n akveg -c conda-forge
conda activate akveg
```

Install the necessary packages for geospatial processing and predictive modeling. In the example below, we install packages to support interactions with Earth Engine and statistical learning with LightGBM and Bayesian Optimization. We also install the "akutils" helper functions.

```bash
conda install -c conda-forge numpy openpyxl pandas gdal geopandas rasterio scikit-learn imbalanced-learn lightgbm bayesian-optimization joblib earthengine-api geemap pyarrow fastparquet
python3 -m pip install git+https://github.com/accs-uaa/akutils
```

### Download files to the virtual machine:

Create the data directories referenced in the script. The example below includes directories to validate and train models.

```bash
akveg_home=/data/gis/raster_base/Alaska/AKVegMap/akveg-working

mkdir -p $akveg_home/scripts
mkdir -p $akveg_home/Data_Input
mkdir -p $akveg_home/Data_Input/extract_data
mkdir -p $akveg_home/Data_Input/species_data
mkdir -p $akveg_home/Data_Output
mkdir -p $akveg_home/Data_Output/model_results
mkdir -p $akveg_home/Data_Output/model_results/20250930
```

Use Google Cloud SDK commands from the terminal to download data and scripts for the storage bucket to the vm.

```
gcloud storage rsync gs://akveg-data/extract_data $akveg_home/Data_Input/extract_data --recursive
gcloud storage rsync gs://akveg-data/species_data $akveg_home/Data_Input/species_data --recursive
gcloud storage rsync gs://akveg-data/scripts $akveg_home/scripts --recursive
```

Use vim to update the scripts as necessary. To begin editing a file once it has been opened in vim, press "i". To save and close a file after editing it in vim, press ":wq".

```bash
vim ~/scripts/01d_Validate_LGBM_Abundance.py
vim ~/scripts/02d_Train_LGBM_Abundance.py
i
:wq
```


## 3. Run scripts
To run a script, first make sure the target vm is running and then open terminal in a browser using ssh. Run the script using the python command. Adding "nohup" to the command will prevent ssh interruptions from stopping the script. The script will run as long as the vm is running and store printed statements in a nohup file (otherwise terminal interruptions will stop the script). When running scripts using "nohup", print statements will not appear in the terminal.

```bash
nohup python3 ~/scripts/01d_Validate_LGBM_Abundance.py
```

