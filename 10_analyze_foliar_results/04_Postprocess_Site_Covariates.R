# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Postprocess site covariates
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-04-07
# Usage: Script should be executed in R 4.3.2+.
# Description: "Postprocess site covariates" performs some basic post-processing on site visit data after covariates have been extracted.
# ---------------------------------------------------------------------------

# Import required libraries
library(dplyr)
library(fs)
library(lubridate)
library(readr)
library(stringr)
library(tibble)
library(tidyr)

# Set root directory
drive = 'C:'
root_folder = 'ACCS_Work'

# Define input folders
project_folder = path(drive,
                      root_folder,
                      'Projects/VegetationEcology/AKVEG_Map/Data/Data_Input')
output_folder = path(project_folder, 'ordination_data')

# Define input files
extract_input = path(output_folder, 'unprocessed/03_site_visit_extract_3338.csv')

# Define output files
extract_output = path(output_folder, '03_site_visit_extract_3338.csv')

# Format extracted data
extract_import = read_csv(extract_input)
extract_data = extract_import %>%
  select(-`system:index`, -`.geo`, -coast, -plt_dm_) %>%
  rename(prjct_cd = prjct_c,
         obs_date = obs_dat,
         data_tier = data_tr,
         scp_vasc = scp_vsc,
         scp_bryo = scp_bry,
         scp_lich = scp_lch,
         cvr_mthd = cvr_mth,
         coast = cst_dst,
         plt_rad_m = plt_rd_,
         strc_class = strc_cl,
         homogeneous = homogns,
         perspect = perspct,
         esa_type = esa_typ)
  
# Format site visit data
site_visit_data = extract_data %>%
  mutate(obs_year = year(obs_date),
         obs_month = month(obs_date),
         obs_day = day(obs_date)) %>%
  mutate(obs_year = case_when(prjct_cd == 'abr_arcticrefuge_2019' ~ as.numeric(str_sub(st_vst, start=-8, end=-5)),
                              TRUE ~ obs_year)) %>%
  mutate(obs_month = case_when(prjct_cd == 'abr_arcticrefuge_2019' ~ as.numeric(str_sub(st_vst, start=-4, end=-3)),
                               TRUE ~ obs_month)) %>%
  mutate(obs_day = case_when(prjct_cd == 'abr_arcticrefuge_2019' ~ as.numeric(str_sub(st_vst, start=-2, end=-1)),
                               TRUE ~ obs_day)) %>%
  mutate(obs_date = case_when(prjct_cd == 'abr_arcticrefuge_2019' ~ as.character(make_date(obs_year, obs_month, obs_day)),
                              TRUE ~ obs_date)) %>%
  select(st_vst, prjct_cd, st_code, data_tier, obs_date, obs_year, obs_month, obs_day, scp_vasc, scp_bryo, scp_lich,
         perspect, cvr_mthd, strc_class, homogeneous, plt_rad_m, lat_dd, long_dd, cent_x, cent_y,
         zone, valid, esa_type, fire_yr, january, summer, precip, coast, river, stream, wetness,
         aspect, elevation, exposure, heatload, position, relief, roughness, slope)

# Format spectral data
drop_columns = c('prjct_cd', 'st_code', 'data_tier', 'obs_date', 'scp_vasc', 'scp_bryo', 'scp_lich',
                 'perspect', 'cvr_mthd', 'strc_class', 'homogeneous', 'plt_rad_m', 'lat_dd', 'long_dd', 'cent_x', 'cent_y',
                 'zone', 'valid', 'esa_type', 'fire_yr', 'january', 'summer', 'precip', 'coast', 'river', 'stream', 'wetness',
                 'aspect', 'elevation', 'exposure', 'heatload', 'position', 'relief', 'roughness', 'slope')
spectral_data = extract_data %>%
  select(-one_of(drop_columns))

# Join final data
final_data = site_visit_data %>%
  left_join(spectral_data, by = 'st_vst') %>%
  arrange(prjct_cd, st_vst) %>%
  # Export data
  write.csv(., file = extract_output, fileEncoding = 'UTF-8', row.names = FALSE)
