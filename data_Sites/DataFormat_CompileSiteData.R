# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compile Site Data
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2021-03-09
# Usage: Script should be executed in R 4.0.0+.
# Description: "Compile Site Data" merges site data from the AKVEG, ABR, and NPS I&M databases into a single table.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input',
                    sep = '/')

# Define input site data files
site_abr_file = paste(data_folder,
                      'databaseABR/databaseABR_Site.xlsx',
                      sep = '/')
site_arcn_file = paste(data_folder,
                       'databaseNPSIM/picea/npsARCN_Site.xlsx',
                       sep = '/')
site_cakn_file = paste(data_folder,
                       'databaseNPSIM/picea/npsCAKN_Site.xlsx',
                       sep = '/')

# Define sheet names
site_sheet = 'site'

# Define output file
output_site = paste(data_folder,
                    'sites/sites_all.csv',
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
query_site = 'SELECT site.site_id as site_id
     , site.site_code as site_code
     , project.project_abbr as initial_project
     , perspective.perspective as perspective
     , cover_method.cover_method as cover_method
     , scope_vascular.scope as scope_vascular
     , scope_bryophyte.scope as scope_bryophyte
     , scope_lichen.scope as scope_lichen
     , plot_dimensions.plot_dimensions as plot_dimensions
     , datum.datum as datum
     , site.latitude as latitude
     , site.longitude as longitude
     , site.error as error
FROM site
    LEFT JOIN project ON site.project_id = project.project_id
    LEFT JOIN perspective ON site.perspective_id = perspective.perspective_id
    LEFT JOIN cover_method ON site.cover_method_id = cover_method.cover_method_id
    LEFT JOIN scope scope_vascular ON site.scope_vascular_id = scope_vascular.scope_id
    LEFT JOIN scope scope_bryophyte ON site.scope_bryophyte_id = scope_bryophyte.scope_id
    LEFT JOIN scope scope_lichen ON site.scope_lichen_id = scope_lichen.scope_id
    LEFT JOIN plot_dimensions ON site.plot_dimensions_id = plot_dimensions.plot_dimensions_id
    LEFT JOIN datum ON site.datum_id = datum.datum_id
ORDER BY site_id;'

# Read and format PostgreSQL data tables into dataframes
site_akveg = as_tibble(dbGetQuery(database_connection, query_site))

# Read and format site data from ABR
site_abr = read_xlsx(site_abr_file, sheet = site_sheet)
site_abr = site_abr %>%
  # Assume standard 10 m radius plot type for unknown dimensions
  mutate(plot_dimensions = ifelse(plot_dimensions == 'unknown', '10 radius', plot_dimensions))

# Read site data from ARCN I&M
site_arcn = read_xlsx(site_arcn_file, sheet = site_sheet)

# Read site data from CAKN I&M
site_cakn = read_xlsx(site_cakn_file, sheet = site_sheet)

# Merge site table
site_data = rbind(site_akveg, site_abr, site_arcn, site_cakn)
site_data = site_data %>%
  select(-site_id)

# Export data
write.csv(site_data, file = output_site, fileEncoding = 'UTF-8', row.names = FALSE)