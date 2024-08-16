# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare taxa presence-absence data
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2024-08-08
# Usage: Script should be executed in R 4.3.2+.
# Description: "Prepare taxa presence-absence data" prepares train/test data for each target species.
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
drive = 'D:'
root_folder = 'ACCS_Work'

# Set repository directory
akveg_repository = path('C:', root_folder, 'Repositories/akveg-database')
sdm_repository = path('C:', root_folder, 'Repositories/akveg-map')
credentials_folder = path('C:', root_folder, 'Credentials/akveg_private_read')

# Define input folders
project_folder = path(drive, root_folder,
                      'Projects/VegetationEcology/AKVEG_Map',
                      'Data/Data_Input')

# Define input files
schema_input = path(project_folder, 'AKVEG_Schema_20240813.xlsx')
zone_input = path(project_folder, 'region_data', 'AlaskaYukon_MapDomain_3338.shp')
zone_file = path(project_folder, 'region_data', 'AlaskaYukon_VegetationZones_30m_3338.tif')
validation_file = path(project_folder, 'validation_grid', 'AlaskaYukon_100_Tiles_3338.tif')
collection_site_input = path(project_folder, 'collection_data/processed', 'Collection_Sites_4269.csv')
collection_veg_input = path(project_folder, 'collection_data/processed', 'Collection_Vegetation_4269.csv')

# Define project geodatabase and absence layer
project_geodatabase = path(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data/AKVEG_Map.gdb')
absence_layer = path('AlaskaYukon_Absences_3338')

# Define output files
site_point_output = path(project_folder, 'site_data', 'AKVEG_Sites_Points_3338.shp')
site_buffer_output = path(project_folder, 'site_data', 'AKVEG_Sites_Buffered_3338.shp')

# Define queries
taxa_file = path(sdm_repository, 'queries/00_taxon_query.sql')
site_visit_file = path(sdm_repository, 'queries/03_site_visit_query.sql')
vegetation_file = path(sdm_repository, 'queries/05_vegetation_query.sql')

# Read collection data
collection_site = read_csv(collection_site_input)
collection_veg = read_csv(collection_veg_input)

# Read local data (must be crs 3338)
zone_shape = st_read(zone_input)

#### QUERY AKVEG DATABASE
####------------------------------

# Import database connection function
connection_script = path(akveg_repository, 'package_DataProcessing', 'connect_database_postgresql.R')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = path(credentials_folder, 'authentication_akveg_private.csv')
database_connection = connect_database_postgresql(authentication)

# Read taxonomy standard from AKVEG Database
taxa_query = read_file(taxa_file)
taxa_data = as_tibble(dbGetQuery(database_connection, taxa_query))

# Read site visit data from AKVEG Database
site_visit_query = read_file(site_visit_file)
site_visit_import = as_tibble(dbGetQuery(database_connection, site_visit_query)) %>%
  rbind(collection_site)

# Read vegetation cover data from AKVEG Database
vegetation_query = read_file(vegetation_file)
vegetation_import = as_tibble(dbGetQuery(database_connection, vegetation_query)) %>%
  rbind(collection_veg)

#### FORMAT SITE VISITS
####------------------------------

# Format absence sites
absence_data = st_read(dsn = project_geodatabase, layer = absence_layer) %>%
  dplyr::select(Shape) %>%
  # Set observe date
  mutate(obs_date = '2024-07-29') %>%
  # Format site visit codes
  rowid_to_column('id') %>%
  mutate(st_vst = case_when(id < 10 ~ paste('ABS-', year(obs_date), '-000', id, sep = ''),
                            id < 100 ~ paste('ABS-', year(obs_date), '-00', id, sep = ''),
                            id < 1000 ~ paste('ABS-', year(obs_date), '-0', id, sep = ''),
                            TRUE ~ paste('ABS-', year(obs_date), '-', id, sep = ''))) %>%
  # Add missing columns
  mutate(prjct_cd = 'akveg_absences',
         scp_vasc = 'exhaustive',
         scp_bryo = 'exhaustive',
         scp_lich = 'exhaustive',
         perspect = 'aerial',
         cvr_mthd = 'image interpretation',
         plt_rad_m = 10) %>%
  # Rename geometry
  rename(geometry = Shape) %>%
  # Add centroid coordinates in EPSG 3338
  mutate(cent_x = st_coordinates(.$geometry)[,1],
         cent_y = st_coordinates(.$geometry)[,2]) %>%
  # Add latitude and longitude in EPSG 4269
  st_transform(crs = st_crs(4269)) %>%
  mutate(long_dd = st_coordinates(.$geometry)[,1],
         lat_dd = st_coordinates(.$geometry)[,2]) %>%
  # Select columns
  dplyr::select(st_vst, prjct_cd, obs_date, scp_vasc, scp_bryo, scp_lich, perspect,
                cvr_mthd, plt_rad_m, lat_dd, long_dd, cent_x, cent_y, geometry) %>%
  # Drop geometry
  st_drop_geometry()

# Format site visit data
site_point_data = site_visit_import %>%
  # Process plot sizes into buffer radius
  mutate(plt_dim_m = case_when(perspect == 'aerial' & plt_dim_m == 'unknown' ~ '20 radius',
                               TRUE ~ plt_dim_m)) %>%
  filter(plt_dim_m != '2×2' &
           plt_dim_m != '5×8' &
           plt_dim_m != '2×7' &
           plt_dim_m != '1×10' &
           plt_dim_m != '3×7' &
           plt_dim_m != '2×5' &
           plt_dim_m != '5×20' &
           plt_dim_m != '3×20' &
           plt_dim_m != '4×4' &
           plt_dim_m != 'unknown' &
           plt_dim_m != '8×8' &
           plt_dim_m != '4×25' &
           plt_dim_m != '5×15' &
           plt_dim_m != '6×6' &
           plt_dim_m != '3×6' &
           plt_dim_m != '5×10' &
           plt_dim_m != '4×8' &
           plt_dim_m != '5×5' &
           plt_dim_m != '5×30' &
           plt_dim_m != '8×10' &
           plt_dim_m != '8×12' &
           plt_dim_m != '2×20' &
           plt_dim_m != '6×10' &
           plt_dim_m != '7×10' &
           plt_dim_m != '2×12' &
           plt_dim_m != '3×12' &
           plt_dim_m != '6×12' &
           plt_dim_m != '3×10' &
           plt_dim_m != '3×15' &
           plt_dim_m != '1×12' &
           plt_dim_m != '3×25' &
           plt_dim_m != '1×8' &
           plt_dim_m != '1×7' &
           plt_dim_m != '7×8' &
           plt_dim_m != '3×8' &
           plt_dim_m != '2×10' &
           plt_dim_m != '1 radius' &
           plt_dim_m != '3 radius') %>%
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
                               plt_dim_m == '5 radius' ~ 5)) %>%
  # Convert geometries to points with EPSG 4269
  st_as_sf(x = ., coords = c('long_dd', 'lat_dd'), crs = 4269, remove = FALSE) %>%
  # Reproject coordinates to EPSG 3338
  st_transform(crs = st_crs(3338)) %>%
  mutate(cent_x = st_coordinates(.$geometry)[,1],
         cent_y = st_coordinates(.$geometry)[,2]) %>%
  # Select columns
  dplyr::select(st_vst, prjct_cd, obs_date, scp_vasc, scp_bryo, scp_lich, perspect,
                cvr_mthd, plt_rad_m, lat_dd, long_dd, cent_x, cent_y, geometry) %>%
  # Drop geometry
  st_drop_geometry() %>%
  # Add absence sites
  rbind(absence_data) %>%
  # Remove sites outside of the Alaska-Yukon Map Domain
  st_as_sf(x = ., coords = c('cent_x', 'cent_y'), crs = 3338, remove = FALSE) %>%
  st_intersection(zone_shape) %>%
  st_zm(drop = TRUE, what = "ZM")
  
# Buffer sites
site_buffer_data = site_point_data %>%
  st_buffer(.$plt_rad_m)

# Save selected points to shapefile
st_write(site_point_data, site_point_output, append = FALSE)
st_write(site_buffer_data, site_buffer_output, append = FALSE)

#### EXPORT SPECIES DATA
####------------------------------

# Check number of vegetation observations per project
project_summary = vegetation_import %>%
  inner_join(site_point_data, join_by('st_vst')) %>%
  group_by(prjct_cd) %>%
  summarize(obs_n = n())

# Read raster data
zone_raster = rast(zone_file)
validation_raster = rast(validation_file)

# Read AKVEG Schema
schema_data = read_xlsx(schema_input, sheet = 'foliar_cover') %>%
  filter(priority == 1) %>%
  select(-comment)

# Create target list
group_list = schema_data %>%
  distinct(target_abbr) %>%
  pull(target_abbr)

# Export data for each target
count = 1
for (group in group_list) {
  # Define output file
  target_output = path(project_folder, 'species_data', paste('cover_', group, '_3338.csv', sep = ''))
  
  # Define taxon list
  taxa_list = schema_data %>%
    filter(target_abbr == group) %>%
    pull(constituents)
  
  # Define life form
  lifeform = schema_data %>%
    filter(target_abbr == group) %>%
    distinct(lifeform) %>%
    pull(lifeform)
  
  # Compile species presence/absence data
  vegetation_data = vegetation_import %>%
    # Restrict data to taxon list
    filter(name_accepted %in% taxa_list &
             dead_status == 'FALSE') %>%
    # Set absences to zero
    mutate(cvr_pct = case_when(cvr_pct == -999 ~ 0,
                               TRUE ~ cvr_pct)) %>%
    # Sum the cover of all taxa in taxa list per site visit
    group_by(st_vst) %>%
    summarize(cvr_pct = sum(cvr_pct),
              number = n()) %>%
    # Join the site visit data to interpret absences
    full_join(site_point_data, by = 'st_vst') %>%
    filter(!is.na(obs_date)) %>%
    # Interpret presence and absence
    mutate(presence = case_when(cvr_pct >= 0.5 ~ 1,
                                cvr_pct == -998 ~ 1, # No cover data recorded, but species is present (i.e., voucher collection)
                                TRUE ~ 0)) %>%
    # Assign zero value to absences
    mutate(cvr_pct = case_when(presence == 0 ~ 0,
                               TRUE ~ cvr_pct)) %>%
    # Assign group name
    mutate(target_abbr = group) %>%
    # Restrict absences based on lifeform scopes
    {if (lifeform == 'vascular')
      filter(., (presence == 1)
             | (presence == 0
                & (scp_vasc == 'exhaustive' | scp_vasc == 'non-trace species')))
      else
        filter(., !is.na(st_vst))} %>%
    {if (lifeform == 'bryophyte')
      filter(., (presence == 1)
             | (presence == 0
                & (scp_bryo == 'exhaustive' | scp_bryo == 'non-trace species' | scp_bryo == 'common species')))
      else
        filter(., !is.na(st_vst))} %>%
    {if (lifeform == 'lichen')
      filter(., (presence == 1)
             | (presence == 0
                & (scp_lich == 'exhaustive' | scp_lich == 'non-trace species' | scp_lich == 'common species')))
      else
        filter(., !is.na(st_vst))} %>%
    # Filter questionable records for Senecio pseudoarnica
    {if (group == 'senpse')
      filter(., st_vst != 'NSSI11186_20110813' &
               st_vst != 'KEFJ04A055_20040807' &
               st_vst != 'KEFJ040351_20040808' &
               st_vst != 'KATM00062_20000808' &
               st_vst != 'KEFJ040361_20040808' &
               st_vst != 'haba-t2-1400_20080721')
      else
        filter(., !is.na(st_vst))} %>%
    # Select columns
    dplyr::select(st_vst, target_abbr, cvr_pct, presence, cent_x, cent_y) %>%
    # Create point geometry
    st_as_sf(x = ., coords = c('cent_x', 'cent_y'), crs = 3338, remove = FALSE) %>%
    mutate(zone = terra::extract(zone_raster, ., raw=TRUE)[,2]) %>%
    mutate(valid = terra::extract(validation_raster, ., raw=TRUE)[,2]) %>%
    st_drop_geometry()
  
  # Export data to output table
  write.csv(vegetation_data, file = target_output, fileEncoding = 'UTF-8', row.names = FALSE)
  
  # Increase count
  count = count + 1
}
