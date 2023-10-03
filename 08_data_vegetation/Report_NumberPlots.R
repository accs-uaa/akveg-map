# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Report Number of Available Plots
# Author: Timm Nawrocki
# Last Updated: 2021-04-02
# Usage: Must be executed in R 4.0.0+.
# Description: "Report Number of Available Plots" finds the number of plots from merged data sources between a specified year range.
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

# Join site data to cover data
combined_data = cover_data %>%
  inner_join(site_data, by = 'site_code') %>%
  select(-initial_project)

# Control for year, method, and target groups
plots_general = combined_data %>%
  filter(perspective == 'ground' |
           perspective == 'aerial') %>%
  filter(year >= 2000 &
           year <= 2019) %>%
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
  filter(project != 'Wrangell LC') %>%
  filter(project != 'NPS ARCN I&M') %>%
  filter(project != 'NPS CAKN I&M') %>%
  select(site_code, project, year, day) %>%
  distinct()

plots_spruce = combined_data %>%
  filter(perspective == 'ground' |
           perspective == 'aerial') %>%
  filter(year >= 2000 &
           year <= 2019) %>%
  filter(project == 'NPS ARCN I&M' |
           project == 'NPS CAKN I&M') %>%
  select(site_code, project, year, day) %>%
  distinct()

#### COUNT DISTINCT SITE TOTALS

# Count number of sites
number_general = nrow(plots_general)
number_spruce = nrow(plots_spruce)

# Print number of sites
print(number_general)
print(number_spruce)

#### SUMMARIZE DISTINCT SITES BY PROJECT
projects_general = plots_general %>%
  group_by(project) %>%
  summarize(num_sites = n())
projects_spruce = plots_spruce %>%
  group_by(project) %>%
  summarize(num_sites = n())
