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
import time
from tqdm import tqdm
import pandas as pd
import requests
from akutils import end_timing

# Define base folder structure
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/USGS_3DEP_60m')
download_folder = os.path.join(data_folder, 'unprocessed')

# Define input csv table
input_table = os.path.join(data_folder, 'USGS_3DEP_60m_20231009.csv')
url_field = 'fileurl'

# Import a csv file with the download urls for the Arctic DEM tiles
download_items = pd.read_csv(input_table)

# Download each zip file if it has not already been downloaded
count = 1
for download in download_items[url_field]:
    # Create download file path
    download_file = os.path.join(download_folder, os.path.split(download)[1])
    # Download file if it does not exist
    if os.path.exists(download_file) == 0:
        print(f'Downloading file {count} of {len(download_items[url_field])}...')
        iteration_start = time.time()
        response = requests.get(download, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(download_file, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        end_timing(iteration_start)
    else:
        print(f'File {count} of {len(download_items[url_field])} already exists.')
        print('----------')
    count += 1
