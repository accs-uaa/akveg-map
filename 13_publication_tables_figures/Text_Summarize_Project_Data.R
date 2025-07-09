# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize project data
# Author: Timm Nawrocki, Amanda Droghini, Alaska Center for Conservation Science
# Last Updated: 2025-07-07
# Usage: Script should be executed in R 4.4.3+.
# Description: "Summarize project data" creates a table for publication to display a summary of the characteristics per project of data used to train and validate foliar cover maps.
# ---------------------------------------------------------------------------

# Import required libraries ----
library(dplyr)
library(fs)
library(janitor)
library(lubridate)
library(readr)
library(readxl)
library(writexl)
library(RPostgres)
library(sf)
library(stringr)
library(terra)
library(tibble)
library(tidyr)

#### Set up directories and files ------------------------------

# Set round date
round_date = 'round_20241124'

# Define indicators
indicators = c('alnus', 'betshr', 'bettre', 'brotre', 'dryas', 'dsalix', 'empnig', 'erivag', 'mwcalama',
               'ndsalix', 'nerishr', 'picgla', 'picmar', 'picsit', 'poptre', 'populbt', 'rhoshr', 'rubspe',
               'sphagn', 'tsumer', 'vaculi', 'vacvit', 'wetsed')

# Set root directory (modify to your folder structure)
drive = 'C:'
root_folder = 'ACCS_Work'

# Define input folders (modify to your folder structure)
database_repository = path(drive, root_folder, 'Repositories/akveg-database-public')
credentials_folder = path(drive, root_folder, 'Credentials/akveg_private_read')
project_folder = path(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map')
input_folder = path(project_folder, 'Data/Data_Input/species_data')
output_folder = path(project_folder, 'Documents/Manuscript_FoliarCover_FloristicGradients/tables')

# Define input files
fireyear_input = path(project_folder, 'Data/Data_Input/ancillary_data/processed/AlaskaYukon_FireYear_10m_3338.tif')

# Define output files
summary_output = path(output_folder, 'text_summary_data.xlsx')
project_output = path(output_folder, 'appendixS5_project_summary.xlsx')

# Define queries
taxa_file = path(database_repository, 'queries/00_taxonomy.sql')
project_file = path(database_repository, 'queries/01_project.sql')
site_visit_file = path(database_repository, 'queries/03_site_visit.sql')
vegetation_file = path(database_repository, 'queries/05_vegetation.sql')
abiotic_file = path(database_repository, 'queries/06_abiotic_top_cover.sql')

# Read local data
fireyear_raster = rast(fireyear_input)

#### QUERY AKVEG DATABASE
####------------------------------

# Import database connection function
connection_script = path(database_repository, 'pull_functions', 'connect_database_postgresql.R')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = path(credentials_folder, 'authentication_akveg_private.csv')
database_connection = connect_database_postgresql(authentication)

# Read taxonomy standard from AKVEG Database
taxa_query = read_file(taxa_file)
taxa_data = as_tibble(dbGetQuery(database_connection, taxa_query))

# Read project data from AKVEG Database
project_query = read_file(project_file)
project_data = as_tibble(dbGetQuery(database_connection, project_query))

# Read site visit data from AKVEG Database
site_visit_query = read_file(site_visit_file)
site_visit_data = as_tibble(dbGetQuery(database_connection, site_visit_query)) %>%
  # Convert geometries to points with EPSG:4269
  st_as_sf(x = ., coords = c('longitude_dd', 'latitude_dd'), crs = 4269, remove = FALSE) %>%
  # Reproject coordinates to EPSG 3338
  st_transform(crs = st_crs(3338)) %>%
  # Add EPSG:3338 centroid coordinates
  mutate(cent_x = st_coordinates(.$geometry)[,1],
         cent_y = st_coordinates(.$geometry)[,2]) %>%
  # Extract raster data to points
  mutate(fire_year = terra::extract(fireyear_raster, ., raw=TRUE)[,2]) %>%
  # Drop geometry
  st_zm(drop = TRUE, what = "ZM") %>%
  # Drop geometry
  st_drop_geometry()
  
# Read vegetation data from AKVEG Database
vegetation_query = read_file(vegetation_file)
vegetation_data = as_tibble(dbGetQuery(database_connection, vegetation_query))

# Read abiotic top cover data from AKVEG Database
abiotic_query = read_file(abiotic_file)
abiotic_data = as_tibble(dbGetQuery(database_connection, abiotic_query))

# Compile sites from vegetation and abiotic cover
vegetation_sites = vegetation_data %>%
  distinct(site_visit_code)
abiotic_sites = abiotic_data %>%
  distinct(site_visit_code)
site_check = rbind(vegetation_sites, abiotic_sites) %>%
  distinct(site_visit_code)

# Check that no site visits lack data for either vegetation cover or abiotic top cover
site_visit_nodata = site_visit_data %>%
  anti_join(site_check, by = 'site_visit_code')
site_visit_data = site_visit_data %>%
  inner_join(site_check, by = 'site_visit_code')

# Identify public data
site_visit_public = site_visit_data %>%
  left_join(project_data, by = 'project_code') %>%
  filter(private == FALSE)

#### COMPILE SELECTED SITE VISITS
####------------------------------

# Prepare empty data frames
site_visit_selected = tibble(site_visit_code = 'a')[0,]
site_visit_count = tibble(indicator = 'a', site_visits = 1)[0,]

# Read data frame of combined selected data
for (indicator in indicators) {
  # Set input files
  indicator_input = path(input_folder, paste('cover_', indicator, '_3338.csv', sep = ''))
  
  # Read results
  indicator_data = read_csv(indicator_input) %>%
    select(st_vst) %>%
    rename(site_visit_code = st_vst) %>%
    distinct(site_visit_code)
  
  # Omit the generated absences from the counts
  site_visit_true = indicator_data %>%
    inner_join(site_visit_data, by = 'site_visit_code')
  
  # Store number of site visits per indicator
  indicator_sites = tibble(indicator = indicator, site_visits = nrow(site_visit_true))
  
  # Bind rows
  site_visit_selected = rbind(site_visit_selected, indicator_data)
  site_visit_count = rbind(site_visit_count, indicator_sites)
  
}

# Identify unique selected sites across all indicators
absence_data = site_visit_selected %>%
  distinct(site_visit_code) %>%
  anti_join(site_visit_data, by = 'site_visit_code') %>%
  filter(grepl('ABS-', site_visit_code))
site_visit_selected = site_visit_selected %>%
  distinct(site_visit_code) %>%
  inner_join(site_visit_data, by = 'site_visit_code')

#### SUMMARIZE AKVEG DATABASE
####------------------------------

# Summarize vegetation observations
vegetation_observations = vegetation_data %>%
  left_join(taxa_data, by = join_by('code_accepted' == 'code_akveg')) %>%
  filter(taxon_category != 'unknown')

# Summarize number of original visits and revisits
site_visit_summary = site_visit_data %>%
  group_by(site_code) %>%
  summarize(site_visit_n = n(),
            min_year = min(year(observe_date)),
            max_year = max(year(observe_date)))
original_visit_data = site_visit_data %>%
  left_join(site_visit_summary, by = 'site_code') %>%
  filter(min_year == year(observe_date)) %>%
  select(-site_visit_n, -min_year, -max_year)
revisit_data = site_visit_data %>%
  anti_join(original_visit_data, by = 'site_visit_code')

# Summarize site visits within year range
site_visit_potential = site_visit_data %>%
  filter(year(observe_date) >= 2000 & year(observe_date) <= 2024)

# Summarize site visits removed by fire
fire_remove_data = site_visit_potential %>%
  filter(year(observe_date) < fire_year)
fire_include_data = site_visit_potential %>%
  filter(year(observe_date) >= fire_year)

# Summarize number of selected sites
max_selected_number = max(site_visit_count$site_visits)
min_selected_number = min(site_visit_count$site_visits)
max_selected_indicator = site_visit_count %>%
  filter(site_visits == max_selected_number) %>%
  pull(indicator)
min_selected_indicator = site_visit_count %>%
  filter(site_visits == min_selected_number) %>%
  pull(indicator)
max_selected_indicators = ''
for (indicator in max_selected_indicator) {
  max_selected_indicators = paste(max_selected_indicators, indicator, sep = ', ')
}
max_selected_indicators = str_sub(max_selected_indicators, 3, -1)
min_selected_indicators = ''
for (indicator in min_selected_indicator) {
  min_selected_indicators = paste(min_selected_indicators, indicator, sep = ', ')
}
min_selected_indicators = str_sub(min_selected_indicators, 3, -1)

# Summarize selected projects
project_selected = site_visit_selected %>%
  distinct(project_code)

#### EXPORT SUMMARY DATA
####------------------------------

# Create export table
summary_data = tibble(project_total = nrow(project_data),
                      site_visit_total = nrow(site_visit_data),
                      public_percentage = round((nrow(site_visit_public)/nrow(site_visit_data)) * 100, 0),
                      public_number = nrow(site_visit_public),
                      original_visit_number = nrow(original_visit_data),
                      revisit_number = nrow(revisit_data),
                      vegetation_total = nrow(vegetation_observations),
                      potential_number = nrow(site_visit_potential),
                      fire_remove = nrow(fire_remove_data),
                      fire_include = nrow(fire_include_data),
                      other_omit = nrow(fire_include_data) - nrow(site_visit_selected),
                      project_selected = nrow(project_selected),
                      combined_selected = nrow(absence_data) + nrow(site_visit_selected),
                      absence_selected = nrow(absence_data),
                      site_visit_selected = nrow(site_visit_selected),
                      max_selected_number = max_selected_number,
                      max_selected_indicator = max_selected_indicators,
                      min_selected_number = min_selected_number,
                      min_selected_indicator = min_selected_indicators)
summary_data = summary_data %>%
  mutate_all(as.character) %>%
  pivot_longer(colnames(summary_data), names_to = 'characteristic', values_to = 'value')

# Export data to xlsx
sheets = list('summary' = summary_data)
write_xlsx(sheets, summary_output, format_headers = FALSE)

#### SUMMARIZE PROJECT METADATA
####------------------------------

# Summarize cover type
cover_type = vegetation_data %>%
  distinct(site_visit_code, cover_type)

# Summarize site visits per project
site_visit_summary = site_visit_data %>%
  inner_join(site_data, by = 'site_visit_code') %>%
  left_join(cover_type, by = 'site_visit_code') %>%
  group_by(project_code, perspective, cover_method, cover_type) %>%
  summarize(site_visit_count = n())

# Identify unique projects
project_list = site_visit_summary %>%
  distinct(project_code)
  

