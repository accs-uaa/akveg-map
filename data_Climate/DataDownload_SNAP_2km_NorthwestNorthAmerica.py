# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download SNAP 2 km Resolution Climate Files
# Author: Timm Nawrocki
# Last Updated: 2020-01-15
# Usage: Can be executed in Anaconda Python 3.7 distribution or ArcGIS Pro Python 3.6 distribution.
# Description: "Download SNAP 2 km Resolution Climate Files" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table should be manually created.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import download_from_csv
import os

# Define base folder structure
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/climatology/SNAP_NorthwestNorthAmerica_2km')

# Define input csv table
input_table = os.path.join(data_folder, 'SNAP2km_20200115.csv')
url_column = 'downloadURL'

# Set target directory for downloads
directory = os.path.join(data_folder, 'unprocessed')

# Download files
download_from_csv(input_table, url_column, directory)