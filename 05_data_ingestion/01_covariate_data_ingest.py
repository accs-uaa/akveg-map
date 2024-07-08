# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Ingest covariate data
# Author: Timm Nawrocki
# Last Updated: 2024-07-08
# Usage: Must be executed in an ArcGIS Pro Python 3.9+ installation.
# Description: "Ingest covariate data" converts raster data in a Google Cloud storage bucket into images as a Google Earth Engine assets.
# ---------------------------------------------------------------------------
import os.path

# Import packages
import ee

# Authenticate with Earth Engine
ee.Authenticate()
ee.Initialize(project='akveg-map')

# Define directories
asset_folder = 'projects/akveg-map/assets/covariates/'
gcloud_folder = 'gs://akveg-data/covariates/'

# Define covariate list
covariate_list = ['CoastDist_10m_3338.tif', 'Elevation_10m_3338.tif', 'Exposure_10m_3338.tif',
                  'HeatLoad_10m_3338.tif', 'January_MinimumTemperature_2006_2015_10m_3338.tif',
                  'Position_10m_3338.tif', 'Precipitation_MeanAnnual_2006_2015_10m_3338.tif',
                  'RadiationAspect_10m_3338.tif', 'Relief_10m_3338.tif', 'RiverDist_10m_3338.tif',
                  'Roughness_10m_3338.tif', 'Slope_10m_3338.tif', 'StreamDist_10m_3338.tif',
                  'SummerWarmth_MeanAnnual_2006_2015_10m_3338.tif', 'Wetness_10m_3338.tif']

# Define a list of covariates to skip
skip_list = []

# Create an ingestion task for each covariate
count = 1
for covariate in covariate_list:
    if covariate in skip_list:
        print(f'Skipping ingestion for covariate {count} of {len(covariate_list)}.')
    else:
        print(f'Starting ingestion for covariate {count} of {len(covariate_list)}.')
        # Define asset path
        asset_path = asset_folder + os.path.splitext(covariate)[0]

        # Define gcloud path
        gcloud_path = gcloud_folder + covariate

        # Create new request
        request_id = ee.data.newTaskId()[0]

        # Define request parameters
        params = {
            'name': asset_path,
            'tilesets': [{'sources': [{'uris': [gcloud_path]}]}]
        }

        # Trigger dataset ingestion
        ee.data.startIngestion(request_id=request_id, params=params)

    # Increase count
    count += 1
