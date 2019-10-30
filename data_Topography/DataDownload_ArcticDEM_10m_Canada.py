# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Arctic DEM 10 m Tiles
# Author: Timm Nawrocki
# Created on: 2019-10-15
# Usage: Must be executed in Python 3.7
# Description: "Download Arctic DEM 10 m Tiles" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table can be generated from the Arctic DEM tile index shapefile.
# ---------------------------------------------------------------------------

# Import packages
from beringianGeospatialProcessing import downloadFromCSV

# Define input file
input_table = 'K:/ACCS_Work/Data/elevation/ArcticDEM_10m/ArcticDEM10m_20191015.csv'
url_column = 'downloadURL'

# Set target directory for downloads
directory = 'K:/ACCS_Work/Data/topography/ArcticDEM_10m/tiles'

# Download files
downloadFromCSV(input_table, url_column, directory)
