# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download USGS 3DEP 60m Alaska tiles
# Author: Timm Nawrocki
# Last Updated: 2023-10-09
# Usage: Execute in Python 3.9+.
# Description: "Download USGS 3DEP 60m Alaska tiles" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table can be generated from The National Map Viewer web application.
# ---------------------------------------------------------------------------

# Import packages
import os
import pandas as pd
import time
import urllib.request
from akveg import end_timing

# Define base folder structure
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS_3DEP_60m')
download_folder = os.path.join(data_folder, 'unprocessed')

# Define input csv table
input_table = os.path.join(data_folder, 'USGS_3DEP_60m_20231009.csv')
url_column = 'url'

# Import a csv file with the download urls for the Arctic DEM tiles
download_items = pd.read_csv(input_table)

# Initialize download count
n = len(download_items[url_column])
count = 1

# Loop through urls in the downloadURL column and download
for url in download_items[url_column]:
    target = os.path.join(download_folder, os.path.split(url)[1])
    # Download file if it does not already exist on local disk
    if os.path.exists(target) == 0:
        iteration_start = time.time()
        try:
            print(f'Downloading {count} of {n} files...')
            # Download data
            file_data = urllib.request.urlopen(url)
            data_to_write = file_data.read()
            with open(target, 'wb') as file:
                file.write(data_to_write)
                file.close()
            end_timing(iteration_start)
        except:
            print(f'File {count} of {n} not available for download. Check url.')
            print('----------')
    else:
        print(f'File {count} of {n} already exists...')
        print('----------')
    # Increase counter
    count += 1