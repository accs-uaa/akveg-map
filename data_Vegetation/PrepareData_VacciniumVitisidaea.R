# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Class Data - Vaccinium vitis-idaea
# Author: Timm Nawrocki
# Last Updated: 2021-03-15
# Usage: Must be executed in R 4.0.0+.
# Description: "Prepare Class Data - Vaccinium vitis-idaea" prepares the map class data for statistical modeling.
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
cover_file = paste(data_folder,
                     'species_data/cover_all.csv',
                     sep = '/')

# Import required libraries for geospatial processing: dplyr, readxl, stringr, and tidyr.
library(dplyr)
library(lubridate)
library(readxl)
library(stringr)
library(tidyr)

# Read site data and species data into dataframes
site_data = read.csv(site_file, fileEncoding = 'UTF-8')
cover_data = read.csv(cover_file, fileEncoding = 'UTF-8')

# Drop X column from site data
site_data = site_data %>%
  select(-X)

# Select columns and parse dates
cover_data = cover_data %>%
  mutate(veg_observe_date = ymd(veg_observe_date)) %>%
  mutate(year = year(veg_observe_date)) %>%
  mutate(day = yday(veg_observe_date)) %>%
  select(project, site_code, year, day, cover_type, name_accepted, genus, cover)

# Create table of site visit dates
site_visit = cover_data %>%
  select(site_code, year, day) %>%
  distinct()

#### CREATE PRESENCE DATA

# Filter the cover data to include only the map class
presence_data = cover_data %>%
  filter(name_accepted == 'Vaccinium vitis-idaea') %>%
  group_by(site_code, project, year, day, name_accepted, genus) %>%
  summarize(cover = max(cover))

# Sum multiple taxa to single summary
presence_data = presence_data %>%
  group_by(site_code, project, year, day) %>%
  summarize(cover = sum(cover)) %>%
  mutate(name_accepted = 'Vaccinium vitis-idaea') %>%
  mutate(genus = 'Vaccinium') %>%
  mutate(zero = ifelse(cover < 0.5, 0, 1))

#### CREATE ABSENCE DATA

# Remove presences from all sites to create observed absences
absence_observed = site_data %>%
  select(site_code, initial_project) %>%
  distinct() %>%
  anti_join(presence_data, by = 'site_code') %>%
  inner_join(site_visit, by = 'site_code') %>%
  rename(project = initial_project)

# Add synthetic absences
absence_synthetic = site_data %>%
  filter(initial_project == 'Lake Absences' |
           initial_project == 'Glacier Absences') %>%
  select(site_code, initial_project) %>%
  mutate(year = 9999) %>%
  mutate(day = 196) %>%
  rename(project = initial_project)
  
# Merge observed and synthetic absences
absence_data = rbind(absence_observed, absence_synthetic)

# Add map class information to absences
absence_data = absence_data %>%
  mutate(name_accepted = 'Vaccinium vitis-idaea') %>%
  mutate(genus = 'Vaccinium') %>%
  mutate(cover = 0) %>%
  mutate(zero = 0)

#### MERGE PRESENCES AND ABSENCES

# Bind rows from ground data
combined_data = bind_rows(presence_data, absence_data)

# Join site data to map class data
combined_data = combined_data %>%
  inner_join(site_data, by = 'site_code') %>%
  select(-initial_project)

# Control for aerial data, fire year, year, cover type, and project
map_class = combined_data %>%
  filter(perspective == 'ground' |
           perspective == 'generated' |
           (perspective == 'aerial' &
              cover >= 5)) %>%
  filter(year > fireYear) %>%
  filter(year >= 1994) %>%
  filter(cover_method != 'braun-blanquet visual estimate' |
           cover_method != 'custom classification visual estimate') %>%
  filter(project != 'AIM Fortymile') %>%
  filter(project != 'Bering LC') %>%
  filter(project != 'Breen Poplar') %>%
  filter(project != 'Katmai Bear') %>%
  filter(project != 'NPS ARCN Lichen') %>%
  filter(project != 'NPS CAKN Permafrost') %>%
  filter(project != 'NPS Denali LC') %>%
  filter(project != 'NPS Gates LC') %>%
  filter(project != 'NPS Yukon-Charley PA') %>%
  filter(project != 'Shell ONES Remote Sensing') %>%
  filter(project != 'USFWS Interior') %>%
  filter(project != 'USFWS SELA PA') %>%
  filter(project != 'USFWS Selawik LC') %>%
  filter(project != 'Wrangell LC')
  
# Remove NPS I&M Data for non-spruce species/groups
map_class = map_class %>%
  filter(project != 'NPS ARCN I&M') %>%
  filter(project != 'NPS CAKN I&M')

#### REMOVE INAPPROPRIATE SITES

# Identify sites that are inappropriate for the modeled class
remove_sites = cover_data %>%
  filter((name_accepted == 'Vaccinium' |
            name_accepted == 'Deciduous Shrub' |
            name_accepted == 'Coniferous Shrub' |
            name_accepted == 'Dwarf Shrub' |
            name_accepted == 'Shrub') &
           cover > 1) %>%
  distinct(site_code)

# Remove inappropriate sites from site data
map_class = map_class %>%
  anti_join(remove_sites, by = 'site_code')

#### EXPORT DATA

# Export map class data as csv
output_csv = paste(data_folder, 'species_data/mapClass_vacvit.csv', sep = '/')
write.csv(map_class, file = output_csv, fileEncoding = 'UTF-8')