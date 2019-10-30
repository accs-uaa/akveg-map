# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download EnvYukon 30 m Yukon DEM
# Author: Timm Nawrocki
# Last Updated: 2019-10-29
# Usage: Can be executed in an Anaconda Python 3.7 distribution or an ArcGIS Pro Python 3.6 distribution.
# Description: "Download EnvYukon 30 m Yukon DEM" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table can be generated from The National Map Viewer web application.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import downloadFromCSV
import os

# Define base folder structure
drive = 'K:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/EnvYukon_30m_Yukon')

# Define input csv table
input_table = os.path.join(data_folder, 'EnvYukon_Yukon_30m_20191029.csv')
url_column = 'downloadURL'

# Set target directory for downloads
directory = os.path.join(data_folder, 'original')

# Download files
downloadFromCSV(input_table, url_column, directory)
