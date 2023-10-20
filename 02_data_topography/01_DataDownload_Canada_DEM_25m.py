# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Canada DEM 25 m tiles
# Author: Timm Nawrocki
# Last Updated: 2023-10-10
# Usage: Execute in Python 3.9+.
# Description: "Download Canada DEM 25 m tiles" contacts a server to download a series of files using the block IDs from the "Indexes of the National Topographic System of Canada" (available: https://open.canada.ca/data/en/dataset/055919c2-101e-4329-bfd7-1d0c333c0e62). The Canada DEM (circa 2011) is available at: https://open.canada.ca/data/en/dataset/7f245e4d-76c2-4caa-951a-45d1d2051333.
# ---------------------------------------------------------------------------

# Import packages
import os
import shutil
import time
import pandas as pd
import requests
from akutils import end_timing

# Define base folder structure
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/Canada_DEM_25m')
download_folder = os.path.join(data_folder, 'zip')
extract_folder = os.path.join(data_folder, 'unprocessed')

# Define input csv table
input_table = os.path.join(data_folder, 'Canada_DEM_Blocks.csv')
block_field = 'NTS_SNRC'

# Define base url
url = 'https://ftp.maps.canada.ca/pub/nrcan_rncan/elevation/cdem_mnec/'

# Import a csv file with the download urls for the Arctic DEM tiles
download_items = pd.read_csv(input_table)

# Create download list
download_list = []
for block in download_items[block_field]:
    download_url = url + block[0:3] + '/' + 'cdem_dem_' + block + '_tif.zip'
    download_list.append(download_url)

# Download each zip file if it has not already been downloaded
count = 1
for download in download_list:
    # Create download file path
    download_file = os.path.join(download_folder, os.path.split(download)[1])
    # Download file if it does not exist
    if os.path.exists(download_file) == 0:
        print(f'Downloading file {count} of {len(download_list)}...')
        iteration_start = time.time()
        # Create response and download content
        response = requests.get(download)
        with open(download_file, mode="wb") as file:
            file.write(response.content)
        # Extract contents from archive
        try:
            shutil.unpack_archive(download_file, extract_folder)
        except:
            print(f'{os.path.split(download_file)[1]} is not an archive.')
        end_timing(iteration_start)
    else:
        print(f'File {count} of {len(download_list)} already exists.')
        print('----------')
    count += 1
