# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Features to Sites
# Author: Timm Nawrocki
# Created on: 2020-05-07
# Usage: Must be executed in R 4.0.0+.
# Description: "Extract Features to Sites" extracts data from rasters to points representing plot locations and collapses multi-point plots into single points with plot-level means.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
parsed_folder = paste(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/sites/parsed', sep = '/')
sentinel2_folder = paste(drive, root_folder, 'Data/imagery/sentinel-2/gridded_select', sep = '/')
modis_folder = paste(drive, root_folder, 'Data/imagery/modis/gridded_select', sep = '/')
topography_folder = paste(drive, root_folder, 'Data/topography/Composite_10m_Beringia/gridded_select', sep = '/')

# Define output folder
output_folder = paste(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/sites/extracted', sep = '/')

# Install required libraries if they are not already installed.
Required_Packages <- c('sp', 'raster', 'rgdal', 'stringr')
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

# Generate a list of all watersheds in the watersheds directory
grid_list = list.files(parsed_folder, pattern='shp$', full.names=FALSE)
grid_length = length(grid_list)
print(grid_list)

# Loop through all grids with site data and extract features to sites
count = 1
for (grid in grid_list) {
  print(grid)
  print(paste('Extracting predictor data to site grid ', count, ' of ', grid_length, '...', sep=''))
  count = count + 1
  
  # Create full path to points shapefile
  grid_sites = paste(parsed_folder, grid, sep = '/')
  
  # Identify grid name and predictor folders
  grid_name = str_remove(grid, '.shp')
  grid_folder = paste('Grid_', grid_name, sep = '')
  sentinel2_grid = paste(sentinel2_folder, grid_folder, sep = '/')
  modis_grid = paste(modis_folder, grid_folder, sep = '/')
  topography_grid = paste(topography_folder, grid_folder, sep = '/')
  
  # Create a list of all predictor rasters
  predictors_sentinel2 = list.files(sentinel2_grid, pattern = 'tif$', full.names = TRUE)
  predictors_modis = list.files(modis_grid, pattern = 'tif$', full.names = TRUE)
  predictors_topography = list.files(topography_grid, pattern = 'tif$', full.names = TRUE)
  predictors_all = c(predictors_topography, predictors_sentinel2, predictors_modis)
  
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
    rename(sent2_05_11_shortIR1 = paste('Sent2_05May_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_12_shortIR2 = paste('Sent2_05May_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_2_blue = paste('Sent2_05May_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_3_green = paste('Sent2_05May_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_4_red = paste('Sent2_05May_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_5_redge1 = paste('Sent2_05May_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_6_redge2 = paste('Sent2_05May_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_7_redge3 = paste('Sent2_05May_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_8_nearIR = paste('Sent2_05May_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_8a_redge4 = paste('Sent2_05May_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_evi2 = paste('Sent2_05May_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_nbr = paste('Sent2_05May_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_ndmi = paste('Sent2_05May_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_ndsi = paste('Sent2_05May_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_ndvi = paste('Sent2_05May_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_05_ndwi = paste('Sent2_05May_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_11_shortIR1 = paste('Sent2_06June_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_12_shortIR2 = paste('Sent2_06June_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_2_blue = paste('Sent2_06June_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_3_green = paste('Sent2_06June_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_4_red = paste('Sent2_06June_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_5_redge1 = paste('Sent2_06June_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_6_redge2 = paste('Sent2_06June_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_7_redge3 = paste('Sent2_06June_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_8_nearIR = paste('Sent2_06June_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_8a_redge4 = paste('Sent2_06June_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_evi2 = paste('Sent2_06June_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_nbr = paste('Sent2_06June_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_ndmi = paste('Sent2_06June_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_ndsi = paste('Sent2_06June_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_ndvi = paste('Sent2_06June_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_06_ndwi = paste('Sent2_06June_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_11_shortIR1 = paste('Sent2_07July_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_12_shortIR2 = paste('Sent2_07July_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_2_blue = paste('Sent2_07July_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_3_green = paste('Sent2_07July_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_4_red = paste('Sent2_07July_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_5_redge1 = paste('Sent2_07July_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_6_redge2 = paste('Sent2_07July_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_7_redge3 = paste('Sent2_07July_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_8_nearIR = paste('Sent2_07July_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_8a_redge4 = paste('Sent2_07July_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_evi2 = paste('Sent2_07July_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_nbr = paste('Sent2_07July_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_ndmi = paste('Sent2_07July_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_ndsi = paste('Sent2_07July_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_ndvi = paste('Sent2_07July_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_07_ndwi = paste('Sent2_07July_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_11_shortIR1 = paste('Sent2_08August_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_12_shortIR2 = paste('Sent2_08August_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_2_blue = paste('Sent2_08August_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_3_green = paste('Sent2_08August_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_4_red = paste('Sent2_08August_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_5_redge1 = paste('Sent2_08August_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_6_redge2 = paste('Sent2_08August_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_7_redge3 = paste('Sent2_08August_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_8_nearIR = paste('Sent2_08August_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_8a_redge4 = paste('Sent2_08August_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_evi2 = paste('Sent2_08August_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_nbr = paste('Sent2_08August_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_ndmi = paste('Sent2_08August_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_ndsi = paste('Sent2_08August_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_ndvi = paste('Sent2_08August_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_08_ndwi = paste('Sent2_08August_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_11_shortIR1 = paste('Sent2_09September_11_shortInfrared1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_12_shortIR2 = paste('Sent2_09September_12_shortInfrared2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_2_blue = paste('Sent2_09September_2_blue_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_3_green = paste('Sent2_09September_3_green_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_4_red = paste('Sent2_09September_4_red_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_5_redge1 = paste('Sent2_09September_5_redEdge1_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_6_redge2 = paste('Sent2_09September_6_redEdge2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_7_redge3 = paste('Sent2_09September_7_redEdge3_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_8_nearIR = paste('Sent2_09September_8_nearInfrared_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_8a_redge4 = paste('Sent2_09September_8a_redEdge4_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_evi2 = paste('Sent2_09September_evi2_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_nbr = paste('Sent2_09September_nbr_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_ndmi = paste('Sent2_09September_ndmi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_ndsi = paste('Sent2_09September_ndsi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_ndvi = paste('Sent2_09September_ndvi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(sent2_09_ndwi = paste('Sent2_09September_ndwi_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(lst_05 = paste('MODIS_05May_meanLST_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(lst_06 = paste('MODIS_06June_meanLST_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(lst_07 = paste('MODIS_07July_meanLST_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(lst_08 = paste('MODIS_08August_meanLST_AKALB_Grid_', grid_name, sep = '')) %>%
    rename(lst_09 = paste('MODIS_09September_meanLST_AKALB_Grid_', grid_name, sep = ''))
  
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
              sent2_05_11_shortIR1 = round(mean(sent2_05_11_shortIR1), digits = 0),
              sent2_05_12_shortIR2 = round(mean(sent2_05_12_shortIR2), digits = 0),
              sent2_05_2_blue = round(mean(sent2_05_2_blue), digits = 0),
              sent2_05_3_green = round(mean(sent2_05_3_green), digits = 0),
              sent2_05_4_red = round(mean(sent2_05_4_red), digits = 0),
              sent2_05_5_redge1 = round(mean(sent2_05_5_redge1), digits = 0),
              sent2_05_6_redge2 = round(mean(sent2_05_6_redge2), digits = 0),
              sent2_05_7_redge3 = round(mean(sent2_05_7_redge3), digits = 0),
              sent2_05_8_nearIR = round(mean(sent2_05_8_nearIR), digits = 0),
              sent2_05_8a_redge4 = round(mean(sent2_05_8a_redge4), digits = 0),
              sent2_05_evi2 = round(mean(sent2_05_evi2), digits = 0),
              sent2_05_nbr = round(mean(sent2_05_nbr), digits = 0),
              sent2_05_ndmi = round(mean(sent2_05_ndmi), digits = 0),
              sent2_05_ndsi = round(mean(sent2_05_ndsi), digits = 0),
              sent2_05_ndvi = round(mean(sent2_05_ndvi), digits = 0),
              sent2_05_ndwi = round(mean(sent2_05_ndwi), digits = 0),
              sent2_06_11_shortIR1 = round(mean(sent2_06_11_shortIR1), digits = 0),
              sent2_06_12_shortIR2 = round(mean(sent2_06_12_shortIR2), digits = 0),
              sent2_06_2_blue = round(mean(sent2_06_2_blue), digits = 0),
              sent2_06_3_green = round(mean(sent2_06_3_green), digits = 0),
              sent2_06_4_red = round(mean(sent2_06_4_red), digits = 0),
              sent2_06_5_redge1 = round(mean(sent2_06_5_redge1), digits = 0),
              sent2_06_6_redge2 = round(mean(sent2_06_6_redge2), digits = 0),
              sent2_06_7_redge3 = round(mean(sent2_06_7_redge3), digits = 0),
              sent2_06_8_nearIR = round(mean(sent2_06_8_nearIR), digits = 0),
              sent2_06_8a_redge4 = round(mean(sent2_06_8a_redge4), digits = 0),
              sent2_06_evi2 = round(mean(sent2_06_evi2), digits = 0),
              sent2_06_nbr = round(mean(sent2_06_nbr), digits = 0),
              sent2_06_ndmi = round(mean(sent2_06_ndmi), digits = 0),
              sent2_06_ndsi = round(mean(sent2_06_ndsi), digits = 0),
              sent2_06_ndvi = round(mean(sent2_06_ndvi), digits = 0),
              sent2_06_ndwi = round(mean(sent2_06_ndwi), digits = 0),
              sent2_07_11_shortIR1 = round(mean(sent2_07_11_shortIR1), digits = 0),
              sent2_07_12_shortIR2 = round(mean(sent2_07_12_shortIR2), digits = 0),
              sent2_07_2_blue = round(mean(sent2_07_2_blue), digits = 0),
              sent2_07_3_green = round(mean(sent2_07_3_green), digits = 0),
              sent2_07_4_red = round(mean(sent2_07_4_red), digits = 0),
              sent2_07_5_redge1 = round(mean(sent2_07_5_redge1), digits = 0),
              sent2_07_6_redge2 = round(mean(sent2_07_6_redge2), digits = 0),
              sent2_07_7_redge3 = round(mean(sent2_07_7_redge3), digits = 0),
              sent2_07_8_nearIR = round(mean(sent2_07_8_nearIR), digits = 0),
              sent2_07_8a_redge4 = round(mean(sent2_07_8a_redge4), digits = 0),
              sent2_07_evi2 = round(mean(sent2_07_evi2), digits = 0),
              sent2_07_nbr = round(mean(sent2_07_nbr), digits = 0),
              sent2_07_ndmi = round(mean(sent2_07_ndmi), digits = 0),
              sent2_07_ndsi = round(mean(sent2_07_ndsi), digits = 0),
              sent2_07_ndvi = round(mean(sent2_07_ndvi), digits = 0),
              sent2_07_ndwi = round(mean(sent2_07_ndwi), digits = 0),
              sent2_08_11_shortIR1 = round(mean(sent2_08_11_shortIR1), digits = 0),
              sent2_08_12_shortIR2 = round(mean(sent2_08_12_shortIR2), digits = 0),
              sent2_08_2_blue = round(mean(sent2_08_2_blue), digits = 0),
              sent2_08_3_green = round(mean(sent2_08_3_green), digits = 0),
              sent2_08_4_red = round(mean(sent2_08_4_red), digits = 0),
              sent2_08_5_redge1 = round(mean(sent2_08_5_redge1), digits = 0),
              sent2_08_6_redge2 = round(mean(sent2_08_6_redge2), digits = 0),
              sent2_08_7_redge3 = round(mean(sent2_08_7_redge3), digits = 0),
              sent2_08_8_nearIR = round(mean(sent2_08_8_nearIR), digits = 0),
              sent2_08_8a_redge4 = round(mean(sent2_08_8a_redge4), digits = 0),
              sent2_08_evi2 = round(mean(sent2_08_evi2), digits = 0),
              sent2_08_nbr = round(mean(sent2_08_nbr), digits = 0),
              sent2_08_ndmi = round(mean(sent2_08_ndmi), digits = 0),
              sent2_08_ndsi = round(mean(sent2_08_ndsi), digits = 0),
              sent2_08_ndvi = round(mean(sent2_08_ndvi), digits = 0),
              sent2_08_ndwi = round(mean(sent2_08_ndwi), digits = 0),
              sent2_09_11_shortIR1 = round(mean(sent2_09_11_shortIR1), digits = 0),
              sent2_09_12_shortIR2 = round(mean(sent2_09_12_shortIR2), digits = 0),
              sent2_09_2_blue = round(mean(sent2_09_2_blue), digits = 0),
              sent2_09_3_green = round(mean(sent2_09_3_green), digits = 0),
              sent2_09_4_red = round(mean(sent2_09_4_red), digits = 0),
              sent2_09_5_redge1 = round(mean(sent2_09_5_redge1), digits = 0),
              sent2_09_6_redge2 = round(mean(sent2_09_6_redge2), digits = 0),
              sent2_09_7_redge3 = round(mean(sent2_09_7_redge3), digits = 0),
              sent2_09_8_nearIR = round(mean(sent2_09_8_nearIR), digits = 0),
              sent2_09_8a_redge4 = round(mean(sent2_09_8a_redge4), digits = 0),
              sent2_09_evi2 = round(mean(sent2_09_evi2), digits = 0),
              sent2_09_nbr = round(mean(sent2_09_nbr), digits = 0),
              sent2_09_ndmi = round(mean(sent2_09_ndmi), digits = 0),
              sent2_09_ndsi = round(mean(sent2_09_ndsi), digits = 0),
              sent2_09_ndvi = round(mean(sent2_09_ndvi), digits = 0),
              sent2_09_ndwi = round(mean(sent2_09_ndwi), digits = 0),
              lst_05 = round(mean(lst_05), digits = 0),
              lst_06 = round(mean(lst_06), digits = 0),
              lst_07 = round(mean(lst_07), digits = 0),
              lst_08 = round(mean(lst_08), digits = 0),
              lst_09 = round(mean(lst_09), digits = 0),
              num_points = n())
  
  # Export data as a csv
  output_csv = paste(output_folder, '/', grid_name, '.csv', sep = '')
  write.csv(sites_mean, file = output_csv)
  print('Finished extracting data to sites.')
}
