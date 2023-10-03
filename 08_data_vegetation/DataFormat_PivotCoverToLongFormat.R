# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Pivot Grid-Point Intercept Cover Data to Long Format
# Author: Timm Nawrocki
# Last Updated: 2020-04-30
# Usage: Should be executed in R 3.6.1+.
# Description: "Pivot Grid-Point Intercept Cover Data to Long Format" transforms the cover data table from the grid point intercept data entry form to contain a single taxon observation per row. In the resulting table, each row represents a single site-line-point-layer.
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
cover_file = "N:\\ACCS_Work\\Projects\\VegetationEcology\\AKVEG_PlotsDatabase\\vegetationPlots\\18_accsRibdon_2019\\source\\2019_RibdonRiver_Data.xlsx"
output_file = "N:\\ACCS_Work\\Projects\\VegetationEcology\\AKVEG_PlotsDatabase\\vegetationPlots\\18_accsRibdon_2019\\source\\2019_RibdonRiver_CoverLongForm.xlsx"
cover_sheet = 2
layers = c("Layer01", "Layer02", "Layer03", "Layer04", "Layer05", "Layer06", "Layer07", "Layer08", "Layer09", "Layer10")

# Read cover data from excel
cover_data = read_xlsx(cover_file,
                       sheet = cover_sheet)

# Transform cover data
cover_data_long = cover_data %>%
  pivot_longer(cols = layers, names_to = "Layer") %>%
  drop_na() %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer01"), 1)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer02"), 2)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer03"), 3)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer04"), 4)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer05"), 5)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer06"), 6)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer07"), 7)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer08"), 8)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer09"), 9)) %>%
  mutate(Layer=replace(Layer, which(Layer == "Layer10"), 10)) %>%
  rename(Abbreviation = value)

# Convert layer to integer
cover_data_long$Layer = as.integer(cover_data_long$Layer)

# Export long format data as a new excel file
write_xlsx(cover_data_long,
           path = output_file)