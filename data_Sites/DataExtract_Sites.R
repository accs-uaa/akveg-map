# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Features to Sites
# Author: Timm Nawrocki
# Last Updated: 2020-11-30
# Usage: Must be executed in R 4.0.0+.
# Description: "Extract Features to Sites" extracts data from rasters to points representing plot locations and collapses multi-point plots into single points with plot-level means.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
site_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input/sites',
                    sep = '/')
parsed_folder = paste(site_folder,
                      'parsed',
                      sep = '/')
topography_folder = paste(drive,
                          root_folder,
                          'Data/topography/Composite_10m_Beringia/gridded_select',
                          sep = '/')
sentinel1_folder = paste(drive,
                         root_folder,
                         'Data/imagery/sentinel-1/gridded_select',
                         sep = '/')
sentinel2_folder = paste(drive,
                         root_folder,
                         'Data/imagery/sentinel-2/gridded_select',
                         sep = '/')
modis_folder = paste(drive,
                     root_folder,
                     'Data/imagery/modis/gridded_select',
                     sep = '/')
climate_folder = paste(drive,
                       root_folder,
                       'Data/climatology/SNAP_NorthwestNorthAmerica_10m/gridded_select',
                       sep = '/')
fire_folder = paste(drive,
                    root_folder,
                    'Data/climatology/Fire/gridded_select',
                    sep = '/')

# Define input site metadata
site_file = paste(site_folder,
                  'sites_all.csv',
                  sep = '/')

# Install required libraries if they are not already installed.
Required_Packages <- c('dplyr', 'raster', 'rgdal', 'sp', 'stringr', 'tidyr')
New_Packages <- Required_Packages[!(Required_Packages %in% installed.packages()[,"Package"])]
if (length(New_Packages) > 0) {
  install.packages(New_Packages)
}
# Import required libraries for geospatial processing: dplyr, raster, rgdal, sp, and stringr.
library(dplyr)
library(raster)
library(rgdal)
library(sp)
library(stringr)

# Read site metadata into dataframe
site_metadata = read.csv(site_file, fileEncoding = 'UTF-8')

# Generate a list of parsed site points
grid_list = list.files(parsed_folder, pattern='shp$', full.names=FALSE)
grid_length = length(grid_list)
print(grid_list)

# Create an empty list to store data frames
data_list = list()

# Loop through all grids with site data and extract features to sites
count = 1
for (grid in grid_list) {
  print(grid)
  print(paste('Extracting predictor data to site points ', count, ' of ', grid_length, '...', sep=''))
  count = count + 1
  
  # Create full path to points shapefile
  grid_sites = paste(parsed_folder, grid, sep = '/')
  
  # Identify grid name and predictor folders
  grid_name = str_remove(grid, '.shp')
  grid_folder = paste('Grid_', grid_name, sep = '')
  topography_grid = paste(topography_folder, grid_folder, sep = '/')
  sentinel1_grid = paste(sentinel1_folder, grid_folder, sep = '/')
  sentinel2_grid = paste(sentinel2_folder, grid_folder, sep = '/')
  modis_grid = paste(modis_folder, grid_folder, sep = '/')
  climate_grid = paste(climate_folder, grid_folder, sep = '/')
  fire_grid = paste(fire_folder, grid_folder, sep = '/')
  
  # Create a list of all predictor rasters
  predictors_topography = list.files(topography_grid, pattern = 'tif$', full.names = TRUE)
  predictors_sentinel1 = list.files(sentinel1_grid, pattern = 'tif$', full.names = TRUE)
  predictors_sentinel2 = list.files(sentinel2_grid, pattern = 'tif$', full.names = TRUE)
  predictors_modis = list.files(modis_grid, pattern = 'tif$', full.names = TRUE)
  predictors_climate = list.files(climate_grid, pattern = 'tif$', full.names = TRUE)
  predictors_fire = list.files(fire_grid, pattern = 'tif$', full.names = TRUE)
  predictors_all = c(predictors_topography,
                     predictors_sentinel1,
                     predictors_sentinel2,
                     predictors_modis,
                     predictors_climate,
                     predictors_fire)
  print("Number of predictor rasters:")
  print(length(predictors_all))
  
  # Generate a stack of all predictor rasters
  predictor_stack = stack(predictors_all)
  
  # Read site data and extract features
  site_data = readOGR(dsn = grid_sites)
  sites_extracted = data.frame(site_data@data, extract(predictor_stack, site_data))
  
  # Find plot level mean values and convert field names to standard
  sites_extracted = sites_extracted %>%
    rename(aspect = paste('Aspect_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(wetness = paste('CompoundTopographic_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(elevation = paste('Elevation_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(slope = paste('MeanSlope_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(roughness = paste('Roughness_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(exposure = paste('SiteExposure_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(area = paste('SurfaceArea_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(relief = paste('SurfaceRelief_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(position = paste('TopographicPosition_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(radiation = paste('TopographicRadiation_Composite_10m_Beringia_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(vh = paste('Sent1_vh_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(vv = paste('Sent1_vv_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR1_05 = paste('Sent2_05May_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR2_05 = paste('Sent2_05May_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(blue_05 = paste('Sent2_05May_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(green_05 = paste('Sent2_05May_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(red_05 = paste('Sent2_05May_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge1_05 = paste('Sent2_05May_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge2_05 = paste('Sent2_05May_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge3_05 = paste('Sent2_05May_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nearIR_05 = paste('Sent2_05May_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge4_05 = paste('Sent2_05May_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(evi2_05 = paste('Sent2_05May_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nbr_05 = paste('Sent2_05May_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndmi_05 = paste('Sent2_05May_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndsi_05 = paste('Sent2_05May_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndvi_05 = paste('Sent2_05May_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndwi_05 = paste('Sent2_05May_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR1_06 = paste('Sent2_06June_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR2_06 = paste('Sent2_06June_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(blue_06 = paste('Sent2_06June_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(green_06 = paste('Sent2_06June_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(red_06 = paste('Sent2_06June_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge1_06 = paste('Sent2_06June_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge2_06 = paste('Sent2_06June_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge3_06 = paste('Sent2_06June_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nearIR_06 = paste('Sent2_06June_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge4_06 = paste('Sent2_06June_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(evi2_06 = paste('Sent2_06June_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nbr_06 = paste('Sent2_06June_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndmi_06 = paste('Sent2_06June_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndsi_06 = paste('Sent2_06June_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndvi_06 = paste('Sent2_06June_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndwi_06 = paste('Sent2_06June_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR1_07 = paste('Sent2_07July_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR2_07 = paste('Sent2_07July_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(blue_07 = paste('Sent2_07July_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(green_07 = paste('Sent2_07July_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(red_07 = paste('Sent2_07July_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge1_07 = paste('Sent2_07July_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge2_07 = paste('Sent2_07July_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge3_07 = paste('Sent2_07July_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nearIR_07 = paste('Sent2_07July_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge4_07 = paste('Sent2_07July_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(evi2_07 = paste('Sent2_07July_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nbr_07 = paste('Sent2_07July_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndmi_07 = paste('Sent2_07July_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndsi_07 = paste('Sent2_07July_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndvi_07 = paste('Sent2_07July_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndwi_07 = paste('Sent2_07July_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR1_08 = paste('Sent2_08August_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR2_08 = paste('Sent2_08August_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(blue_08 = paste('Sent2_08August_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(green_08 = paste('Sent2_08August_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(red_08 = paste('Sent2_08August_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge1_08 = paste('Sent2_08August_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge2_08 = paste('Sent2_08August_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge3_08 = paste('Sent2_08August_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nearIR_08 = paste('Sent2_08August_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge4_08 = paste('Sent2_08August_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(evi2_08 = paste('Sent2_08August_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nbr_08 = paste('Sent2_08August_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndmi_08 = paste('Sent2_08August_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndsi_08 = paste('Sent2_08August_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndvi_08 = paste('Sent2_08August_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndwi_08 = paste('Sent2_08August_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR1_09 = paste('Sent2_09September_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(shortIR2_09 = paste('Sent2_09September_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(blue_09 = paste('Sent2_09September_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(green_09 = paste('Sent2_09September_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(red_09 = paste('Sent2_09September_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge1_09 = paste('Sent2_09September_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge2_09 = paste('Sent2_09September_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge3_09 = paste('Sent2_09September_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nearIR_09 = paste('Sent2_09September_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(redge4_09 = paste('Sent2_09September_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(evi2_09 = paste('Sent2_09September_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(nbr_09 = paste('Sent2_09September_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndmi_09 = paste('Sent2_09September_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndsi_09 = paste('Sent2_09September_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndvi_09 = paste('Sent2_09September_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(ndwi_09 = paste('Sent2_09September_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(lstWarmth = paste('MODIS_LST_WarmthIndex_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(summerWarmth = paste('SummerWarmth_MeanAnnual_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(precip = paste('Precipitation_MeanAnnual_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(fireYear = paste('FireHistory_AKALB_Grid_', grid_name, sep = ''))

  # Summarize data by site and taxon
  sites_mean = sites_extracted %>%
    group_by(siteCode) %>%
    summarize(aspect = round(mean(aspect), digits = 0),
              wetness = round(mean(wetness), digits = 0),
              elevation = round(mean(elevation), digits = 0),
              slope = round(mean(slope), digits = 0),
              roughness = round(mean(roughness), digits = 0),
              exposure = round(mean(exposure), digits = 0),
              area = round(mean(area), digits = 0),
              relief = round(mean(relief), digits = 0),
              position = round(mean(position), digits = 0),
              radiation = round(mean(radiation), digits = 0),
              vh = round(mean(vh), digits = 0),
              vv = round(mean(vv), digits = 0),
              shortIR1_05 = round(mean(shortIR1_05), digits = 0),
              shortIR2_05 = round(mean(shortIR2_05), digits = 0),
              blue_05 = round(mean(blue_05), digits = 0),
              green_05 = round(mean(green_05), digits = 0),
              red_05 = round(mean(red_05), digits = 0),
              redge1_05 = round(mean(redge1_05), digits = 0),
              redge2_05 = round(mean(redge2_05), digits = 0),
              redge3_05 = round(mean(redge3_05), digits = 0),
              nearIR_05 = round(mean(nearIR_05), digits = 0),
              redge4_05 = round(mean(redge4_05), digits = 0),
              evi2_05 = round(mean(evi2_05), digits = 0),
              nbr_05 = round(mean(nbr_05), digits = 0),
              ndmi_05 = round(mean(ndmi_05), digits = 0),
              ndsi_05 = round(mean(ndsi_05), digits = 0),
              ndvi_05 = round(mean(ndvi_05), digits = 0),
              ndwi_05 = round(mean(ndwi_05), digits = 0),
              shortIR1_06 = round(mean(shortIR1_06), digits = 0),
              shortIR2_06 = round(mean(shortIR2_06), digits = 0),
              blue_06 = round(mean(blue_06), digits = 0),
              green_06 = round(mean(green_06), digits = 0),
              red_06 = round(mean(red_06), digits = 0),
              redge1_06 = round(mean(redge1_06), digits = 0),
              redge2_06 = round(mean(redge2_06), digits = 0),
              redge3_06 = round(mean(redge3_06), digits = 0),
              nearIR_06 = round(mean(nearIR_06), digits = 0),
              redge4_06 = round(mean(redge4_06), digits = 0),
              evi2_06 = round(mean(evi2_06), digits = 0),
              nbr_06 = round(mean(nbr_06), digits = 0),
              ndmi_06 = round(mean(ndmi_06), digits = 0),
              ndsi_06 = round(mean(ndsi_06), digits = 0),
              ndvi_06 = round(mean(ndvi_06), digits = 0),
              ndwi_06 = round(mean(ndwi_06), digits = 0),
              shortIR1_07 = round(mean(shortIR1_07), digits = 0),
              shortIR2_07 = round(mean(shortIR2_07), digits = 0),
              blue_07 = round(mean(blue_07), digits = 0),
              green_07 = round(mean(green_07), digits = 0),
              red_07 = round(mean(red_07), digits = 0),
              redge1_07 = round(mean(redge1_07), digits = 0),
              redge2_07 = round(mean(redge2_07), digits = 0),
              redge3_07 = round(mean(redge3_07), digits = 0),
              nearIR_07 = round(mean(nearIR_07), digits = 0),
              redge4_07 = round(mean(redge4_07), digits = 0),
              evi2_07 = round(mean(evi2_07), digits = 0),
              nbr_07 = round(mean(nbr_07), digits = 0),
              ndmi_07 = round(mean(ndmi_07), digits = 0),
              ndsi_07 = round(mean(ndsi_07), digits = 0),
              ndvi_07 = round(mean(ndvi_07), digits = 0),
              ndwi_07 = round(mean(ndwi_07), digits = 0),
              shortIR1_08 = round(mean(shortIR1_08), digits = 0),
              shortIR2_08 = round(mean(shortIR2_08), digits = 0),
              blue_08 = round(mean(blue_08), digits = 0),
              green_08 = round(mean(green_08), digits = 0),
              red_08 = round(mean(red_08), digits = 0),
              redge1_08 = round(mean(redge1_08), digits = 0),
              redge2_08 = round(mean(redge2_08), digits = 0),
              redge3_08 = round(mean(redge3_08), digits = 0),
              nearIR_08 = round(mean(nearIR_08), digits = 0),
              redge4_08 = round(mean(redge4_08), digits = 0),
              evi2_08 = round(mean(evi2_08), digits = 0),
              nbr_08 = round(mean(nbr_08), digits = 0),
              ndmi_08 = round(mean(ndmi_08), digits = 0),
              ndsi_08 = round(mean(ndsi_08), digits = 0),
              ndvi_08 = round(mean(ndvi_08), digits = 0),
              ndwi_08 = round(mean(ndwi_08), digits = 0),
              shortIR1_09 = round(mean(shortIR1_09), digits = 0),
              shortIR2_09 = round(mean(shortIR2_09), digits = 0),
              blue_09 = round(mean(blue_09), digits = 0),
              green_09 = round(mean(green_09), digits = 0),
              red_09 = round(mean(red_09), digits = 0),
              redge1_09 = round(mean(redge1_09), digits = 0),
              redge2_09 = round(mean(redge2_09), digits = 0),
              redge3_09 = round(mean(redge3_09), digits = 0),
              nearIR_09 = round(mean(nearIR_09), digits = 0),
              redge4_09 = round(mean(redge4_09), digits = 0),
              evi2_09 = round(mean(evi2_09), digits = 0),
              nbr_09 = round(mean(nbr_09), digits = 0),
              ndmi_09 = round(mean(ndmi_09), digits = 0),
              ndsi_09 = round(mean(ndsi_09), digits = 0),
              ndvi_09 = round(mean(ndvi_09), digits = 0),
              ndwi_09 = round(mean(ndwi_09), digits = 0),
              lstWarmth = round(mean(lstWarmth), digits = 0),
              precip = round(mean(precip), digits = 0),
              summerWarmth = round(mean(summerWarmth), digits = 0),
              fireYear = round(max(fireYear), digits = 0),
              num_points = n())
  
  # Add sites mean to list of data frames
  data_list = c(data_list, list(sites_mean))
}

# Import required library for data manipulation: tidyr. NOTE: Tidyr conflicts with raster and therefore must be loaded after all raster extractions are complete.
library(tidyr)

# Merge data list into single data frame
sites_extracted = bind_rows(data_list)

# Join site metadata to extracted data and remove na values
sites_joined = site_metadata %>%
  inner_join(sites_extracted, by = 'siteCode') %>%
  drop_na()

# Export data as a csv
output_csv = paste(site_folder, 'sites_extracted.csv', sep = '/')
write.csv(sites_joined, file = output_csv, fileEncoding = 'UTF-8')
print('Finished extracting data to sites.')
