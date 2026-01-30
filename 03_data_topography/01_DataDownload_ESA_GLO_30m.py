# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download ESA GLO DEM 30 m tiles
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Download ESA GLO DEM 30 m tiles" contacts a server to download a series of 30 m DEM tiles for the ESA GLO 30 m DEM: https://spacedata.copernicus.eu/en/web/guest/collections/copernicus-digital-elevation-model
# ---------------------------------------------------------------------------

# Import packages
import glob
import os
import shutil
import time
from tqdm import tqdm
import pandas as pd
import requests
from akutils import end_timing

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Define base folder structure
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/ESA_GLO_30m')
download_folder = os.path.join(data_folder, 'zip')
extract_folder = os.path.join(data_folder, 'unprocessed')

# Make output directory if it does not already exist
if os.path.exists(download_folder) == 0:
    os.mkdir(download_folder)
if os.path.exists(extract_folder) == 0:
    os.mkdir(extract_folder)

# Define input csv table
download_input = os.path.join(data_folder, 'ESA_GLO_30m_Index.csv')
block_field = 'Product30'
base_url = 'https://prism-dem-open.copernicus.eu/pd-desk-open-access/prismDownload/COP-DEM_GLO-30-DGED__2022_1/'

#### PROCESS DATA DOWNLOADS
####____________________________________________________

# Import a csv file with the download urls for the Arctic DEM tiles
download_items = pd.read_csv(download_input)

# Download each zip file if it has not already been downloaded
count = 1
for download in download_items[block_field]:
    # Update file name
    download = download.replace('DSM_30', 'DSM_10') + '.tar'
    # Create download file path
    download_file = os.path.join(download_folder, download)
    # Download file if it does not exist
    if os.path.exists(download_file) == 0:
        print(f'Downloading file {count} of {len(download_items[block_field])}...')
        iteration_start = time.time()
        response = requests.get(base_url + download, stream=True)
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
            shutil.unpack_archive(download_file, extract_folder, 'tar')
        except:
            print(f'{os.path.split(download_file)[1]} is not an archive.')
        end_timing(iteration_start)
    else:
        print(f'File {count} of {len(download_items[block_field])} already exists.')
        print('----------')
    count += 1

# Copy files to main directory
for folder in next(os.walk(extract_folder))[1]:
    if folder != 'corrected':
        source_folder = os.path.join(extract_folder, folder, 'DEM')
        os.chdir(source_folder)
        source_file = glob.glob('*DEM.tif')[0]
        shutil.copyfile(os.path.join(source_folder, source_file),
                        os.path.join(extract_folder, source_file))
