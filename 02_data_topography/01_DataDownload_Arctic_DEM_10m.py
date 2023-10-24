# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Arctic DEM 10 m tiles
# Author: Timm Nawrocki
# Last Updated: 2023-10-10
# Usage: Execute in Python 3.9+.
# Description: "Download Arctic DEM 10 m tiles" contacts a server to download a series of 10 m mosaic files for the Arctic DEM v 4.1: https://www.pgc.umn.edu/data/arcticdem/
# ---------------------------------------------------------------------------

# Import packages
import os
import shutil
import time
from tqdm import tqdm
import pandas as pd
import requests
from akutils import end_timing

# Define base folder structure
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/Arctic_DEM_10m')
download_folder = os.path.join(data_folder, 'zip')
extract_folder = os.path.join(data_folder, 'unprocessed')

# Define input csv table
input_table = os.path.join(data_folder, 'Arctic_DEM_10m_4_1_Index.csv')
block_field = 'fileurl'

# Import a csv file with the download urls for the Arctic DEM tiles
download_items = pd.read_csv(input_table)

# Download each zip file if it has not already been downloaded
count = 1
for download in download_items[block_field]:
    # Create download file path
    download_file = os.path.join(download_folder, os.path.split(download)[1])
    # Download file if it does not exist
    if os.path.exists(download_file) == 0:
        print(f'Downloading file {count} of {len(download_items[block_field])}...')
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
        # Extract contents from archive
        try:
            print('Unzipping archive...')
            shutil.unpack_archive(download_file, extract_folder, 'gztar')
        except:
            print(f'{os.path.split(download_file)[1]} is not an archive.')
        end_timing(iteration_start)
    else:
        print(f'File {count} of {len(download_items[block_field])} already exists.')
        print('----------')
    count += 1
