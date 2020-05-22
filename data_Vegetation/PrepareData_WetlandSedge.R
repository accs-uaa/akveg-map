# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Class Data - Obligate Wetland Sedges
# Author: Timm Nawrocki
# Created on: 2020-05-16
# Usage: Must be executed in R 4.0.0+.
# Description: "Prepare Class Data - Obligate Wetland Sedges" prepares the map class data for statistical modeling.
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

#### FILTER SPECIES DATA

# Clean unused columns from species data
species_data = species_data[c('siteCode', 'year', 'day', 'nameAccepted', 'genus', 'coverTotal')]
# Filter out years prior to 2000
species_data = species_data %>%
  filter(year >= 2000)

# Filter the species data to include only the map class
presence_sites = species_data %>%
  filter(nameAccepted == 'Carex adelostoma' |
           nameAccepted == 'Carex aquatilis' |
           nameAccepted == 'Carex arcta' |
           nameAccepted == 'Carex bicolor' |
           nameAccepted == 'Carex chordorrhiza' |
           nameAccepted == 'Carex diandra' |
           nameAccepted == 'Carex echinata' |
           nameAccepted == 'Carex enanderi' |
           nameAccepted == 'Carex glareosa' |
           nameAccepted == 'Carex glareosa ssp. glareosa' |
           nameAccepted == 'Carex gynocrates' |
           nameAccepted == 'Carex holostoma' |
           nameAccepted == 'Carex interior' |
           nameAccepted == 'Carex kelloggii' |
           nameAccepted == 'Carex lachenalii' |
           nameAccepted == 'Carex lasiocarpa' |
           nameAccepted == 'Carex laxa' |
           nameAccepted == 'Carex leptalea' |
           nameAccepted == 'Carex limosa' |
           nameAccepted == 'Carex livida' |
           nameAccepted == 'Carex lyngbyei' |
           nameAccepted == 'Carex marina' |
           nameAccepted == 'Carex marina ssp. marina' |
           nameAccepted == 'Carex membranacea' |
           nameAccepted == 'Carex microglochin' |
           nameAccepted == 'Carex pauciflora' |
           nameAccepted == 'Carex paupercula' |
           nameAccepted == 'Carex pluriflora' |
           nameAccepted == 'Carex rariflora' |
           nameAccepted == 'Carex rostrata' |
           nameAccepted == 'Carex rotundata' |
           nameAccepted == 'Carex saxatilis' |
           nameAccepted == 'Carex saxatilis ssp. laxa' |
           nameAccepted == 'Carex sitchensis' |
           nameAccepted == 'Carex utriculata' |
           nameAccepted == 'Carex vaginata' |
           nameAccepted == 'Carex viridula ssp. viridula' |
           nameAccepted == 'Eriophorum angustifolium' |
           nameAccepted == 'Eriophorum chamissonis' |
           nameAccepted == 'Eriophorum gracile' |
           nameAccepted == 'Eriophorum russeolum' |
           nameAccepted == 'Eriophorum russeolum ssp. leiocarpum' |
           nameAccepted == 'Eriophorum scheuchzeri' |
           nameAccepted == 'Eriophorum triste' |
           nameAccepted == 'Eriophorum viridicarinatum') %>%
  group_by(siteCode, year, day, nameAccepted, genus) %>%
  summarize(coverTotal = max(coverTotal))

# Sum multiple taxa to single summary
presence_sites = presence_sites %>%
  group_by(siteCode, year, day) %>%
  summarize(coverTotal = sum(coverTotal)) %>%
  mutate(nameAccepted = 'Wetland Sedge') %>%
  mutate(genus = 'Wetland Sedge') %>%
  mutate(zero = 1)

#### REMOVE INAPPROPRIATE DATA

# Identify sites that are inappropriate for the modeled class
remove_sites = species_data %>%
  filter(nameAccepted == 'Carex' |
           nameAccepted == 'Eriophorum') %>%
  filter(coverTotal >= 2)
  
# Remove inappropriate sites from site data
site_data = site_data %>%
  # Remove inappropriate projects from site data
  filter(initialProject != 'NPS ARCN Lichen' &
           initialProject != 'NPS CAKN I&M' &
           initialProject != 'NPS ARCN I&M') %>%
  # Remove sites that are inappropriate for the modeled class
  anti_join(remove_sites, by = 'siteCode')

#### CREATE ABSENCE DATA

# Summarize date information from species data
date_data = unique(species_data[c('siteCode', 'year', 'day')])

# Remove presence sites from filtered sites to create absence sites
absence_sites = site_data['siteCode'] %>%
  anti_join(presence_sites, by = 'siteCode') %>%
  inner_join(date_data, by = 'siteCode') %>%
  mutate(nameAccepted = 'Wetland Sedge') %>%
  mutate(genus = 'Wetland Sedge') %>%
  mutate(coverTotal = 0) %>%
  mutate(zero = 0)

#### MERGE PRESENCE AND ABSENCE DATA

# Bind rows from presence sites and absence sites
map_class = bind_rows(presence_sites, absence_sites)

# Join site data
map_class = map_class %>%
  inner_join(site_data, by = 'siteCode')

# Export map class data as csv
output_csv = paste(data_folder, 'species_data/mapClass_WetlandSedge.csv', sep = '/')
write.csv(map_class, file = output_csv, fileEncoding = 'UTF-8')