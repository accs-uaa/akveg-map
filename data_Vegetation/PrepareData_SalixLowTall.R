# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Class Data - Salix Low-Tall Shrubs
# Author: Timm Nawrocki
# Created on: 2020-05-25
# Usage: Must be executed in R 4.0.0+.
# Description: "Prepare Class Data - Salix Low-Tall Shrubs" prepares the map class data for statistical modeling.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
data_folder = paste(drive,
                    root_folder,
                    'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input',
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
  filter(nameAccepted == 'Salix alaxensis' |
           nameAccepted == 'Salix alaxensis var. alaxensis' |
           nameAccepted == 'Salix alaxensis var. longistylus' |
           nameAccepted == 'Salix arbusculoides' |
           nameAccepted == 'Salix athabascensis' |
           nameAccepted == 'Salix barclayi' |
           nameAccepted == 'Salix barrattiana' |
           nameAccepted == 'Salix bebbiana' |
           nameAccepted == 'Salix candida' |
           nameAccepted == 'Salix commutata' |
           nameAccepted == 'Salix glauca' |
           nameAccepted == 'Salix glauca ssp. acutifolia' |
           nameAccepted == 'Salix glauca ssp. stipulifera' |
           nameAccepted == 'Salix hastata' |
           nameAccepted == 'Salix hookeriana' |
           nameAccepted == 'Salix interior' |
           nameAccepted == 'Salix lasiandra' |
           nameAccepted == 'Salix lasiandra var. caudata' |
           nameAccepted == 'Salix lasiandra var. lasiandra' |
           nameAccepted == 'Salix myrtillifolia' |
           nameAccepted == 'Salix niphoclada' |
           nameAccepted == 'Salix planifolia' |
           nameAccepted == 'Salix pseudomonticola' |
           nameAccepted == 'Salix pseudomyrsinites' |
           nameAccepted == 'Salix pulchra' |
           nameAccepted == 'Salix richardsonii' |
           nameAccepted == 'Salix scouleriana' |
           nameAccepted == 'Salix sitchensis') %>%
  group_by(siteCode, year, day, nameAccepted, genus) %>%
  summarize(coverTotal = max(coverTotal))

# Sum multiple taxa to single summary
presence_data = presence_data %>%
  group_by(siteCode, year, day) %>%
  summarize(coverTotal = sum(coverTotal)) %>%
  mutate(nameAccepted = 'Salix Low-Tall') %>%
  mutate(genus = 'Salix') %>%
  mutate(regress = 1)

#### REMOVE INAPPROPRIATE GROUND SITES

# Identify sites that are inappropriate for the modeled class
remove_sites = species_data %>%
  filter(nameAccepted == 'Salix')

# Remove inappropriate sites from site data
sites = site_data %>%
  anti_join(remove_sites, by = 'siteCode')

#### CREATE ABSENCE DATA

# Remove presences from all sites to create absence sites
absence_data = sites['siteCode'] %>%
  anti_join(presence_data, by = 'siteCode') %>%
  inner_join(visit_date, by = 'siteCode') %>%
  mutate(nameAccepted = 'Salix Low-Tall') %>%
  mutate(genus = 'Salix') %>%
  mutate(coverTotal = 0) %>%
  mutate(regress = 0)

#### MERGE PRESENCES AND ABSENCES

# Bind rows from ground data
combined_data = bind_rows(presence_data, absence_data)

# Join site data to map class
combined_data = combined_data %>%
  inner_join(site_data, by = 'siteCode')

# Add zero field to ground data
absences = combined_data %>%
  filter(coverType != 'aerial') %>%
  filter(coverTotal < 0.5) %>%
  mutate(zero = 0)
ground_presences = combined_data %>%
  filter(coverType != 'aerial') %>%
  filter(coverTotal >= 0.5) %>%
  mutate(zero = 1)

# Filter appropriate species presences for aerial sites
aerial_data = species_data %>%
  filter(nameAccepted == 'Salix alaxensis' |
           nameAccepted == 'Salix alaxensis var. alaxensis' |
           nameAccepted == 'Salix alaxensis var. longistylus' |
           nameAccepted == 'Salix arbusculoides' |
           nameAccepted == 'Salix athabascensis' |
           nameAccepted == 'Salix barclayi' |
           nameAccepted == 'Salix barrattiana' |
           nameAccepted == 'Salix bebbiana' |
           nameAccepted == 'Salix candida' |
           nameAccepted == 'Salix commutata' |
           nameAccepted == 'Salix glauca' |
           nameAccepted == 'Salix glauca ssp. acutifolia' |
           nameAccepted == 'Salix glauca ssp. stipulifera' |
           nameAccepted == 'Salix hastata' |
           nameAccepted == 'Salix hookeriana' |
           nameAccepted == 'Salix interior' |
           nameAccepted == 'Salix lasiandra' |
           nameAccepted == 'Salix lasiandra var. caudata' |
           nameAccepted == 'Salix lasiandra var. lasiandra' |
           nameAccepted == 'Salix myrtillifolia' |
           nameAccepted == 'Salix niphoclada' |
           nameAccepted == 'Salix planifolia' |
           nameAccepted == 'Salix pseudomonticola' |
           nameAccepted == 'Salix pseudomyrsinites' |
           nameAccepted == 'Salix pulchra' |
           nameAccepted == 'Salix richardsonii' |
           nameAccepted == 'Salix scouleriana' |
           nameAccepted == 'Salix sitchensis' |
           nameAccepted == 'Salix') %>%
  group_by(siteCode, year, day, nameAccepted, genus) %>%
  summarize(coverTotal = max(coverTotal))

# Sum multiple taxa to single summary
aerial_data = aerial_data %>%
  group_by(siteCode, year, day) %>%
  summarize(coverTotal = sum(coverTotal)) %>%
  mutate(nameAccepted = 'Salix Low-Tall') %>%
  mutate(genus = 'Salix') %>%
  mutate(regress = 1)

# Join site data to aerial data
aerial_data = aerial_data %>%
  inner_join(site_data, by = 'siteCode')

# Filter aerial presences
aerial_presences = aerial_data %>%
  filter(coverType == 'aerial') %>%
  filter(coverTotal >= 5) %>%
  mutate(zero = 1)

# Bind all data into map class
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
  filter(initialProject != 'NPS ARCN Lichen') %>%
  filter(initialProject != 'NPS ARCN I&M') %>%
  filter(initialProject != 'NPS CAKN I&M')

# Export map class data as csv
output_csv = paste(data_folder, 'species_data/mapClass_salshr.csv', sep = '/')
write.csv(map_class, file = output_csv, fileEncoding = 'UTF-8')