# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compile Cover Data
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2021-03-09
# Usage: Script should be executed in R 4.0.0+.
# Description: "Compile Cover Data" merges cover data from the AKVEG, ABR, and NPS I&M databases into a single table.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input',
                    sep = '/')

# Define input cover data files
cover_abr_file = paste(data_folder,
                       'databaseABR/databaseABR_Cover.xlsx',
                       sep = '/')
cover_arcn_file = paste(data_folder,
                        'databaseNPSIM/picea/npsARCN_Picea_Cover.xlsx',
                        sep = '/')
cover_cakn_file = paste(data_folder,
                        'databaseNPSIM/picea/npsCAKN_Picea_Cover.xlsx',
                        sep = '/')

# Define sheet names
cover_sheet = 'cover'

# Define output file
output_cover = paste(data_folder,
                     'species_data/cover_all.csv',
                     sep = '/')

# Set repository directory
repository = 'C:/Users/timmn/Documents/Repositories/vegetation-plots-database'

# Import required libraries
library(dplyr)
library(readr)
library(readxl)
library(RPostgres)
library(stringr)
library(tibble)
library(tidyr)

# Import database connection function
connection_script = paste(repository,
                          'package_DataProcessing',
                          'connectDatabasePostGreSQL.R',
                          sep = '/')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = paste(drive,
                       root_folder,
                       'Administrative/Credentials/accs-postgresql/authentication_akveg.csv',
                       sep = '/')
database_connection = connect_database_postgresql(authentication)

# Define queries for AKVEG
query_adjudicated = 'SELECT * FROM taxon_adjudicated'
query_accepted = 'SELECT * FROM taxon_accepted'
query_hierarchy = 'SELECT * FROM hierarchy'
query_cover = 'SELECT cover.cover_id as cover_id
     , project.project_abbr as project
     , site.site_code as site_code
     , cover.veg_observe_date as veg_observe_date
     , veg_observer.personnel as veg_observer
     , veg_recorder.personnel as veg_recorder
     , cover_type.cover_type as cover_type
     , taxon_accepted.name_accepted as name_accepted
     , cover.cover as cover
FROM cover
    LEFT JOIN project ON cover.project_id = project.project_id
    LEFT JOIN site ON cover.site_id = site.site_id
    LEFT JOIN personnel veg_observer ON cover.veg_observer_id = veg_observer.personnel_id
    LEFT JOIN personnel veg_recorder ON cover.veg_recorder_id = veg_recorder.personnel_id
    LEFT JOIN cover_type ON cover.cover_type_id = cover_type.cover_type_id
    LEFT JOIN taxon_adjudicated ON cover.adjudicated_id = taxon_adjudicated.adjudicated_id
    LEFT JOIN taxon_accepted ON taxon_adjudicated.accepted_id = taxon_accepted.accepted_id
ORDER BY cover_id;'

# Read PostgreSQL taxonomy tables into dataframes
taxa_adjudicated = as_tibble(dbGetQuery(database_connection, query_adjudicated))
taxa_accepted = as_tibble(dbGetQuery(database_connection, query_accepted))
hierarchy = as_tibble(dbGetQuery(database_connection, query_hierarchy))

# Read and format PostgreSQL data tables into dataframes
cover_akveg = as_tibble(dbGetQuery(database_connection, query_cover))
cover_akveg = cover_akveg %>%
  # Remove cover_id
  select(-cover_id)

# Read and format cover data from ABR
cover_abr = read_xlsx(cover_abr_file, sheet = cover_sheet)
cover_abr = cover_abr %>%
  # Add accepted names
  left_join(taxa_adjudicated, by = 'name_adjudicated') %>%
  left_join(taxa_accepted, by = 'accepted_id') %>%
  select(project, site_code, veg_observe_date, veg_observer, veg_recorder, cover_type, name_accepted, cover)

# Read cover data from ARCN I&M
cover_arcn = read_xlsx(cover_arcn_file, sheet = cover_sheet)
cover_arcn = cover_arcn %>%
  # Add accepted names
  left_join(taxa_adjudicated, by = 'name_adjudicated') %>%
  left_join(taxa_accepted, by = 'accepted_id') %>%
  select(project, site_code, veg_observe_date, veg_observer, veg_recorder, cover_type, name_accepted, cover)

# Read cover data from CAKN I&M
cover_cakn = read_xlsx(cover_cakn_file, sheet = cover_sheet)
cover_cakn = cover_cakn %>%
  # Add accepted names
  left_join(taxa_adjudicated, by = 'name_adjudicated') %>%
  left_join(taxa_accepted, by = 'accepted_id') %>%
  select(project, site_code, veg_observe_date, veg_observer, veg_recorder, cover_type, name_accepted, cover)

# Merge cover table
cover_data = rbind(cover_akveg, cover_abr, cover_arcn, cover_cakn)
cover_data = cover_data %>%
  # Correct values greater than 100%
  mutate(cover = ifelse(cover > 100, 100, cover)) %>%
  # Add accepted genus
  left_join(taxa_accepted, by = 'name_accepted') %>%
  left_join(hierarchy, by = 'hierarchy_id') %>%
  rename(genus = genus_accepted) %>%
  select(project, site_code, veg_observe_date, veg_observer, veg_recorder, cover_type, name_accepted, genus, cover)

# Export data
write.csv(cover_data, file = output_cover, fileEncoding = 'UTF-8', row.names = FALSE)