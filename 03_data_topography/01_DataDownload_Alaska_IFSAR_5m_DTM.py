# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Alaska IFSAR 5m DTM tiles
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Download Alaska IFSAR 5m DTM tiles" contacts the DGGS FTP server to download all 5 m IFSAR DTM tiles for Alaska.
# ---------------------------------------------------------------------------

# Import packages
import os
import shutil
import time
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from akutils import end_timing

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Define base folder structure
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/Alaska_IFSAR_DTM_5m')
download_folder = os.path.join(data_folder, 'zip')
extract_folder = os.path.join(data_folder, 'unprocessed')

# Define source urls
base_url = 'https://dggs.alaska.gov/public_lidar/dds4/ifsar/dtm/'

# Make output directory if it does not already exist
if os.path.exists(download_folder) == 0:
    os.mkdir(download_folder)
if os.path.exists(extract_folder) == 0:
    os.mkdir(extract_folder)

#### PROCESS DATA DOWNLOADS
####____________________________________________________

# Get all links from source url
source_requests = requests.get(base_url)
source_format = BeautifulSoup(source_requests.text, features='lxml')
file_list = []
for link in source_format.find_all('a'):
    file_list.append(link.get('href'))
file_list.remove('../')
file_list.remove('_md5_checksums.txt')
file_list.remove('_sha1_checksums.txt')

# Loop through urls in the downloadURL column and download
count = 1
for download in file_list:
    url = base_url + '/' + download
    download_file = os.path.join(download_folder, download)
    # Download file if it does not already exist on local disk
    if os.path.exists(download_file) == 0:
        try:
            print(f'Downloading file {count} of {len(file_list)}...')
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
        except:
            print(f'File {count} of {len(file_list)} not available for download. Check url.')
            print('----------')
    else:
        print(f'\tFile {count} of {len(file_list)} already exists...')
        print('\t----------')
    count += 1
