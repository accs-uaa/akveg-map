# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Figure 3a. Training and validation data
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2025-07-09
# Usage: Script should be executed in R 4.4.3+.
# Description: "Figure 3a. Training and validation data" creates a map figure for publication that shows the training and validation data selected for the AKVEG foliar cover maps.
# ---------------------------------------------------------------------------

# Import required libraries
library(dplyr)
library(fs)
library(ggplot2)
library(ggrepel)
library(ggpattern)
library(readr)
library(readxl)
library(writexl)
library(RPostgres)
library(sf)
library(stringr)
library(terra)
library(tidyterra)
library(tibble)
library(tidyr)

#### SET UP DIRECTORIES AND FILES
####------------------------------

# Set round date
round_date = 'round_20241124'

# Define indicators
indicators = c('alnus', 'betshr', 'bettre', 'brotre', 'dryas', 'dsalix', 'empnig', 'erivag', 'mwcalama',
               'ndsalix', 'nerishr', 'picgla', 'picmar', 'picsit', 'poptre', 'populbt', 'rhoshr', 'rubspe',
               'sphagn', 'tsumer', 'vaculi', 'vacvit', 'wetsed')

# Set root directory
drive = 'C:'
root_folder = 'ACCS_Work'

# Define folder structure
database_repository = path(drive, root_folder, 'Repositories/akveg-database-public')
credentials_folder = path(drive, root_folder, 'Credentials/akveg_private_read')
project_folder = path(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map')
input_folder = path(project_folder, 'Data/Data_Input/species_data')
base_folder = path(project_folder, 'Data/Data_Input/basemap')
region_folder = path(project_folder, 'Data/Data_Input/region_data')
output_folder = path(project_folder, 'Documents/Manuscript_FoliarCover_FloristicGradients/figures')

# Define input files
ocean_input = path(base_folder, 'Basemap_Ocean_3338.shp')
russia_input = path(region_folder, 'Russia_Coastline_3571.shp')
na_input = path(region_folder, 'NorthAmerica_Coastline_4269.shp')
river_input = path(base_folder, 'NaturalEarth_10m_Rivers_Centerlines.shp')
domain_input = path(region_folder, 'AlaskaYukon_MapDomain_v2.0_3338.shp')
region_input = path(region_folder, 'AlaskaYukon_Regions_v2.0_3338.shp')

# Define queries
taxa_file = path(database_repository, 'queries/00_taxonomy.sql')
project_file = path(database_repository, 'queries/01_project.sql')
site_visit_file = path(database_repository, 'queries/03_site_visit.sql')
vegetation_file = path(database_repository, 'queries/05_vegetation.sql')
abiotic_file = path(database_repository, 'queries/06_abiotic_top_cover.sql')

# Define output files
figurea_output = path(output_folder, 'Figure3a_Training_Validation_Data.jpg')
training_output = path(input_folder, '00_training_data_summary.xlsx')

#### QUERY AKVEG DATABASE
####------------------------------

# Import database connection function
connection_script = path(database_repository, 'pull_functions', 'connect_database_postgresql.R')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = path(credentials_folder, 'authentication_akveg_private.csv')
database_connection = connect_database_postgresql(authentication)

# Read taxonomy standard from AKVEG Database
taxa_query = read_file(taxa_file)
taxa_data = as_tibble(dbGetQuery(database_connection, taxa_query))

# Read project data from AKVEG Database
project_query = read_file(project_file)
project_data = as_tibble(dbGetQuery(database_connection, project_query))

# Read site visit data from AKVEG Database
site_visit_query = read_file(site_visit_file)
site_visit_data = as_tibble(dbGetQuery(database_connection, site_visit_query))

# Read vegetation data from AKVEG Database
vegetation_query = read_file(vegetation_file)
vegetation_data = as_tibble(dbGetQuery(database_connection, vegetation_query))

# Read abiotic top cover data from AKVEG Database
abiotic_query = read_file(abiotic_file)
abiotic_data = as_tibble(dbGetQuery(database_connection, abiotic_query))

# Compile sites from vegetation and abiotic cover
vegetation_sites = vegetation_data %>%
  distinct(site_visit_code)
abiotic_sites = abiotic_data %>%
  distinct(site_visit_code)
site_check = rbind(vegetation_sites, abiotic_sites) %>%
  distinct(site_visit_code)

# Check that no site visits lack data for either vegetation cover or abiotic top cover
site_visit_nodata = site_visit_data %>%
  anti_join(site_check, by = 'site_visit_code')
site_visit_data = site_visit_data %>%
  inner_join(site_check, by = 'site_visit_code')

# Identify public data
site_visit_public = site_visit_data %>%
  left_join(project_data, by = 'project_code') %>%
  filter(private == FALSE)

#### COMPILE SELECTED SITE VISITS
####------------------------------

# Prepare empty data frames
site_visit_selected = tibble(site_visit_code = 'a')[0,]
site_visit_count = tibble(indicator = 'a', site_visits = 1)[0,]

# Read data frame of combined selected data
for (indicator in indicators) {
  # Set input files
  indicator_input = path(input_folder, paste('cover_', indicator, '_3338.csv', sep = ''))
  
  # Read results
  indicator_data = read_csv(indicator_input) %>%
    select(st_vst) %>%
    rename(site_visit_code = st_vst) %>%
    distinct(site_visit_code)
  
  # Omit the generated absences from the counts
  site_visit_true = indicator_data %>%
    inner_join(site_visit_data, by = 'site_visit_code')
  
  # Store number of site visits per indicator
  indicator_sites = tibble(indicator = indicator, site_visits = nrow(site_visit_true))
  
  # Bind rows
  site_visit_selected = rbind(site_visit_selected, indicator_data)
  site_visit_count = rbind(site_visit_count, indicator_sites)
  
}

# Process cover type
cover_data = vegetation_data %>%
  distinct(site_visit_code, cover_type)

# Identify unique selected sites across all indicators
absence_data = site_visit_selected %>%
  distinct(site_visit_code) %>%
  anti_join(site_visit_data, by = 'site_visit_code') %>%
  filter(grepl('ABS-', site_visit_code))
site_visit_selected = site_visit_selected %>%
  distinct(site_visit_code) %>%
  inner_join(site_visit_data, by = 'site_visit_code') %>%
  inner_join(cover_data, by = 'site_visit_code') %>%
  mutate(cover_version = case_when((cover_type == 'absolute canopy cover' | cover_type == 'absolute foliar cover') ~ 'absolute',
                                   (cover_type == 'top canopy cover' | cover_type == 'top foliar cover') ~ 'top',
                                   TRUE ~ 'error')) %>%
  # Convert geometries to points with EPSG:4269
  st_as_sf(x = ., coords = c('longitude_dd', 'latitude_dd'), crs = 4269, remove = FALSE) %>%
  # Reproject coordinates to EPSG 3338
  st_transform(crs = st_crs(3338)) %>%
  # Add EPSG:3338 centroid coordinates
  mutate(cent_x = st_coordinates(.$geometry)[,1],
         cent_y = st_coordinates(.$geometry)[,2]) %>%
  # Arrange data to plot absolute cover on top
  arrange(desc(cover_version))

#### CREATE MAP PLOT
####------------------------------

# Read shapes
ocean_data = st_read(ocean_input)
russia_data = st_read(russia_input) %>%
  st_transform(., crs = 3338)
na_data = st_read(na_input) %>%
  st_transform(., crs = 3338)
river_data = st_read(river_input) %>%
  st_transform(., crs = 3338)
domain_data = st_read(domain_input) %>%
  mutate(name = 'Alaska-Yukon Map Domain')
region_data = st_read(region_input) %>%
  select(biome, region)

# Define custom fill colors
custom_colors = c(
  'absolute' = '#535A6C',
  'top' = '#E1E5EE',
  'Alaska-Yukon Map Domain' = 'black'
)

# Define minimum and maximum latitude and longitude (EPSG:4326)
lon_min = -130
lon_max = 174
lat_min = 50
lat_max = 70

# Create a bounding box polygon and transform to EPSG:3338
bounds_4326 = st_sfc(
  st_polygon(list(rbind(
    c(lon_min, lat_min),
    c(lon_min, lat_max),
    c(lon_max, lat_max),
    c(lon_max, lat_min),
    c(lon_min, lat_min)
  ))),
  crs = 4326
)
bounds_3338 = st_transform(bounds_4326, crs = 3338)

# Extract x and y limits from bounding box
limit_coords = st_coordinates(bounds_3338)[,1:2]
x_limits = range(limit_coords[,1])
y_limits = range(limit_coords[,2])

# Create map of AKVEG regions and map domain
map_plot = ggplot() +
  geom_sf(data = ocean_data, color = NA, fill = '#BEE8FF', alpha = 0.3) +
  geom_sf(data = russia_data, color = 'black', fill = 'lightgray', linewidth = 0.2, alpha = 0.5) +
  geom_sf(data = na_data, color = 'black', fill = 'lightgray', linewidth = 0.2, alpha = 0.5) +
  geom_sf(data = region_data, color = 'black', fill = 'white', linewidth = 0.5) +
  geom_sf(data = river_data, color = '#BFD9F2', linewidth = 1) +
  geom_sf(data = russia_data, color = 'white', fill = NA, linewidth = 1.2) +
  geom_sf(data = russia_data, color = 'black', fill = NA, linewidth = 0.2) +
  geom_sf(data = na_data, color = 'white', fill = NA, linewidth = 1.2) +
  geom_sf(data = na_data, color = 'black', fill = NA, linewidth = 0.2) +
  geom_sf(data = site_visit_selected,
          aes(fill = cover_version),
          color = 'black',
          pch = 21,
          linewidth = 0.3,
          size = 2) +
  geom_sf(data = region_data, color = 'white', fill = NA, linewidth = 1.5) +
  geom_sf(data = region_data, color = 'black', fill = NA, linewidth = 0.5) +
  geom_sf(data = domain_data, aes(color = name), fill = NA, linewidth = 1.5) +
  scale_fill_manual(values = custom_colors) +
  scale_color_manual(values = custom_colors) +
  coord_sf(
    crs = st_crs(3338),
    xlim = x_limits,
    ylim = y_limits,
    expand = FALSE
  ) +
  scale_x_continuous(breaks = seq(-180, 180, by = 20))+
  scale_y_continuous(breaks = seq(50,70, by = 5)) +
  ggtitle('a. Map of site visits by absolute or top cover') +
  theme_minimal() +
  theme(
    axis.title = element_blank(),
    axis.text = element_text(size = 14),
    panel.grid.major = element_line(colour = 'gray'),
    legend.text = element_text(size = 18),
    legend.title = element_blank(),
    legend.position = 'top',
    legend.margin = margin(t = 10),
    plot.title = element_text(size = 20),
  ) +
  guides(
    fill = guide_legend(override.aes = list(size = 5)),
    color = guide_legend(override.aes = list(size = 2))
  )
  labs(
    fill = "Biome"
  )

# Export plot
ggsave(figurea_output,
       plot = map_plot,
       device = 'jpeg',
       path = NULL,
       scale = 2,
       width = 6.5,
       height = 4,
       units = 'in',
       dpi = 600,
       limitsize = TRUE)

# Export data to xlsx
export_data = site_visit_selected %>%
  # Join region
  st_join(., region_data) %>%
  # Drop geometry
  st_drop_geometry()
sheets = list('training' = export_data)
write_xlsx(sheets, training_output, format_headers = FALSE)