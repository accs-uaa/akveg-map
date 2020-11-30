# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Class Data - Cladonia
# Author: Timm Nawrocki
# Last Updated: 2020-11-30
# Usage: Must be executed in R 4.0.0+.
# Description: "Prepare Class Data - Cladonia" prepares the map class data for statistical modeling.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Input',
                    sep = '/')

# Define input site and species data files
site_file = paste(data_folder,
                  'sites/sites_extracted.csv',
                  sep = '/')
species_file = paste(data_folder,
                     'species_data/akveg_CoverTotal.xlsx',
                     sep = '/')
date_file = paste(data_folder,
                  'sites/visit_date.xlsx',
                  sep = '/')
observation_sheet = 1

# Install required libraries if they are not already installed.
Required_Packages <- c('dplyr', 'readxl', 'stringr', 'tidyr')
New_Packages <- Required_Packages[!(Required_Packages %in% installed.packages()[,"Package"])]
if (length(New_Packages) > 0) {
  install.packages(New_Packages)
}
# Import required libraries for geospatial processing: dplyr, readxl, stringr, and tidyr.
library(dplyr)
library(readxl)
library(stringr)
library(tidyr)

# Read site data and species data into dataframes
site_data = read.csv(site_file, fileEncoding = 'UTF-8')
species_data = read_xlsx(species_file,
                         sheet = observation_sheet)
visit_date = read_xlsx(date_file,
                       sheet = observation_sheet)

#### CREATE PRESENCE DATA

# Clean unused columns from species data
species_data = species_data[c('siteCode', 'year', 'day', 'nameAdjudicated', 'nameAccepted',  'genus', 'coverTotal')]

# Filter the species data to include only the map class
presence_data = species_data %>%
  filter(genus == 'Cladonia' |
           genus == 'Cladina') %>%
  group_by(siteCode, year, day, nameAccepted, genus) %>%
  summarize(coverTotal = max(coverTotal))

# Sum multiple taxa to single summary
presence_data = presence_data %>%
  group_by(siteCode, year, day) %>%
  summarize(coverTotal = sum(coverTotal)) %>%
  mutate(nameAccepted = 'Cladonia') %>%
  mutate(genus = 'Cladonia') %>%
  mutate(regress = 1)

#### REMOVE INAPPROPRIATE GROUND SITES

# Identify sites that are inappropriate for the modeled class
remove_sites = species_data %>%
  filter(nameAccepted == 'Lichen' |
           nameAccepted == 'Fruticose Lichen') %>%
  filter(coverTotal >= 2)

# Remove inappropriate sites from site data
sites = site_data %>%
  anti_join(remove_sites, by = 'siteCode')

#### CREATE ABSENCE DATA

# Remove presences from all sites to create absence sites
absence_data = sites['siteCode'] %>%
  anti_join(presence_data, by = 'siteCode') %>%
  inner_join(visit_date, by = 'siteCode') %>%
  mutate(nameAccepted = 'Cladonia') %>%
  mutate(genus = 'Cladonia') %>%
  mutate(coverTotal = 0) %>%
  mutate(regress = 0)

#### MERGE PRESENCES AND ABSENCES

# Bind rows from ground data
combined_data = bind_rows(presence_data, absence_data)

# Join site data to map class
combined_data = combined_data %>%
  inner_join(site_data, by = 'siteCode')

# Add zero field
absences = combined_data %>%
  filter(coverType != 'aerial') %>%
  filter(coverTotal < 0.5) %>%
  mutate(zero = 0)
ground_presences = combined_data %>%
  filter(coverType != 'aerial') %>%
  filter(coverTotal >= 0.5) %>%
  mutate(zero = 1)
aerial_presences = combined_data %>%
  filter(coverType == 'aerial') %>%
  filter(coverTotal >= 5) %>%
  mutate(zero = 1)
map_class = bind_rows(absences, ground_presences, aerial_presences)

# Control for fire year, year, cover type, and project
map_class = map_class %>%
  filter(year > fireYear) %>%
  filter(year >= 2000) %>%
  filter(coverType != 'Braun-Blanquet Classification') %>%
  filter(initialProject != 'NPS CAKN Permafrost') %>%
  filter(initialProject != 'NPS YUCH PA') %>%
  filter(initialProject != 'Shell ONES Remote Sensing') %>%
  filter(initialProject != 'USFWS IRM') %>%
  filter(initialProject != 'Bering LC') %>%
  filter(initialProject != 'NPS Katmai LC') %>%
  filter(initialProject != 'Wrangell-St. Elias LC') %>%
  filter(initialProject != 'NPS Alagnak ELS') %>%
  filter(initialProject != 'NSSI LC')

# Remove project data inappropriate to map class
map_class = map_class %>%
  filter(initialProject != 'NPS ARCN I&M') %>%
  filter(initialProject != 'NPS CAKN I&M') %>%
  filter(initialProject != 'Dalton Earth Cover') %>%
  filter(initialProject != 'Goodnews Earth Cover') %>%
  filter(initialProject != 'Koyukuk Earth Cover') %>%
  filter(initialProject != 'Kvichak Earth Cover') %>%
  filter(initialProject != 'Naknek Earth Cover') %>%
  filter(initialProject != 'Northern Yukon Earth Cover') %>%
  filter(initialProject != 'Nowitna Earth Cover') %>%
  filter(initialProject != 'NPS Alagnak LC') %>%
  filter(initialProject != 'Seward Peninsula Earth Cover') %>%
  filter(initialProject != 'Southern Yukon Earth Cover') %>%
  filter(initialProject != 'Tetlin Earth Cover') %>%
  filter(initialProject != 'Yukon Delta Earth Cover')

# Export map class data as csv
output_csv = paste(data_folder, 'species_data/mapClass_cladon.csv', sep = '/')
write.csv(map_class, file = output_csv, fileEncoding = 'UTF-8')