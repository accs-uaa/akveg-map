# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download USGS 3DEP 5 m Alaska Tiles
# Author: Timm Nawrocki
# Last Updated: 2019-10-29
# Usage: Can be executed in an Anaconda Python 3.7 distribution or an ArcGIS Pro Python 3.6 distribution.
# Description: "Download USGS 3DEP 5 m Alaska Tiles" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table can be generated from The National Map Viewer web application.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import download_from_csv
import os

# Define base folder structure
drive = 'K:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS3DEP_5m_Alaska')

# Define input csv table
input_table = os.path.join(data_folder, 'USGS3DEP_5m_Alaska_Tiles_PartA.csv')
url_column = 'downloadURL'

# Set target directory for downloads
directory = os.path.join(data_folder, 'tiles')

# Download files
download_from_csv(input_table, url_column, directory)
