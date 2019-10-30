# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Canada USGS 3DEP 30 m DEM Tiles
# Author: Timm Nawrocki
# Last Updated: 2019-10-29
# Usage: Can be executed in an Anaconda Python 3.7 distribution or an ArcGIS Pro Python 3.6 distribution.
# Description: "Download Canada USGS 3DEP 30 m DEM Tiles" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table can be generated from The National Map Viewer web application.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import downloadFromCSV

# Define input file
input_table = 'K:/ACCS_Work/Data/elevation/Canada_30m/canada30m_20191021.csv'
url_column = 'downloadURL'

# Set target directory for downloads
directory = 'K:/ACCS_Work/Data/topography/Canada_30m/tiles'

# Download files
downloadFromCSV(input_table, url_column, directory)
