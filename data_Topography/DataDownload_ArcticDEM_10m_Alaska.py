# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Arctic DEM 10 m Alaska Tiles
# Author: Timm Nawrocki
# Last Updated: 2019-10-29
# Usage: Can be executed in an Anaconda Python 3.7 distribution or an ArcGIS Pro Python 3.6 distribution.
# Description: "Download Arctic DEM 10 m Alaska Tiles" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table can be generated from the Arctic DEM tile index shapefile.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import downloadFromCSV
import os

# Define base folder structure
drive = 'K:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/ArcticDEM_10m_Alaska')

# Define input csv table
input_table = os.path.join(data_folder, 'ArcticDEM_Alaska_10m_20191029.csv')
url_column = 'downloadURL'

# Set target directory for downloads
directory = os.path.join(data_folder, 'tiles')

# Download files
downloadFromCSV(input_table, url_column, directory)
