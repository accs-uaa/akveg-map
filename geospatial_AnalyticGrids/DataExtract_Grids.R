# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Features to Grids
# Author: Timm Nawrocki
# Last Updated: 2020-06-07
# Usage: Must be executed in R 4.0.0+.
# Description: "Extract Features to Grids" extracts data from rasters to prediction grids.
# ---------------------------------------------------------------------------

# Enter machine number
machine_number = 1

# Set root directory
root_folder = '/home/twnawrocki_rstudio'

# Define input grid list
grid_csv = paste(root_folder,
                 'meta/gridMinor_Selected.csv',
                 sep ='/')

# Define input folders
grid_folder = paste(root_folder,
                    'rasters/gridMinor',
                    sep = '/')
topography_folder = paste(root_folder,
                          'rasters/topography/gridded_select',
                          sep = '/')
sentinel1_folder = paste(root_folder,
                         'rasters/sentinel-1/gridded_select',
                         sep = '/')
sentinel2_folder = paste(root_folder,
                         'rasters/sentinel-2/gridded_select',
                         sep = '/')
modis_folder = paste(root_folder,
                     'rasters/modis/gridded_select',
                     sep = '/')
climate_folder = paste(root_folder,
                       'rasters/climate/gridded_select',
                       sep = '/')
output_folder = paste(root_folder,
                      'grids',
                      sep = '/')

# Install required libraries if they are not already installed.
Required_Packages <- c('dplyr', 'raster', 'rgdal', 'sp', 'stringr')
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

# Define input grid list
grid_table = read.csv(grid_csv, encoding = 'UTF-8')
grid_table = grid_table %>%
  filter(Major != 'C6')
grid_list = pull(grid_table, var = 'Minor')

# Subset grid list
first = (24 * machine_number) - 23
last = 24 * machine_number
grid_list = grid_list[first:last]
grid_length = length(grid_list)

# Loop through all grids with site data and extract features to sites
count = 1
for (grid in grid_list) {
  
  # Define output csv file
  output_csv = paste(output_folder, '/', grid, '.csv', sep = '')
  
  # If output csv file does not already exist, extract features to grid
  if (!file.exists(output_csv)) {
    print(paste('Extracting predictor data to Grid ', grid, ' (', count, ' of ', grid_length, ')...', sep=''))
  
    # Create full path to grid raster
    grid_file = paste(grid_folder, '/', 'Grid_', grid, '.tif', sep = '')
  
    # Convert raster to spatial dataframe of points
    grid_raster = raster(grid_file)
    grid_points = data.frame(rasterToPoints(grid_raster, spatial=FALSE))
    grid_points = grid_points[,1:2]
  
    # Identify grid name and predictor folders
    major_grid = paste('Grid_', substr(grid, start = 1, stop = 2), sep='')
    topography_grid = paste(topography_folder, major_grid, sep = '/')
    sentinel1_grid = paste(sentinel1_folder, major_grid, sep = '/')
    sentinel2_grid = paste(sentinel2_folder, major_grid, sep = '/')
    modis_grid = paste(modis_folder, major_grid, sep = '/')
    climate_grid = paste(climate_folder, major_grid, sep = '/')
  
    # Create a list of all predictor rasters
    predictors_topography = list.files(topography_grid, pattern = 'tif$', full.names = TRUE)
    predictors_sentinel1 = list.files(sentinel1_grid, pattern = 'tif$', full.names = TRUE)
    predictors_sentinel2 = list.files(sentinel2_grid, pattern = 'tif$', full.names = TRUE)
    predictors_modis = list.files(modis_grid, pattern = 'tif$', full.names = TRUE)
    predictors_climate = list.files(climate_grid, pattern = 'tif$', full.names = TRUE)
    predictors_all = c(predictors_topography,
                      predictors_sentinel1,
                      predictors_sentinel2,
                      predictors_modis,
                      predictors_climate)
    print(paste('Number of predictor rasters: ', length(predictors_all), sep = ''))
  
    # Generate a stack of all predictor rasters
    print('Creating raster stack...')
    start = proc.time()
    predictor_stack = stack(predictors_all)
    end = proc.time() - start
    print(end[3])
  
    # Read site data and extract features
    print('Extracting features...')
    start = proc.time()
    grid_extracted = data.frame(grid_points, extract(predictor_stack, grid_points))
    end = proc.time() - start
    print(end[3])
    
    # Define major grid name
    grid_name = substr(grid, start = 1, stop = 2)
  
    # Find plot level mean values and convert field names to standard
    grid_extracted = grid_extracted %>%
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
      rename(precip = paste('Precipitation_MeanAnnual_AKALB_Grid_', grid_name, sep = ''))
  
    # Export data as a csv
    write.csv(grid_extracted, file = output_csv, fileEncoding = 'UTF-8')
    print(paste('Finished extracting data to Grid ', grid, '.', sep = ''))
    print('----------')
  } else {
    print(paste('File for Grid ', grid, ' already exists.', sep = ''))
    print('----------')
  }
  
  # Increase the count by one
  count = count + 1
}