# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare AKVEG sites full
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-04-07
# Usage: Script should be executed in R 4.3.2+.
# Description: "Prepare AKVEG sites full" compiles all site and species data from the AKVEG Database.
# ---------------------------------------------------------------------------

# Import required libraries
library(dplyr)
library(fs)
library(janitor)
library(lubridate)
library(readr)
library(readxl)
library(RPostgres)
library(sf)
library(stringr)
library(terra)
library(tibble)
library(tidyr)

# Set root directory
drive = 'C:'
root_folder = 'ACCS_Work'

# Set repository directory
database_repository = path(drive, root_folder, 'Repositories/akveg-database')
credentials_folder = path(drive, root_folder, 'Credentials/akveg_private_read')

# Define input folders
project_folder = path(drive,
                      root_folder,
                      'Projects/VegetationEcology/AKVEG_Map/Data/Data_Input')
site_folder = path(project_folder, 'site_data')
output_folder = path(project_folder, 'ordination_data')

# Define input files
domain_input = path(project_folder, 'region_data', 'AlaskaYukon_MapDomain_3338.shp')
zone_input = path(project_folder, 'region_data', 'AlaskaYukon_VegetationZones_30m_3338.tif')
validation_input = path(project_folder, 'grid_100', 'AlaskaYukon_100_Tiles_3338.tif')
coast_input = path('D:', root_folder, 'Data/hydrography/processed/CoastDist_10m_3338.tif')
esa_input = path(project_folder, 'ancillary_data/processed/AlaskaYukon_ESAWorldCover2_10m_3338.tif')
fire_input = path(project_folder, 'ancillary_data/processed/AlaskaYukon_FireYear_10m_3338.tif')

# Define output files
taxa_output = path(output_folder, '00_taxonomy.csv')
site_point_output = path(output_folder, 'unprocessed/03_site_visit_3338.shp')
site_buffer_output = path(output_folder, 'unprocessed/03_site_visit_buffer_3338.shp')
vegetation_output = path(output_folder, '05_vegetation.csv')

# Define queries
taxa_file = path(database_repository, '05_queries/analysis/00_taxonomy.sql')
site_visit_file = path(database_repository, '05_queries/analysis/03_site_visit.sql')
vegetation_file = path(database_repository, '05_queries/analysis/05_vegetation.sql')

# Read local data (must be crs 3338)
domain_shape = st_read(domain_input)
zone_raster = rast(zone_input)
validation_raster = rast(validation_input)
coast_raster = rast(coast_input)
esa_raster = rast(esa_input)
fire_raster = rast(fire_input)

#### QUERY AKVEG DATABASE
####------------------------------

# Import database connection function
connection_script = path(database_repository, 'package_DataProcessing', 'connect_database_postgresql.R')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = path(credentials_folder, 'authentication_akveg_private.csv')
database_connection = connect_database_postgresql(authentication)

# Read taxonomy standard from AKVEG Database
taxa_query = read_file(taxa_file)
taxa_data = as_tibble(dbGetQuery(database_connection, taxa_query))

# Get geometry for intersection
intersect_geometry = st_geometry(domain_shape)

# Read site visit data from AKVEG Database
site_visit_query = read_file(site_visit_file)
site_visit_data = as_tibble(dbGetQuery(database_connection, site_visit_query)) %>%
  # Remove data from erroneous project
  filter(prjct_cd != 'nps_bering_2003') %>%
  # Convert geometries to points with EPSG:4269
  st_as_sf(x = ., coords = c('long_dd', 'lat_dd'), crs = 4269, remove = FALSE) %>%
  # Reproject coordinates to EPSG 3338
  st_transform(crs = st_crs(3338)) %>%
  # Add EPSG:3338 centroid coordinates
  mutate(cent_x = st_coordinates(.$geometry)[,1],
         cent_y = st_coordinates(.$geometry)[,2]) %>%
  # Subset points to those within the target zone
  st_intersection(intersect_geometry) %>% # Intersect with named feature
  # Extract raster data
  mutate(zone = terra::extract(zone_raster, ., raw=TRUE)[,2]) %>%
  mutate(valid = terra::extract(validation_raster, ., raw=TRUE)[,2]) %>%
  mutate(coast_dist = terra::extract(coast_raster, ., raw=TRUE)[,2]) %>%
  mutate(esa_type = terra::extract(esa_raster, ., raw=TRUE)[,2]) %>%
  mutate(fire_yr = terra::extract(fire_raster, ., raw=TRUE)[,2]) %>%
  # Drop geometry
  st_zm(drop = TRUE, what = "ZM") %>%
  # Process plot sizes into buffer radius
  mutate(plt_dim_m = case_when(perspect == 'aerial' & plt_dim_m == 'unknown' ~ '20 radius',
                               TRUE ~ plt_dim_m)) %>%
  mutate(plt_dim_m = case_when(perspect == 'ground' & plt_dim_m == 'unknown' ~ '5 radius',
                               TRUE ~ plt_dim_m)) %>%
  mutate(plt_rad_m = case_when(plt_dim_m == '55 radius' ~ 55,
                               (plt_dim_m == '34.7 radius' |
                                  plt_dim_m == '50×50') ~ 35,
                               plt_dim_m == '30 radius' ~ 30,
                               plt_dim_m == '30×80' ~ 25,
                               plt_dim_m == '23 radius' ~ 23,
                               (plt_dim_m == '20 radius' |
                                  plt_dim_m == '30×30' |
                                  plt_dim_m == '25×100') ~ 20,
                               (plt_dim_m == '25×25' |
                                  plt_dim_m == '20×40' |
                                  plt_dim_m == '20×100' |
                                  plt_dim_m == '20×80') ~ 18,
                               (plt_dim_m == '15 radius' |
                                  plt_dim_m == '20×20' |
                                  plt_dim_m == '15×30' |
                                  plt_dim_m == '15×100') ~ 15,
                               (plt_dim_m == '12.5 radius' |
                                  plt_dim_m == '18×18') ~ 12.5,
                               plt_dim_m == '11.6 radius' ~ 12,
                               (plt_dim_m == '10 radius' |
                                  plt_dim_m == '15×15' |
                                  plt_dim_m == '10×20' |
                                  plt_dim_m == '15×18' |
                                  plt_dim_m == '10×40' |
                                  plt_dim_m == '10×30') ~ 10,
                               (plt_dim_m == '8 radius' |
                                  plt_dim_m == '12×12') ~ 8,
                               (plt_dim_m == '10×10' |
                                  plt_dim_m == '10×12') ~ 7,
                               (plt_dim_m != '1 radius' |
                                  plt_dim_m != '1×7' |
                                  plt_dim_m != '1×8' |
                                  plt_dim_m != '1×10' |
                                  plt_dim_m != '1×12' |
                                  plt_dim_m != '2×2' |
                                  plt_dim_m != '2×5' |
                                  plt_dim_m != '2×7' |
                                  plt_dim_m != '2×10' |
                                  plt_dim_m != '2×12' |
                                  plt_dim_m != '2×20' |
                                  plt_dim_m != '3 radius' |
                                  plt_dim_m != '3×6' |
                                  plt_dim_m != '3×7' |
                                  plt_dim_m != '3×8' |
                                  plt_dim_m != '3×10' |
                                  plt_dim_m != '3×12' |
                                  plt_dim_m != '3×15' |
                                  plt_dim_m != '3×20' |
                                  plt_dim_m != '3×25' |
                                  plt_dim_m != '4×4' |
                                  plt_dim_m != '4×8' |
                                  plt_dim_m != '4×25' |
                                  plt_dim_m != '5×5' |
                                  plt_dim_m != '5×8' |
                                  plt_dim_m != '5×10' |
                                  plt_dim_m != '5×15' |
                                  plt_dim_m != '5×20' |
                                  plt_dim_m != '5×30' |
                                  plt_dim_m != '6×6' |
                                  plt_dim_m != '6×10' |
                                  plt_dim_m != '6×12' |
                                  plt_dim_m != '7×8' |
                                  plt_dim_m != '7×10' |
                                  plt_dim_m == '5 radius' |
                                  plt_dim_m == '8×8' |
                                  plt_dim_m == '1×10' |
                                  plt_dim_m == '8×10' |
                                  plt_dim_m == '8×12') ~ 5,
                               TRUE ~ -999)) %>%
  # Select columns
  dplyr::select(st_vst, prjct_cd, st_code, data_tier, obs_date, scp_vasc, scp_bryo, scp_lich, perspect,
                cvr_mthd, strc_class, zone, valid, coast_dist, esa_type, fire_yr, homogeneous, plt_dim_m,
                plt_rad_m, lat_dd, long_dd, cent_x, cent_y, geometry)

# Buffer sites
site_buffer_data = site_visit_data %>%
  st_buffer(.$plt_rad_m)

# Read vegetation cover data from AKVEG Database
vegetation_query = read_file(vegetation_file)
vegetation_data = as_tibble(dbGetQuery(database_connection, vegetation_query))

# Sites with valid vegetation cover data
veg_sites = vegetation_data %>%
  distinct(st_vst)
missing_data = site_visit_data %>%
  anti_join(veg_sites, by = 'st_vst')

# Check number of cover observations per project
project_summary = vegetation_data %>%
  left_join(site_visit_data, join_by('st_vst')) %>%
  group_by(prjct_cd) %>%
  summarize(obs_n = n())

# Save site visits to shapefiles
st_write(site_visit_data, site_point_output, append = FALSE)
st_write(site_buffer_data, site_buffer_output, append = FALSE)

# Save tabular data
taxa_data %>%
  write.csv(., file = taxa_output, fileEncoding = 'UTF-8', row.names = FALSE)
vegetation_data %>%
  write.csv(., file = vegetation_output, fileEncoding = 'UTF-8', row.names = FALSE)
