# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract data to sites
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2024-07-29
# Usage: Must be executed in a Python 3.12+ installation with authentication to Google Earth Engine.
# Description: "Extract data to sites" reduces covariate image assets to buffered points on Google Earth Engine.
# ---------------------------------------------------------------------------

# Import packages
import ee
from google.auth.transport.requests import AuthorizedSession

# Define paths
ee_project = 'akveg-map'
storage_bucket = 'akveg-data'
storage_prefix = 'extract'

# Authenticate with Earth Engine
print('Requesting information from server...')
ee.Authenticate()
ee.Initialize(project=ee_project)

# Specify the cloud project you want associated with Earth Engine requests.
session = AuthorizedSession(
  ee.data.get_persistent_credentials().with_quota_project(ee_project)
)

#### 1. INITIALIZE

# Define asset path
asset_path = f'projects/{ee_project}/assets'
covariate_path = f'{asset_path}/covariates_v20240711'

# Load image collection
midsummer_collection = ee.ImageCollection(f'{asset_path}/s2_sr_2019_2023_median_midsummer_v20240724')
midsummer_image = midsummer_collection.median()

# Load covariates
validation_image = (
    ee.Image(f'{asset_path}/validation_v20240729/AlaskaYukon_100_Tiles_3338')
        .rename(['valid'])
)
summer_image = (
    ee.Image(f'{covariate_path}/SummerWarmth_MeanAnnual_2006_2015_10m_3338')
        .rename(['summer'])
)
january_image = (
    ee.Image(f'{covariate_path}/January_MinimumTemperature_2006_2015_10m_3338')
        .rename(['january'])
)
precip_image = (
    ee.Image(f'{covariate_path}/Precipitation_MeanAnnual_2006_2015_10m_3338')
        .rename(['precip'])
)
coast_image = (
    ee.Image(f'{covariate_path}/CoastDist_10m_3338')
        .rename(['coast'])
)
stream_image = (
    ee.Image(f'{covariate_path}/StreamDist_10m_3338')
        .rename(['stream'])
)
river_image = (
    ee.Image(f'{covariate_path}/RiverDist_10m_3338')
        .rename(['river'])
)
wetness_image = (
    ee.Image(f'{covariate_path}/Wetness_10m_3338')
        .rename(['wetness'])
)
elevation_image = (
    ee.Image(f'{covariate_path}/Elevation_10m_3338')
        .rename(['elevation'])
)
exposure_image = (
    ee.Image(f'{covariate_path}/Exposure_10m_3338')
        .rename(['exposure'])
)
heatload_image = (
    ee.Image(f'{covariate_path}/HeatLoad_10m_3338')
        .rename(['heatload'])
)
position_image = (
    ee.Image(f'{covariate_path}/Position_10m_3338')
        .rename(['position'])
)
aspect_image = (
    ee.Image(f'{covariate_path}/RadiationAspect_10m_3338')
        .rename(['aspect'])
)
relief_image = (
    ee.Image(f'{covariate_path}/Relief_10m_3338')
        .rename(['relief'])
)
roughness_image = (
    ee.Image(f'{covariate_path}/Roughness_10m_3338')
        .rename(['roughness'])
)
slope_image = (
    ee.Image(f'{covariate_path}/Slope_10m_3338')
        .rename(['slope'])
)
buffer_feature = ee.FeatureCollection(f'{asset_path}/sites/NPSS_Sites_Buffered_3338')
area_feature = ee.FeatureCollection(f'{asset_path}/regions/AlaskaYukon_MapDomain_3338_v20230330')

# Create image collection
covariate_image = midsummer_image.addBands(
    srcImg=[summer_image, january_image, precip_image,
            coast_image, stream_image, river_image, wetness_image,
            elevation_image, exposure_image, heatload_image, position_image,
            aspect_image, relief_image, roughness_image, slope_image,
            validation_image],
    overwrite=False
)

# Add reducer output to the Features in the collection.
print('Creating GEE task...')
buffer_means = covariate_image.reduceRegions(
    collection=buffer_feature,
    reducer=ee.Reducer.mean(),
    scale=10,
    crs='EPSG:3338'
)

# Export results to cloud storage.
task = ee.batch.Export.table.toCloudStorage(
  collection=buffer_means,
  description='npss-covariates',
  bucket=storage_bucket,
  fileNamePrefix=f'{storage_prefix}/NPSS_Sites_Covariates_3338',
  fileFormat='CSV',
  maxVertices=100000
)
task.start()
print('GEE task sent to server.')
print('----------')
