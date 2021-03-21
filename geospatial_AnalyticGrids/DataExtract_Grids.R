# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract Features to Grids
# Author: Timm Nawrocki
# Last Updated: 2021-03-20
# Usage: Must be executed in R 4.0.0+.
# Description: "Extract Features to Grids" extracts data from rasters to prediction grids.
# ---------------------------------------------------------------------------

# Enter machine number
machine_number = 1

# Define input grid list
grid_table = '/home/twn_rstudio/gridMinor.xlsx'

# Define input folders
grid_folder = '/home/twn_rstudio/gridMinor'
raster_folder = '/home/twn_rstudio/rasters'
output_folder = '/home/twn_rstudio/extracted_grids'

# Import required libraries
library(dplyr)
library(raster)
library(readxl)
library(rgdal)
library(sp)
library(stringr)

# Define and subset input grid data
grid_data = read_excel(grid_table, sheet = 'gridMinor')
first = (265 * machine_number) - 264
last = 265 * machine_number
grid_data = slice(grid_data, (first:last))
major_data = grid_data %>%
  distinct(Major)
major_list = pull(major_data, var = 'Major')
minor_list = pull(grid_data, var = 'Minor')
minor_length = length(minor_list)

# Loop through all grids with site data and extract features to sites
for (major in major_list) {
  print(paste('Creating raster stack for Major Grid ', major, '...', sep = ''))
  start = proc.time()
  
  # Identify grid name and predictor folders
  major_grid = paste('Grid_', major, sep='')
  raster_grid = paste(raster_folder, major_grid, sep = '/')
  
  # Create a list of all predictor rasters
  predictors_all = list.files(raster_grid, pattern = 'tif$', full.names = TRUE)
  print(paste('Number of predictor rasters: ', length(predictors_all), sep = ''))
  
  # Generate a stack of all predictor rasters
  predictor_stack = stack(predictors_all)
  end = proc.time() - start
  print(paste('Finished compiling raster stack in ', end[3], ' seconds.', sep = ''))
  
  # Iterate through all minor grids and extract raster stack to grids
  count = 1
  for(minor in minor_list) {
    
    # Define output csv file
    output_csv = paste(output_folder, '/', minor, '.csv', sep = '')
    
    # Define minor group
    minor_group = substr(minor, start = 1, stop = 2)
    
    # If output csv file does not already exist, then extract features to grid
    if (!file.exists(output_csv)) {
      # If minor grid is within major grid, then extract features to grid
      if (minor_group == major) {
        print(paste('Extracting predictor data to Grid ', minor, ' (', count, ' of ', minor_length, ')...', sep=''))
        start = proc.time()
        
        # Create full path to grid raster
        minor_file = paste(grid_folder, '/', 'Grid_', minor, '.tif', sep = '')
        
        # Convert raster to data frame of points
        minor_raster = raster(minor_file)
        minor_points = data.frame(rasterToPoints(minor_raster, spatial = FALSE))
        minor_points = minor_points[,1:2]
        
        # Read site data and extract features
        minor_extracted = data.frame(minor_points, extract(predictor_stack, minor_points))
        
        # Find plot level mean values and convert field names to standard
        minor_extracted = minor_extracted %>%
          rename(aspect = paste('Aspect_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(wetness = paste('CompoundTopographic_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(elevation = paste('Elevation_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(slope = paste('MeanSlope_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(roughness = paste('Roughness_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(exposure = paste('SiteExposure_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(area = paste('SurfaceArea_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(relief = paste('SurfaceRelief_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(position = paste('TopographicPosition_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(radiation = paste('TopographicRadiation_Composite_10m_Beringia_AKALB_Grid_', major, sep = '')) %>%
          rename(vh = paste('Sent1_vh_AKALB_Grid_', major, sep = '')) %>%
          rename(vv = paste('Sent1_vv_AKALB_Grid_', major, sep = '')) %>%
          rename(shortIR1_06 = paste('Sent2_06_11_shortInfrared1_AKALB_Grid_', major, sep = '')) %>%
          rename(shortIR2_06 = paste('Sent2_06_12_shortInfrared2_AKALB_Grid_', major, sep = '')) %>%
          rename(blue_06 = paste('Sent2_06_2_blue_AKALB_Grid_', major, sep = '')) %>%
          rename(green_06 = paste('Sent2_06_3_green_AKALB_Grid_', major, sep = '')) %>%
          rename(red_06 = paste('Sent2_06_4_red_AKALB_Grid_', major, sep = '')) %>%
          rename(redge1_06 = paste('Sent2_06_5_redEdge1_AKALB_Grid_', major, sep = '')) %>%
          rename(redge2_06 = paste('Sent2_06_6_redEdge2_AKALB_Grid_', major, sep = '')) %>%
          rename(redge3_06 = paste('Sent2_06_7_redEdge3_AKALB_Grid_', major, sep = '')) %>%
          rename(nearIR_06 = paste('Sent2_06_8_nearInfrared_AKALB_Grid_', major, sep = '')) %>%
          rename(redge4_06 = paste('Sent2_06_8a_redEdge4_AKALB_Grid_', major, sep = '')) %>%
          rename(evi2_06 = paste('Sent2_06_evi2_AKALB_Grid_', major, sep = '')) %>%
          rename(nbr_06 = paste('Sent2_06_nbr_AKALB_Grid_', major, sep = '')) %>%
          rename(ndmi_06 = paste('Sent2_06_ndmi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndsi_06 = paste('Sent2_06_ndsi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndvi_06 = paste('Sent2_06_ndvi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndwi_06 = paste('Sent2_06_ndwi_AKALB_Grid_', major, sep = '')) %>%
          rename(shortIR1_07 = paste('Sent2_07_11_shortInfrared1_AKALB_Grid_', major, sep = '')) %>%
          rename(shortIR2_07 = paste('Sent2_07_12_shortInfrared2_AKALB_Grid_', major, sep = '')) %>%
          rename(blue_07 = paste('Sent2_07_2_blue_AKALB_Grid_', major, sep = '')) %>%
          rename(green_07 = paste('Sent2_07_3_green_AKALB_Grid_', major, sep = '')) %>%
          rename(red_07 = paste('Sent2_07_4_red_AKALB_Grid_', major, sep = '')) %>%
          rename(redge1_07 = paste('Sent2_07_5_redEdge1_AKALB_Grid_', major, sep = '')) %>%
          rename(redge2_07 = paste('Sent2_07_6_redEdge2_AKALB_Grid_', major, sep = '')) %>%
          rename(redge3_07 = paste('Sent2_07_7_redEdge3_AKALB_Grid_', major, sep = '')) %>%
          rename(nearIR_07 = paste('Sent2_07_8_nearInfrared_AKALB_Grid_', major, sep = '')) %>%
          rename(redge4_07 = paste('Sent2_07_8a_redEdge4_AKALB_Grid_', major, sep = '')) %>%
          rename(evi2_07 = paste('Sent2_07_evi2_AKALB_Grid_', major, sep = '')) %>%
          rename(nbr_07 = paste('Sent2_07_nbr_AKALB_Grid_', major, sep = '')) %>%
          rename(ndmi_07 = paste('Sent2_07_ndmi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndsi_07 = paste('Sent2_07_ndsi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndvi_07 = paste('Sent2_07_ndvi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndwi_07 = paste('Sent2_07_ndwi_AKALB_Grid_', major, sep = '')) %>%
          rename(shortIR1_08 = paste('Sent2_08.09_11_shortInfrared1_AKALB_Grid_', major, sep = '')) %>%
          rename(shortIR2_08 = paste('Sent2_08.09_12_shortInfrared2_AKALB_Grid_', major, sep = '')) %>%
          rename(blue_08 = paste('Sent2_08.09_2_blue_AKALB_Grid_', major, sep = '')) %>%
          rename(green_08 = paste('Sent2_08.09_3_green_AKALB_Grid_', major, sep = '')) %>%
          rename(red_08 = paste('Sent2_08.09_4_red_AKALB_Grid_', major, sep = '')) %>%
          rename(redge1_08 = paste('Sent2_08.09_5_redEdge1_AKALB_Grid_', major, sep = '')) %>%
          rename(redge2_08 = paste('Sent2_08.09_6_redEdge2_AKALB_Grid_', major, sep = '')) %>%
          rename(redge3_08 = paste('Sent2_08.09_7_redEdge3_AKALB_Grid_', major, sep = '')) %>%
          rename(nearIR_08 = paste('Sent2_08.09_8_nearInfrared_AKALB_Grid_', major, sep = '')) %>%
          rename(redge4_08 = paste('Sent2_08.09_8a_redEdge4_AKALB_Grid_', major, sep = '')) %>%
          rename(evi2_08 = paste('Sent2_08.09_evi2_AKALB_Grid_', major, sep = '')) %>%
          rename(nbr_08 = paste('Sent2_08.09_nbr_AKALB_Grid_', major, sep = '')) %>%
          rename(ndmi_08 = paste('Sent2_08.09_ndmi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndsi_08 = paste('Sent2_08.09_ndsi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndvi_08 = paste('Sent2_08.09_ndvi_AKALB_Grid_', major, sep = '')) %>%
          rename(ndwi_08 = paste('Sent2_08.09_ndwi_AKALB_Grid_', major, sep = '')) %>%
          rename(lstWarmth = paste('MODIS_LST_WarmthIndex_AKALB_Grid_', major, sep = '')) %>%
          rename(janMin = paste('January_MinimumTemperature_AKALB_Grid_', major, sep = '')) %>%
          rename(summerWarmth = paste('SummerWarmth_MeanAnnual_AKALB_Grid_', major, sep = '')) %>%
          rename(precip = paste('Precipitation_MeanAnnual_AKALB_Grid_', major, sep = ''))
        
        # Export data as a csv
        write.csv(minor_extracted, file = output_csv, fileEncoding = 'UTF-8')
        end = proc.time() - start
        print(paste('Finished extracting data to Grid ', minor, '.', sep = ''))
        print(paste('Time elapsed: ', end[3], ' seconds', sep = ''))
        print('----------')
      } else {
        print(paste('Minor Grid ', minor, ' not part of raster stack for', major, '.', sep = ''))
        print('----------')
      }
    } else {
      print(paste('File for Grid ', minor, ' already exists.', sep = ''))
      print('----------')
    }
    # Increase counter
    count = count + 1
  }
}