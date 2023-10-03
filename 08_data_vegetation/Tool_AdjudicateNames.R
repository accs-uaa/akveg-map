# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Adjudicate names for foliar cover observations
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2021-01-29
# Usage: Script should be executed in R 4.0.0+.
# Description: "Adjudicate names for foliar cover observations" joins the adjudicated names to the original names. A manual review is required after running this script to apply names that could not be automatically adjudicated.
# ---------------------------------------------------------------------------

# Set target name
target_paths = c('databaseABR')

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folder
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input',
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
                          'connectDatabasePostgreSQL.R',
                          sep = '/')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = paste(drive,
                       root_folder,
                       'Administrative/Credentials/accs-postgresql/authentication_akveg.csv',
                       sep = '/')
database_connection = connect_database_postgresql(authentication)

# Read constraints into data frames from AKVEG
query_taxa = 'SELECT * FROM taxon_adjudicated'
taxa_data = as_tibble(dbGetQuery(database_connection, query_taxa))

# Iterate through target paths and produce output insert statements
for (target_path in target_paths) {
  # Parse target name into sequence and name
  project_name = substr(target_path, start = 1, stop = str_length(target_path))
  
  # Designate input file
  input_file = paste(project_name,
                     '_Cover.xlsx',
                     sep = '')
  input_file = paste(data_folder,
                     target_path,
                     input_file,
                     sep = '/')
  
  # Designate output csv file
  output_csv = 'cover_adjudicated.csv'
  output_csv = paste(data_folder,
                     target_path,
                     output_csv,
                     sep = '/')
  
  # Read input data into dataframe
  input_data = read_excel(input_file, sheet = 'cover')

  # Select necessary columns from the adjudicated names
  taxa_data = taxa_data %>%
    select(adjudicated_id, name_adjudicated)

  # Join adjudicated names to observation data
  observation_data = input_data %>%
    select(project, site_code, veg_observe_date, veg_observer, veg_recorder, cover_type, name_original, name_check, cover) %>%
    left_join(taxa_data, by = c('name_check' = 'name_adjudicated')) %>%
    left_join(taxa_data, by = 'adjudicated_id') %>%
    select(project, site_code, veg_observe_date, veg_observer, veg_recorder, cover_type, name_original, name_check, name_adjudicated, cover)

  # Export the adjudicated observations
  write.csv(observation_data, file = output_csv, fileEncoding = 'UTF-8', row.names = FALSE)
}