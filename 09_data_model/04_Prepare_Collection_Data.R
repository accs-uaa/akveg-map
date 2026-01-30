# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare collection data
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2024-08-09
# Usage: Script should be executed in R 4.3.2+.
# Description: "Prepare collection data" prepares collection data for integration with AKVEG data.
# ---------------------------------------------------------------------------

# Import required libraries
library(dplyr)
library(fs)
library(lubridate)
library(readr)
library(readxl)
library(RPostgres)
library(sf)
library(stringr)
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
atka_input = path(project_folder, 'collection_data/unprocessed', 'Atka_2019.xlsx')
dechaine_input = path(project_folder, 'collection_data/unprocessed', 'SBHP_Location_Data.xlsx')

# Define output files
site_output = path(project_folder, 'collection_data/processed', 'Collection_Sites_4269.csv')
vegetation_output = path(project_folder, 'collection_data/processed', 'Collection_Vegetation_4269.csv')

# Define queries
taxa_file = path(sdm_repository, 'queries/00_taxon_query.sql')

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

#### FORMAT COLLECTION DATA
####------------------------------

# Read and format Atka 2019 data
atka_data = read_xlsx(atka_input, sheet = 'Atka_2019') %>%
  # Compile taxonomic names
  mutate(name_original = case_when(is.na(Infrank) ~ paste(Gen, ' ', Spe, sep = ''),
                                   TRUE ~ paste(Gen, ' ', Spe, ' ', Infrank, ' ', Infname, sep = ''))) %>%
  # Format dates
  mutate(obs_date = paste(Year, '-07-', Day, sep = '')) %>%
  # Standardize column names
  rename(lat_dd = `Lat(decdegree)`,
         long_dd = `Long(decdegree)`,
         st_vst = `Collection #`) %>%
  # Select columns
  dplyr::select(st_vst, name_original, obs_date, lat_dd, long_dd)

# Read and format Dechaine data
dechaine_data = read_xlsx(dechaine_input, sheet = 'Dechaine') %>%
  # Remove unreliable absence records
  filter(presence == 1) %>%
  # Format dates
  mutate(obs_date = case_when(month(date) < 10 & day(date) < 10 ~ paste(year(date), '-0', month(date), '-0', day(date), sep = ''),
                              month(date) < 10 & day(date) >= 10 ~ paste(year(date), '-0', month(date), '-', day(date), sep = ''),
                              month(date) >= 10 & day(date) < 10 ~ paste(year(date), '-', month(date), '-0', day(date), sep = ''),
                              TRUE ~ paste(year(date), '-', month(date), '-', day(date), sep = ''))) %>%
  # Format site visit codes
  rowid_to_column('id') %>%
  mutate(st_vst = case_when(id < 10 ~ paste('EGD-', year(obs_date), '-00', id, sep = ''),
                            id < 100 ~ paste('EGD-', year(obs_date), '-0', id, sep = ''),
                            TRUE ~ paste('EGD-', year(obs_date), '-', id, sep = ''))) %>%
  # Standardize column names
  rename(name_original = taxon,
         lat_dd = latitude_dd,
         long_dd = longitude_dd) %>%
  # Select columns
  dplyr::select(st_vst, name_original, obs_date, lat_dd, long_dd) %>%
  # Convert geometries to points with EPSG 4326
  st_as_sf(x = ., coords = c('long_dd', 'lat_dd'), crs = 4326, remove = FALSE) %>%
  # Reproject coordinates to EPSG 4269
  st_transform(crs = st_crs(4269)) %>%
  # Replace coordinates in EPSG 4269
  mutate(long_dd = st_coordinates(.$geometry)[,1],
         lat_dd = st_coordinates(.$geometry)[,2]) %>%
  st_drop_geometry()

#### PARSE COLLECTION DATA
####------------------------------

# Format collection site data
site_data = rbind(atka_data, dechaine_data) %>%
  # Add missing columns
  mutate(prjct_cd = 'nps_npss_2018',
         scp_vasc = 'target species',
         scp_bryo = 'none',
         scp_lich = 'none',
         perspect = 'ground',
         cvr_mthd = 'voucher collection',
         plt_dim_m = '10 radius') %>%
  # Add accepted taxa names
  left_join(taxa_data, by = c('name_original' = 'taxon_name')) %>%
  rename(name_accepted = taxon_accepted) %>%
  filter(!is.na(name_accepted)) %>%
  # Select columns
  dplyr::select(st_vst, prjct_cd, scp_vasc, scp_bryo, scp_lich, perspect, cvr_mthd, plt_dim_m, obs_date, lat_dd, long_dd)

# Format collection vegetation data
vegetation_data = rbind(atka_data, dechaine_data) %>%
  # Add accepted taxa names
  left_join(taxa_data, by = c('name_original' = 'taxon_name')) %>%
  rename(name_accepted = taxon_accepted) %>%
  filter(!is.na(name_accepted)) %>%
  # Add missing columns
  mutate(cvr_type = 'voucher collection',
         dead_status = 'FALSE',
         cvr_pct = -998) %>%
  # Select columns
  dplyr::select(st_vst, cvr_type, name_accepted, dead_status, cvr_pct)

# Export data
write.csv(site_data, file = site_output, fileEncoding = 'UTF-8', row.names = FALSE)
write.csv(vegetation_data, file = vegetation_output, fileEncoding = 'UTF-8', row.names = FALSE)
