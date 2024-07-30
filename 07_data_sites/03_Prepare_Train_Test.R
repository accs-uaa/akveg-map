# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare taxa presence-absence data
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2024-07-29
# Usage: Script should be executed in R 4.3.2+.
# Description: "Prepare taxa presence-absence data" prepares train/test data for each target species.
# ---------------------------------------------------------------------------

# Import required libraries
library(dplyr)
library(fs)
library(janitor)
library(lubridate)
library(openxlsx)
library(readr)
library(readxl)
library(RPostgres)
library(rvest)
library(sf)
library(stringr)
library(tibble)
library(tidyr)

# Set root directory
drive = 'D:'
root_folder = 'ACCS_Work'

# Set repository directory
akveg_repository = path('C:', root_folder, 'Repositories/akveg-database')
sdm_repository = path('C:', root_folder, 'Repositories/north-pacific-sdm')
credentials_folder = path('C:', root_folder, 'Credentials/akveg_private_read')

# Define input folders
project_folder = path(drive, root_folder,
                      'Projects/Botany/NPS_NorthPacificSteppingStones',
                      'Data/Data_Input')

# Define input files
zone_input = path(project_folder, 'region_data', 'AlaskaYukon_MapDomain_3338.shp')
atka_input = path(project_folder, 'collection_data', 'Atka_2019.xlsx')
dechaine_input = path(project_folder, 'collection_data', 'SBHP_Location_Data.xlsx')
rare_input = path(project_folder, 'collection_data', 'RarePlant_Dataset_Apr2024.xlsx')

# Define project geodatabase and absence layer
project_geodatabase = path(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data/AKVEG_Map.gdb')
absence_layer = path('AlaskaYukon_Absences_3338')

# Define output files
sites_output = path(project_folder, 'site_data', 'NPSS_Sites_Buffered_3338.shp')

# Define queries
taxa_file = path(sdm_repository, 'queries/00_taxon_query.sql')
site_visit_file = path(sdm_repository, 'queries/03_site_visit_query.sql')
vegetation_file = path(sdm_repository, 'queries/05_vegetation_query.sql')

#### QUERY AKVEG DATABASE
####------------------------------

# Import database connection function
connection_script = path(akveg_repository, 'package_DataProcessing', 'connect_database_postgresql.R')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = path(credentials_folder, 'authentication_akveg_private.csv')
database_connection = connect_database_postgresql(authentication)

# Read taxonomy standard from AKVEG Database
taxa_query = read_file(taxa_file)
taxa_data = as_tibble(dbGetQuery(database_connection, taxa_query))

# Read site visit data from AKVEG Database
site_visit_query = read_file(site_visit_file)
site_visit_data = as_tibble(dbGetQuery(database_connection, site_visit_query)) 

# Read vegetation cover data from AKVEG Database
vegetation_query = read_file(vegetation_file)
vegetation_data = as_tibble(dbGetQuery(database_connection, vegetation_query)) %>%
  # Use short names
  rename(st_vst = site_visit_code,
         cvr_pct = cover_percent) %>%
  # Standardize names
  mutate(name_accepted = case_when(name_accepted == 'Achillea millefolium' ~ 'Achillea millefolium ssp. borealis',
                                   name_accepted == 'Leymus mollis ssp. mollis' ~ 'Leymus mollis',
                                   name_accepted == 'Leymus mollis ssp. villosissimus' ~ 'Leymus mollis',
                                   name_accepted == 'Saxifraga funstonii' ~ 'Saxifraga cherlerioides',
                                   TRUE ~ name_accepted))

#### PROCESS COLLECTION DATA
####------------------------------

# Read local data (must be crs 3338)
zone_shape = st_read(zone_input)

# Read and format Atka 2019 data
atka_data = read_xlsx(atka_input, sheet = 'Atka_2019') %>%
  # Compile taxonomic names
  mutate(name_original = case_when(is.na(Infrank) ~ paste(Gen, ' ', Spe, sep = ''),
                                   TRUE ~ paste(Gen, ' ', Spe, ' ', Infrank, ' ', Infname, sep = ''))) %>%
  # Format dates
  mutate(observe_date = paste(Year, '-07-', Day, sep = '')) %>%
  # Standardize column names
  rename(latitude_dd = `Lat(decdegree)`,
         longitude_dd = `Long(decdegree)`,
         site_visit_code = `Collection #`) %>%
  # Select columns
  select(site_visit_code, name_original, observe_date, latitude_dd, longitude_dd) %>%
  # Convert geometries to points with EPSG 4269
  st_as_sf(x = ., coords = c('longitude_dd', 'latitude_dd'), crs = 4269, remove = FALSE) %>%
  # Reproject coordinates to EPSG 3338
  st_transform(crs = st_crs(3338))

# Read and format Dechaine data
dechaine_data = read_xlsx(dechaine_input, sheet = 'Dechaine') %>%
  # Remove unreliable absence records
  filter(presence == 1) %>%
  # Format dates
  mutate(observe_date = case_when(month(date) < 10 & day(date) < 10 ~ paste(year(date), '-0', month(date), '-0', day(date), sep = ''),
                                  month(date) < 10 & day(date) >= 10 ~ paste(year(date), '-0', month(date), '-', day(date), sep = ''),
                                  month(date) >= 10 & day(date) < 10 ~ paste(year(date), '-', month(date), '-0', day(date), sep = ''),
                                  TRUE ~ paste(year(date), '-', month(date), '-', day(date), sep = ''))) %>%
  # Format site visit codes
  rowid_to_column('id') %>%
  mutate(site_visit_code = case_when(id < 10 ~ paste('EGD-', year(observe_date), '-00', id, sep = ''),
                                     id < 100 ~ paste('EGD-', year(observe_date), '-0', id, sep = ''),
                                     TRUE ~ paste('EGD-', year(observe_date), '-', id, sep = ''))) %>%
  # Standardize column names
  rename(name_original = taxon) %>%
  # Select columns
  select(site_visit_code, name_original, observe_date, latitude_dd, longitude_dd) %>%
  # Convert geometries to points with EPSG 4326
  st_as_sf(x = ., coords = c('longitude_dd', 'latitude_dd'), crs = 4326, remove = FALSE) %>%
  # Reproject coordinates to EPSG 3338
  st_transform(crs = st_crs(3338))

# Read and format Rare Plant data
rare_data = read_xlsx(rare_input, sheet = 'Occurrences') %>%
  # Select relevant records
  filter(SPECIMEN_ID == '160080' |
           SPECIMEN_ID == '147482' |
           SPECIMEN_ID == '60414' |
           SPECIMEN_ID == '88883' |
           SPECIMEN_ID == '160096' |
           SPECIMEN_ID == 'https://www.inaturalist.org/observations/95891343') %>%
  # Format dates
  rename(date = DATE) %>%
  mutate(date = as.numeric(date)) %>%
  mutate(date = excel_numeric_to_date(date)) %>%
  mutate(observe_date = case_when(month(date) < 10 & day(date) < 10 ~ paste(year(date), '-0', month(date), '-0', day(date), sep = ''),
                                  month(date) < 10 & day(date) >= 10 ~ paste(year(date), '-0', month(date), '-', day(date), sep = ''),
                                  month(date) >= 10 & day(date) < 10 ~ paste(year(date), '-', month(date), '-0', day(date), sep = ''),
                                  TRUE ~ paste(year(date), '-', month(date), '-', day(date), sep = ''))) %>%
  # Format site visit codes
  mutate(site_visit_code = case_when(SPECIMEN_ID == 'https://www.inaturalist.org/observations/95891343' ~ 'INAT_95891343',
                                     TRUE ~ paste('ALA_', SPECIMEN_ID, sep = ''))) %>%
  # Standardize column names
  rename(latitude_dd = LATITUDE,
         longitude_dd = LONGITUDE,
         name_original = TAXON) %>%
  # Select columns
  select(site_visit_code, name_original, observe_date, latitude_dd, longitude_dd) %>%
  # Convert geometries to points with EPSG 4269
  st_as_sf(x = ., coords = c('longitude_dd', 'latitude_dd'), crs = 4269, remove = FALSE) %>%
  # Reproject coordinates to EPSG 3338
  st_transform(crs = st_crs(3338))

# Merge the Atka and Dechaine data
collection_data = rbind(atka_data, dechaine_data, rare_data) %>%
  # Add missing columns
  mutate(project_code = 'nps_npss_2018',
         scope_vascular = 'target species',
         plot_radius_m = 20) %>%
  # Add accepted taxa names
  left_join(taxa_data, by = c('name_original' = 'taxon_name')) %>%
  rename(name_accepted = taxon_accepted) %>%
  filter(!is.na(name_accepted)) %>%
  # Select columns
  select(site_visit_code, project_code, name_accepted, observe_date, scope_vascular, plot_radius_m, geometry) %>%
  # Add centroid coordinates in EPSG 3338
  mutate(cent_x = st_coordinates(.$geometry)[,1],
         cent_y = st_coordinates(.$geometry)[,2])

# Create site-taxon table
collection_taxa = collection_data %>%
  select(site_visit_code, name_accepted) %>%
  rename(name_collection = name_accepted)

#### FORMAT SITE VISITS
####------------------------------

# Format site visit data
akveg_site_data = site_visit_data %>%
  # Process plot sizes into buffer radius
  mutate(plot_dimensions_m = case_when(perspective == 'aerial' & plot_dimensions_m == 'unknown' ~ '20 radius',
                                       TRUE ~ plot_dimensions_m)) %>%
  filter(plot_dimensions_m != '2×2' &
           plot_dimensions_m != '5×8' &
           plot_dimensions_m != '2×7' &
           plot_dimensions_m != '1×10' &
           plot_dimensions_m != '3×7' &
           plot_dimensions_m != '2×5' &
           plot_dimensions_m != '5×20' &
           plot_dimensions_m != '3×20' &
           plot_dimensions_m != '4×4' &
           plot_dimensions_m != 'unknown' &
           plot_dimensions_m != '8×8' &
           plot_dimensions_m != '4×25' &
           plot_dimensions_m != '5×15' &
           plot_dimensions_m != '6×6' &
           plot_dimensions_m != '3×6' &
           plot_dimensions_m != '5×10' &
           plot_dimensions_m != '4×8' &
           plot_dimensions_m != '5×5' &
           plot_dimensions_m != '5×30' &
           plot_dimensions_m != '8×10' &
           plot_dimensions_m != '8×12' &
           plot_dimensions_m != '2×20' &
           plot_dimensions_m != '6×10' &
           plot_dimensions_m != '7×10' &
           plot_dimensions_m != '2×12' &
           plot_dimensions_m != '3×12' &
           plot_dimensions_m != '6×12' &
           plot_dimensions_m != '3×10' &
           plot_dimensions_m != '3×15' &
           plot_dimensions_m != '1×12' &
           plot_dimensions_m != '3×25' &
           plot_dimensions_m != '1×8' &
           plot_dimensions_m != '1×7' &
           plot_dimensions_m != '7×8' &
           plot_dimensions_m != '3×8' &
           plot_dimensions_m != '2×10' &
           plot_dimensions_m != '1 radius') %>%
  mutate(plot_radius_m = case_when(plot_dimensions_m == '55 radius' ~ 55,
                                   (plot_dimensions_m == '34.7 radius' |
                                      plot_dimensions_m == '50×50') ~ 35,
                                   plot_dimensions_m == '30 radius' ~ 30,
                                   plot_dimensions_m == '30×80' ~ 25,
                                   plot_dimensions_m == '23 radius' ~ 23,
                                   (plot_dimensions_m == '20 radius' |
                                      plot_dimensions_m == '30×30' |
                                      plot_dimensions_m == '25×100') ~ 20,
                                   (plot_dimensions_m == '25×25' |
                                      plot_dimensions_m == '20×40' |
                                      plot_dimensions_m == '20×100' |
                                      plot_dimensions_m == '20×80') ~ 18,
                                   (plot_dimensions_m == '15 radius' |
                                      plot_dimensions_m == '20×20' |
                                      plot_dimensions_m == '15×30' |
                                      plot_dimensions_m == '15×100') ~ 15,
                                   (plot_dimensions_m == '12.5 radius' |
                                      plot_dimensions_m == '18×18') ~ 12.5,
                                   plot_dimensions_m == '11.6 m radius' ~ 12,
                                   (plot_dimensions_m == '10 radius' |
                                      plot_dimensions_m == '15×15' |
                                      plot_dimensions_m == '10×20' |
                                      plot_dimensions_m == '15×18' |
                                      plot_dimensions_m == '10×40' |
                                      plot_dimensions_m == '10×30') ~ 10,
                                   (plot_dimensions_m == '8 radius' |
                                      plot_dimensions_m == '12×12') ~ 8,
                                   (plot_dimensions_m == '10×10' |
                                      plot_dimensions_m == '10×12') ~ 7,
                                   plot_dimensions_m == '5 radius' ~ 5)) %>%
  # Convert geometries to points with EPSG 4269
  st_as_sf(x = ., coords = c('longitude_dd', 'latitude_dd'), crs = 4269, remove = FALSE) %>%
  # Reproject coordinates to EPSG 3338
  st_transform(crs = st_crs(3338)) %>%
  # Select columns
  select(site_visit_code, project_code, observe_date, scope_vascular, plot_radius_m, geometry) %>%
  # Add centroid coordinates in EPSG 3338
  mutate(cent_x = st_coordinates(.$geometry)[,1],
         cent_y = st_coordinates(.$geometry)[,2])

# Format absence sites
absence_data = st_read(dsn = project_geodatabase, layer = absence_layer) %>%
  select(Shape) %>%
  # Set observe date
  mutate(observe_date = '2024-07-29') %>%
  # Format site visit codes
  rowid_to_column('id') %>%
  mutate(site_visit_code = case_when(id < 10 ~ paste('ABS-', year(observe_date), '-000', id, sep = ''),
                                     id < 100 ~ paste('ABS-', year(observe_date), '-00', id, sep = ''),
                                     id < 1000 ~ paste('ABS-', year(observe_date), '-00', id, sep = ''),
                                     TRUE ~ paste('EGD-', year(observe_date), '-', id, sep = ''))) %>%
  # Add missing columns
  mutate(project_code = 'akveg_absences',
         scope_vascular = 'exhaustive',
         plot_radius_m = 10) %>%
  # Add centroid coordinates in EPSG 3338
  mutate(cent_x = st_coordinates(.$Shape)[,1],
         cent_y = st_coordinates(.$Shape)[,2]) %>%
  # Select columns
  select(site_visit_code, project_code, observe_date, scope_vascular, plot_radius_m, cent_x, cent_y) %>%
  # Format geometry
  st_drop_geometry() %>%
  st_as_sf(x = ., coords = c('cent_x', 'cent_y'), crs = 3338, remove = FALSE)

# Bind site
sites_all = collection_data %>%
  select(-name_accepted) %>%
  # Combine collection, AKVEG, and absence sites
  rbind(akveg_site_data) %>%
  rbind(absence_data) %>%
  # Use column short names
  rename(st_vst = site_visit_code,
         prjct_cd = project_code,
         obs_date = observe_date,
         scp_vasc = scope_vascular,
         plt_rad_m = plot_radius_m) %>%
  # Remove sites outside of the Alaska-Yukon Map Domain
  st_as_sf(x = ., coords = c('centroid_x', 'centroid_y'), crs = 3338, remove = FALSE) %>%
  st_intersection(zone_shape) %>%
  st_zm(drop = TRUE, what = "ZM") %>%
  # Buffer sites
  st_buffer(.$plt_rad_m)

# Save selected points to shapefile
st_write(sites_all, sites_output, append = FALSE)

#### EXPORT SPECIES DATA
####------------------------------

# Define target species list
target_list = c('Achillea millefolium ssp. borealis', 'Arctostaphylos uva-ursi',
               'Cerastium aleuticum', 'Empetrum nigrum', 'Leymus mollis',
               'Lupinus nootkatensis', 'Rubus chamaemorus', 'Saxifraga aleutica',
               'Saxifraga cherlerioides', 'Senecio pseudoarnica')
code_list = c('ACHMILSBOR', 'ARCUVA', 'CERALE', 'EMPNIG', 'LEYMOL',
              'LUPNOO', 'RUBCHA', 'SAXALE', 'SAXCHE', 'SENPSE')

# Export species data for each taxon
count = 1
for (target_species in target_list) {
  # Define output file
  species_output = path(project_folder, 'species_data', paste('PresenceAbsence_', code_list[count], '_3338.csv', sep = ''))
  
  # Compile species presence/absence data
  species_data = vegetation_data %>%
    filter(name_accepted == target_species &
             dead_status == 'FALSE') %>%
    full_join(sites_all, by = 'st_vst') %>%
    filter(!is.na(obs_date)) %>%
    left_join(collection_taxa, by = c('st_vst' = 'site_visit_code')) %>%
    mutate(name_accepted = case_when(prjct_cd == 'nps_npss_2018' ~ name_collection,
                                     TRUE ~ name_accepted)) %>%
    filter((name_accepted == target_species & prjct_cd == 'nps_npss_2018') |
             prjct_cd != 'nps_npss_2018') %>%
    mutate(cvr_pct = case_when(prjct_cd == 'nps_npss_2018' ~ 0,
                               is.na(cvr_pct) ~ -999,
                               TRUE ~ cvr_pct)) %>%
    mutate(presence = case_when(cvr_pct == -999 ~ 0,
                                TRUE ~ 1)) %>%
    filter((presence == 1) | (presence == 0 & (scp_vasc == 'exhaustive' | scp_vasc == 'non-trace species'))) %>%
    # Filter questionable records for Senecio pseudoarnica
    {if (target_species == 'Senecio pseudoarnica') filter(., st_vst != 'NSSI11186_20110813' &
                                                            st_vst != 'KEFJ04A055_20040807' &
                                                            st_vst != 'KEFJ040351_20040808' &
                                                            st_vst != 'KATM00062_20000808' &
                                                            st_vst != 'KEFJ040361_20040808' &
                                                            st_vst != 'haba-t2-1400_20080721')
      else filter(., !is.na(st_vst))} %>%
    # Select columns
    select(st_vst, prjct_cd, obs_date, scp_vasc, plt_rad_m,
           cvr_pct, presence, lat_dd, long_dd, cent_x, cent_y) %>%
    # Create point geometry
    st_as_sf(x = ., coords = c('cent_x', 'cent_y'), crs = 3338, remove = FALSE)
  
  # Export data to output table
  st_write(species_data, species_output, append = FALSE)
  
  # Increase count
  count = count + 1
}
