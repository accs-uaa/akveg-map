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

# Load Sentinel-2 geometric median
sent2_collection = ee.ImageCollection(f'{asset_path}/s2_sr_2019_2023_gMedian_v20240713d')
sent2_image = sent2_collection.median(
    ).select(['s2_seas1spring_blue', 's2_seas1spring_green', 's2_seas1spring_red',
                 's2_seas1spring_rededge1', 's2_seas1spring_rededge2', 's2_seas1spring_rededge3',
                 's2_seas1spring_nir', 's2_seas1spring_rededge4',
                 's2_seas1spring_swir1', 's2_seas1spring_swir2',
                 's2_seas2earlySummer_blue', 's2_seas2earlySummer_green', 's2_seas2earlySummer_red',
                 's2_seas2earlySummer_rededge1', 's2_seas2earlySummer_rededge2', 's2_seas2earlySummer_rededge3',
                 's2_seas2earlySummer_nir', 's2_seas2earlySummer_rededge4',
                 's2_seas2earlySummer_swir1', 's2_seas2earlySummer_swir2',
                 's2_seas3midSummer_blue', 's2_seas3midSummer_green', 's2_seas3midSummer_red',
                 's2_seas3midSummer_rededge1', 's2_seas3midSummer_rededge2', 's2_seas3midSummer_rededge3',
                 's2_seas3midSummer_nir', 's2_seas3midSummer_rededge4',
                 's2_seas3midSummer_swir1', 's2_seas3midSummer_swir2',
                 's2_seas4lateSummer_blue', 's2_seas4lateSummer_green', 's2_seas4lateSummer_red',
                 's2_seas4lateSummer_rededge1', 's2_seas4lateSummer_rededge2', 's2_seas4lateSummer_rededge3',
                 's2_seas4lateSummer_nir', 's2_seas4lateSummer_rededge4',
                 's2_seas4lateSummer_swir1', 's2_seas4lateSummer_swir2',
                 's2_seas5fall_blue', 's2_seas5fall_green', 's2_seas5fall_red',
                 's2_seas5fall_rededge1', 's2_seas5fall_rededge2', 's2_seas5fall_rededge3',
                 's2_seas5fall_nir', 's2_seas5fall_rededge4',
                 's2_seas5fall_swir1', 's2_seas5fall_swir2'
              ]).rename(['s2_1_blue', 's2_1_green', 's2_1_red', 's2_1_redge1', 's2_1_redge2',
                         's2_1_redge3', 's2_1_nir', 's2_1_redge4', 's2_1_swir1', 's2_1_swir2',
                         's2_2_blue', 's2_2_green', 's2_2_red', 's2_2_redge1', 's2_2_redge2',
                         's2_2_redge3', 's2_2_nir', 's2_2_redge4', 's2_2_swir1', 's2_2_swir2',
                         's2_3_blue', 's2_3_green', 's2_3_red', 's2_3_redge1', 's2_3_redge2',
                         's2_3_redge3', 's2_3_nir', 's2_3_redge4', 's2_3_swir1', 's2_3_swir2',
                         's2_4_blue', 's2_4_green', 's2_4_red', 's2_4_redge1', 's2_4_redge2',
                         's2_4_redge3', 's2_4_nir', 's2_4_redge4', 's2_4_swir1', 's2_4_swir2',
                         's2_5_blue', 's2_5_green', 's2_5_red', 's2_5_redge1', 's2_5_redge2',
                         's2_5_redge3', 's2_5_nir', 's2_5_redge4', 's2_5_swir1', 's2_5_swir2'
                         ])

# Load Sentinel-1
sent1_collection = ee.ImageCollection(f'{asset_path}/s1_2022_v20230326')
sent1_image = sent1_collection.median(
    ).select(['VH_p50_fall_asc', 'VH_p50_fall_desc', 'VH_p50_froz_asc', 'VH_p50_froz_desc',
              'VH_p50_grow_asc', 'VH_p50_grow_desc', 'VV_p50_fall_asc', 'VV_p50_fall_desc',
              'VV_p50_froz_asc', 'VV_p50_froz_desc', 'VV_p50_grow_asc', 'VV_p50_grow_desc'
              ]).rename(['s1_2_vha', 's1_2_vhd', 's1_3_vha', 's1_3_vhd',
                         's1_1_vha', 's1_1_vhd', 's1_2_vva', 's1_2_vvd',
                         's1_3_vva', 's1_3_vvd', 's1_1_vva', 's1_1_vvd'])

# Load covariates
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
buffer_feature = ee.FeatureCollection(f'{asset_path}/sites/AKVEG_Sites_Buffered_3338')
area_feature = ee.FeatureCollection(f'{asset_path}/regions/AlaskaYukon_MapDomain_3338_v20230330')

# Create image collection
covariate_image = sent2_image.addBands(
    srcImg=[sent1_image, summer_image, january_image, precip_image,
            coast_image, stream_image, river_image, wetness_image,
            elevation_image, exposure_image, heatload_image, position_image,
            aspect_image, relief_image, roughness_image, slope_image],
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
  description='akveg-covariates',
  bucket=storage_bucket,
  fileNamePrefix=f'{storage_prefix}/AKVEG_Sites_Covariates_3338',
  fileFormat='CSV',
  maxVertices=100000
)
task.start()
print('GEE task sent to server.')
print('----------')
