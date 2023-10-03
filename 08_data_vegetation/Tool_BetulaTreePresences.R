# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Export Betula tree presences
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2021-03-09
# Usage: Script should be executed in R 4.0.0+.
# Description: "Export Betula tree presences" joins cover and site tables to get all sites for which Betula neoalaskana or Betula kenaica were present.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folder
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input',
                    sep = '/')

# Define input files
cover_file = paste(data_folder,
                   'species_data/cover_all.csv',
                   sep = '/')
site_file = paste(data_folder,
                   'sites/sites_all.csv',
                   sep = '/')

# Define output file
output_csv = paste(data_folder,
                   'species_data/cover_all_bettre.csv',
                   sep = '/')

# Import required libraries
library(dplyr)
library(readr)
library(readxl)
library(RPostgres)
library(stringr)
library(tibble)
library(tidyr)

# Read input files into data frames
cover_data = read.csv(cover_file, fileEncoding = 'UTF-8')
site_data = read.csv(site_file, fileEncoding = 'UTF-8')

# Join site data to cover data and filter to Betula trees
cover_data = cover_data %>%
  left_join(site_data, by = 'site_code') %>%
  filter(name_accepted == 'Betula neoalaskana' |
           name_accepted == 'Betula kenaica') %>%
  drop_na(latitude) %>%
  select(-site_id)

# Export data
write.csv(cover_data, file = output_csv, fileEncoding = 'UTF-8')