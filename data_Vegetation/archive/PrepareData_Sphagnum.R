# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Class Data - Sphagnum
# Author: Timm Nawrocki
# Created on: 2020-05-25
# Usage: Must be executed in R 4.0.0+.
# Description: "Prepare Class Data - Sphagnum" prepares the map class data for statistical modeling.
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

# Parse site data into ground sites and aerial sites
ground_sites = site_data %>%
  filter(coverType != 'aerial')
aerial_sites = site_data %>%
  filter(coverType == 'aerial')

#### CREATE PRESENCE DATA

# Clean unused columns from species data
species_data = species_data[c('siteCode', 'year', 'day', 'nameAccepted', 'genus', 'coverTotal')]

# Filter the species data to include only the map class
presence_data = species_data %>%
  filter(genus == 'Sphagnum') %>%
  group_by(siteCode, year, day, nameAccepted, genus) %>%
  summarize(coverTotal = max(coverTotal))

# Sum multiple taxa to single summary
presence_data = presence_data %>%
  group_by(siteCode, year, day) %>%
  summarize(coverTotal = sum(coverTotal)) %>%
  mutate(nameAccepted = 'Sphagnum') %>%
  mutate(genus = 'Sphagnum') %>%
  mutate(zero = 1)

#### SPLIT PRESENCE DATA INTO GROUND AND AERIAL

ground_presences = presence_data %>%
  anti_join(aerial_sites, by = 'siteCode')

aerial_presences = presence_data %>%
  anti_join(ground_sites, by = 'siteCode') %>%
  filter(coverTotal > 5)

#### REMOVE INAPPROPRIATE GROUND SITES

# Identify sites that are inappropriate for the modeled class
remove_sites = ground_presences %>%
  filter(nameAccepted == 'Moss') %>%
  filter(coverTotal >= 2)

# Remove inappropriate sites from site data
ground_sites = ground_sites %>%
  filter(initialProject != 'NPS ARCN Lichen' &
           initialProject != 'NPS CAKN I&M' &
           initialProject != 'NPS ARCN I&M') %>%
  # Remove site that are inappropriate for the modeled class
  anti_join(remove_sites, by = 'siteCode')

#### CREATE GROUND ABSENCES

# Remove ground presences from filtered sites to create absence sites
ground_absences = ground_sites['siteCode'] %>%
  anti_join(ground_presences, by = 'siteCode') %>%
  inner_join(visit_date, by = 'siteCode') %>%
  mutate(nameAccepted = 'Sphagnum') %>%
  mutate(genus = 'Sphagnum') %>%
  mutate(coverTotal = 0) %>%
  mutate(zero = 0)

#### MERGE GROUND PRESENCES AND GROUND ABSENCES

# Bind rows from ground data
ground_data = bind_rows(ground_presences, ground_absences)

# Join ground data to ground sites
ground_data = ground_data %>%
  inner_join(ground_sites, by = 'siteCode')

#### MERGE GROUND DATA AND AERIAL DATA

aerial_data = aerial_presences %>%
  inner_join(aerial_sites, by = 'siteCode')

# Bind rows from ground and aerial data
map_class = bind_rows(ground_data, aerial_data)

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
  filter(initialProject != 'Wrangell-St. Elias LC')

# Export map class data as csv
output_csv = paste(data_folder, 'species_data/mapClass_Sphagnum.csv', sep = '/')
write.csv(map_class, file = output_csv, fileEncoding = 'UTF-8')