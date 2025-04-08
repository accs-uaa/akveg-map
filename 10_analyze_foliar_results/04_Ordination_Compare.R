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
root_folder = 'ACCS_Work'

# Define input folders (modify to your folder structure)
database_repository = path('C:', root_folder, 'Repositories/akveg-database')
credentials_folder = path('C:', root_folder, 'Credentials/akveg_private_read')
project_folder = path('C:', root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
input_folder = path(project_folder, 'Data_Input/extract_data')
output_folder = path(project_folder, 'Data_Output')

# Define input files
site_visit_input = path(input_folder, '03_site_visit.csv')