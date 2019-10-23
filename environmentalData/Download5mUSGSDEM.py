# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download USGS 3DEP 5 m DEM Tiles
# Author: Timm Nawrocki
# Created on: 2019-10-15
# Usage: Must be executed in Python 3.7
# Description: "Download USGS 3DEP 5 m DEM Tiles" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table can be generated from The National Map Viewer web application.
# ---------------------------------------------------------------------------

# Import packages
from beringianGeospatialProcessing import downloadFromCSV

# Define input file
input_table = 'K:/ACCS_Work/Data/elevation/USGS_5m/usgs5m_20191014.csv'
url_column = 'downloadURL'

# Set target directory for downloads
directory = 'K:/ACCS_Work/Data/elevation/USGS_5m/tiles'

# Download files
downloadFromCSV(input_table, url_column, directory)
