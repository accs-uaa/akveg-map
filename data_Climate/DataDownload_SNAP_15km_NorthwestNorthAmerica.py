# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download SNAP Climate Files
# Author: Timm Nawrocki
# Created on: 2020-01-06
# Usage: Can be executed in Anaconda Python 3.7 distribution or ArcGIS Pro Python 3.6 distribution.
# Description: "Download SNAP Climate Files" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table should be manually created.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import download_from_csv
import os

# Define base folder structure
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/climatology/SNAP_NorthwestNorthAmerica_15km')

# Define input csv table
input_table = os.path.join(data_folder, 'SNAP15km_20191029.csv')
url_column = 'downloadURL'

# Set target directory for downloads
directory = os.path.join(data_folder, 'unprocessed')

# Download files
download_from_csv(input_table, url_column, directory)


