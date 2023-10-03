# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate Total (Any-hit) Foliar Cover
# Author: Timm Nawrocki
# Last Updated: 2020-05-01
# Usage: Should be executed in R 3.6.1+.
# Description: "Calculate Total (Any-hit) Foliar Cover" calculates total foliar cover (any-hit cover sensu Karl et al. 2017) from a long format observation table stored as an excel file. The long format observation table should be produced using the "Pivot Grid-Point Intercept Cover Data to Long Format" script.
# ---------------------------------------------------------------------------

# Install required libraries if they are not already installed.
Required_Packages <- c("dplyr", "readxl", "writexl", "tidyr")
New_Packages <- Required_Packages[!(Required_Packages %in% installed.packages()[,"Package"])]
if (length(New_Packages) > 0) {
  install.packages(New_Packages)
}
# Import required libraries.
library(dplyr)
library(readxl)
library(writexl)
library(tidyr)

# Define excel file and sheet containing cover data
observation_file = "N:\\ACCS_Work\\Projects\\VegetationEcology\\AKVEG_PlotsDatabase\\vegetationPlots\\18_accsRibdon_2019\\source\\2019_RibdonRiver_CoverLongForm.xlsx"
output_file = "N:\\ACCS_Work\\Projects\\VegetationEcology\\AKVEG_PlotsDatabase\\vegetationPlots\\18_accsRibdon_2019\\accsRibdon_2019_CoverTotal.xlsx"
observation_sheet = 1

# Read cover data from excel
observation_data = read_xlsx(observation_file,
                             sheet = observation_sheet)

# Summarize data by site and taxon
total_cover = observation_data %>%
  group_by(Site, Observation) %>%
  summarize(coverTotal = n()) %>%
  rename(siteCode = Site) %>%
  rename(nameOriginal = Observation) %>%
  mutate(coverTotal = round((coverTotal/150)*100, digits = 1))

# Export cover data as a new excel file
write_xlsx(total_cover,
           path = output_file)