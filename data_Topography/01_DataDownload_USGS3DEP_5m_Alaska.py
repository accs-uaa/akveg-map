# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download USGS 3DEP 5m Alaska Tiles
# Author: Timm Nawrocki
# Last Updated: 2021-11-22
# Usage: Can be executed in an Anaconda Python 3.7 distribution or an ArcGIS Pro Python 3.6 distribution.
# Description: "Download USGS 3DEP 5m Alaska Tiles" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table can be generated from The National Map Viewer web application.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import download_from_csv
import os

# Define base folder structure
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS_3DEP_5m')
directory = os.path.join(data_folder, 'tiles')

# Define input csv table
input_table = os.path.join(data_folder, 'USGS_3DEP_5m_20211121.csv')
url_column = 'url'

# Download files
download_from_csv(input_table, url_column, directory)