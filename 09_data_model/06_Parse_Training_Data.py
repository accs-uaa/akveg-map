# ---------------------------------------------------------------------------
# Parse training data
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2026-02-12
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Parse training data" parses train-validate-test data for each diagnostic species set.
# ---------------------------------------------------------------------------

# Import libraries
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio

# Set version date
version_date = '20260212'

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work'

# Define folder structure
repository_folder = os.path.join(drive, root_folder, 'Repositories/foliar-cover')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map')
input_folder = os.path.join(project_folder, 'Data/Data_Input/database_archive', f'version_{version_date}')
output_folder = os.path.join(project_folder, 'Data/Data_Output/exclude_data', f'version_{version_date}')

# Define input files
schema_input = os.path.join(repository_folder, 'AKVEG_Schema_FoliarCover.csv')
site_visit_input = os.path.join(input_folder, '03_site_visit.csv')
vegetation_input = os.path.join(input_folder, '05_vegetation_cover.csv')

# Define output files

# Read input data
schema_data = pd.read_csv(schema_input)
site_visit_data = pd.read_csv(site_visit_input)
vegetation_data = pd.read_csv(vegetation_input)

# Remove dead vegetation
vegetation_data = vegetation_data[vegetation_data['dead_status'] == False]

#### IDENTIFY EXCLUSION SITES
####____________________________________________________

# Define a function to list site visit codes for exclusion
def exclusion_sites(vegetation_data, exclude_taxon):
    # Filter site visits from vegetation data to the excluded taxon
    filtered_data = vegetation_data[
        (vegetation_data['name_accepted'] == exclude_taxon)
        & ((vegetation_data['cover_percent'] >= 5) | (vegetation_data['cover_percent'] == -999))]
    exclude_site_visits = filtered_data['site_visit_code'].unique()
    return exclude_site_visits

# Create exclusion sites for plots below threshold size
exclude_plot_size = site_visit_data[
    site_visit_data['plot_radius_m'] <= 3]['site_visit_code'].unique()

# Exclude burned sites
exclude_burned = site_visit_data[
    site_visit_data['fire_year'] >= site_visit_data['observe_year']]['site_visit_code'].unique()

# Create exclusion sites where centroid overlaps water
exclude_water = site_visit_data[
    ((site_visit_data['esa_type'] == 80) & (site_visit_data['project_code'] != 'akveg_absences'))
    | ((site_visit_data['coast'] < 50) & (site_visit_data['project_code'] == 'nps_kenai_2004'))
]['site_visit_code'].unique()

# Exclude sites with tree observations
exclude_brotre = exclusion_sites(vegetation_data, 'tree broadleaf')
exclude_nedtre = exclusion_sites(vegetation_data, 'tree needleleaf')
exclude_betula = exclusion_sites(vegetation_data, 'Betula')
exclude_picea = exclusion_sites(vegetation_data, 'Picea')
exclude_populus = exclusion_sites(vegetation_data, 'Populus')
exclude_tsuga = exclusion_sites(vegetation_data, 'Tsuga')

# Exclude sites with shrub observations
exclude_dwashr = exclusion_sites(vegetation_data, 'shrub dwarf')
exclude_shrub = exclusion_sites(vegetation_data, 'shrub')
exclude_decshr = exclusion_sites(vegetation_data, 'shrub deciduous')
exclude_evrshr = exclusion_sites(vegetation_data, 'shrub evergreen')
exclude_rubus = exclusion_sites(vegetation_data, 'Rubus')
exclude_salix = exclusion_sites(vegetation_data, 'Salix')
exclude_vaccinium = exclusion_sites(vegetation_data, 'Vaccinium')

# Exclude sites with herbaceous observations
exclude_forb = exclusion_sites(vegetation_data, 'forb')
exclude_gramin = exclusion_sites(vegetation_data, 'graminoid')
exclude_grass = exclusion_sites(vegetation_data, 'grass (Poaceae)')
exclude_herb = exclusion_sites(vegetation_data, 'herbaceous')
exclude_calama = exclusion_sites(vegetation_data, 'Calamagrostis')
exclude_carex = exclusion_sites(vegetation_data, 'Carex')
exclude_erioph = exclusion_sites(vegetation_data, 'Eriophorum')
exclude_festuca = exclusion_sites(vegetation_data, 'Festuca')
exclude_sedge = exclusion_sites(vegetation_data, 'sedge (Cyperaceae)')
exclude_leymus = exclusion_sites(vegetation_data, 'Leymus')

# Exclude sites with nonvascular observations
exclude_bryoph = exclusion_sites(vegetation_data, 'bryophyte')
exclude_moss = exclusion_sites(vegetation_data, 'moss')

#### PARSE TRAINING DATA
####____________________________________________________

# Join taxon habit to vegetation cover


# Split observed absences from observed presences
explicit_absences = vegetation_data[vegetation_data[cover_percent] == -999]
vegetation_data = vegetation_data[vegetation_data[cover_percent] >= 0]

# Define a function to parse training data
def parse_training_data(target, schema_data, vegetation_data, site_visit_data,
                        explicit_absences, exclude_plot_size, exclude_burned, exclude_water):
    # Retrieve parameters from schema
    parameter_data = schema_data[schema_data['target_abbr'] == target]

    # If functional group, sum taxon habit cover values

    # If diagnostic species set, sum taxa cover values

    # If vascular plant
        # If top absence is true
            # Interpret absences
        # If top absence is false
            # Interpret absences

    # If bryophyte (top absence is always false)
        # Interpret absences

    # If lichen (top absence is always false)
        # Interpret absences

    # Add explicit absences

    # Remove exclusion sites
