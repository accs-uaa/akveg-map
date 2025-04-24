# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Comparison of mapped foliar cover to ordination for Nelchina Basin
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-04-23
# Usage: Script should be executed in R 4.4.3+.
# Description: "Comparison of mapped foliar cover to ordination for Nelchina Basin" creates a 3-axis NMDS ordination of plant community composition data collected above treeline in the Nelchina Basin in 2022 & 2023 and models the deviance explained across the three ordination axes by the cross-validation results of the foliar cover maps.
# ---------------------------------------------------------------------------

# Import required libraries
library(dplyr)
library(fs)
library(ggplot2)
library(metR)
library(janitor)
library(lubridate)
library(readr)
library(writexl)
library(stringr)
library(tibble)
library(tidyr)
library(vegan)
library(vegan3d)
library(vegclust)
library(rgl)
library(indicspecies)
library(viridis)

#### SET UP DIRECTORIES AND FILES
####------------------------------

# Set random seed
set.seed(314)

# Set root directory (modify to your folder structure)
drive = 'C:'
root_folder = 'ACCS_Work'

# Define input folders (modify to your folder structure)
project_folder = path(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
input_folder = path(project_folder, 'Data_Input/ordination_data')
results_folder = path(project_folder, 'Data_Output/model_results')

# Define input files
site_visit_input = path(input_folder, '03_site_visit_extract_3338.csv')
vegetation_input = path(input_folder, '05_vegetation.csv')

# Define model lists
lgbm_list = c('alnus', 'betshr', 'bettre', 'brotre', 'erivag', 'mwcalama', 'ndsalix',
              'picgla', 'picmar', 'populbt', 'rhoshr', 'sphagn', 'vaculi', 'wetsed')
lgbmnc_list = c('dryas', 'dsalix', 'empnig', 'nerishr', 'poptre', 'tsumer')
rf_list = c('picsit', 'rubspe', 'vacvit')
combined_list = c(lgbm_list, lgbmnc_list, rf_list)

#### FORMAT DATA
####------------------------------

# Read site visit data
site_data = read_csv(site_visit_input)

# Sites with valid vegetation cover data
veg_sites = read_csv(vegetation_input) %>%
  distinct(st_vst)
missing_data = site_data %>%
  anti_join(veg_sites, by = 'st_vst')

# Remove sites with missing data
site_data = site_data %>%
  anti_join(missing_data, by = 'st_vst')

# Read data frame of combined results
for (target in combined_list) {
  # Set input file
  if (target %in% lgbm_list) {
    results_input = path(results_folder, 'round_20241124', target, paste(target, '_results.csv', sep = ''))
  } else if (target %in% lgbmnc_list) {
    results_input = path(results_folder, 'round_20241129', target, paste(target, '_results.csv', sep = ''))
  } else if (target %in% rf_list) {
    results_input = path(results_folder, 'round_20241204_rf', target, paste(target, '_results.csv', sep = ''))
  } else {
    print(paste('ERROR: ', target, ' is not an available result.', sep = ''))
    quit()
  }
  
  # Read results
  results_data = read_csv(results_input) %>%
    select(st_vst, prediction) %>%
    rename(!!target := prediction)
  
  # Left join results to site data
  site_data = site_data %>%
    left_join(results_data, by = 'st_vst')
}

# Omit canyon plot (430)
omit_plots = c('NLC_430_20230723')

# Select site visit data appropriate for ordination
ordination_data = site_data %>%
  filter(prjct_cd == 'accs_nelchina_2023') %>%
  filter(!st_vst %in% omit_plots) %>%
  select(st_vst, perspect, zone, alnus, betshr, bettre, brotre, dryas, dsalix, empnig, erivag,
         mwcalama, ndsalix, nerishr, picgla, picmar, picsit, poptre, populbt, rhoshr, rubspe,
         sphagn, tsumer, vaculi, vacvit, wetsed) %>%
  filter(perspect == 'ground') %>%
  drop_na() %>%
  arrange(st_vst)
ordination_sites = ordination_data %>%
  distinct(st_vst)

# Read data into dataframes
vegetation_data = read_csv(vegetation_input) %>%
  right_join(ordination_sites) %>%
  # Standardize taxa
  mutate(name_accepted = case_when(code_accepted == 'betnan' ~ 'Betula nana ssp. exilis',
                                   code_accepted == 'calthpal' ~ 'Caltha palustris ssp. radicans',
                                   code_accepted == 'camlas' ~ 'Campanula lasiocarpa ssp. latisepala',
                                   code_accepted == 'dryaja' ~ 'Dryas ajanensis ssp. beringensis',
                                   code_accepted == 'rhotom' ~ 'Rhododendron tomentosum ssp. decumbens',
                                   TRUE ~ name_accepted)) %>%
  mutate(code_accepted = case_when(code_accepted == 'betnan' ~ 'betnansexi',
                                   code_accepted == 'calthpal' ~ 'calpalsrad',
                                   code_accepted == 'camlas' ~ 'camlasslat',
                                   code_accepted == 'dryaja' ~ 'dryajasber',
                                   code_accepted == 'rhotom' ~ 'rhotomsdec',
                                   TRUE ~ code_accepted)) %>%
  # Convert dead vegetation to unique names
  mutate(taxon_code = case_when(dead_status == TRUE ~ paste(code_accepted, 'dead', sep='#'),
                                TRUE ~ code_accepted)) %>%
  # Convert trace values to 0.1%
  mutate(cvr_pct = case_when(cvr_pct == 0 ~ 0.1,
                             TRUE ~ cvr_pct)) %>%
  # Ensure no duplicate records from name changes
  group_by(st_vst, code_accepted, name_accepted, dead_status, cvr_type, taxon_code) %>%
  summarize(cvr_pct = sum(cvr_pct)) %>%
  # Round cover values to nearest 0.1%
  mutate(cvr_pct = round(cvr_pct, 1)) %>%
  # Omit plots
  filter(!st_vst %in% omit_plots) %>%
  # Order by site visit
  arrange(st_vst) %>%
  # Ungroup data
  ungroup()

# Convert vegetation data to matrix
vegetation_matrix = vegetation_data %>%
  # Convert to wide format
  select(st_vst, taxon_code, cvr_pct) %>%
  pivot_wider(names_from = taxon_code, values_from = cvr_pct) %>%
  # Convert NA values to zero
  replace(is.na(.), 0) %>%
  # Convert st_vst column to row names
  column_to_rownames(var='st_vst')

#### CONDUCT ORDINATION
####------------------------------

# Normalize vegetation matrix
vegetation_normalized = decostand(vegetation_matrix, method='normalize')

# Calculate bray dissimilarity on normalized vegetation matrix
bray_normalized = vegdist(vegetation_normalized, method="bray")

# Calculate NMDS ordination on dissimilarity matrix
nmds_normalized = metaMDS(bray_normalized,
                          distance = "bray",
                          k = 3,
                          maxit = 50, 
                          trymax = 100,
                          wascores = TRUE)

# Compare stress plots
stressplot(nmds_normalized, main="Stress Plot for Normalized Cover/Bray-Curtis")

# Assign scores from NMDS axes
analysis_data = ordination_data %>%
  mutate(nmds_axis_1 = scores(nmds_normalized, display = "sites")[, 1]) %>%
  mutate(nmds_axis_2 = scores(nmds_normalized, display = "sites")[, 2]) %>%
  mutate(nmds_axis_3 = scores(nmds_normalized, display = "sites")[, 3])

# Calculate a multivariate GAM to model the NMDS axes from the foliar cover cross-validation results
library(mgcv)
gam_all = gam(list(nmds_axis_1 ~ s(betshr) + s(dryas) + s(dsalix) + s(empnig) + s(mwcalama) + s(ndsalix) + s(nerishr) + s(rhoshr) + s(sphagn) + s(vaculi) + s(vacvit) + s(wetsed),
                   nmds_axis_2 ~ s(betshr) + s(dryas) + s(dsalix) + s(empnig) + s(mwcalama) + s(ndsalix) + s(nerishr) + s(rhoshr) + s(sphagn) + s(vaculi) + s(vacvit) + s(wetsed),
                   nmds_axis_3 ~ s(betshr) + s(dryas) + s(dsalix) + s(empnig) + s(mwcalama) + s(ndsalix) + s(nerishr) + s(rhoshr) + s(sphagn) + s(vaculi) + s(vacvit) + s(wetsed)),
    data = analysis_data, family = mvn(d = 3))
summary(gam_all)