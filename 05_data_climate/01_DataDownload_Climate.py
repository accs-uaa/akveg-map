# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download climate datasets
# Author: Timm Nawrocki
# Last Updated: 2025-12-18
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Download climate datasets" contacts a server to download a series of files specified in a csv table. The full url to the resources must be specified in the table. The table should be manually created.
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
drive = 'E:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/climatology')
download_folder = os.path.join(data_folder, 'zip')
extract_folder = os.path.join(data_folder, 'unprocessed')

# Define input csv table
download_input = os.path.join(data_folder, 'ClimateDatasets_20251218.csv')
url_column = 'downloadURL'

#### PROCESS DATA DOWNLOADS
####____________________________________________________

# Import a csv file with the download urls
download_items = pd.read_csv(download_input)

# Download each zip file if it has not already been downloaded
count = 1
for download_url in download_items[url_column]:
    # Create download file path
    download_file = os.path.join(download_folder, os.path.split(download_url)[1])
    # Download file if it does not exist
    if os.path.exists(download_file) == 0:
        print(f'Downloading file {count} of {len(download_items[url_column])}...')
        try:
            # Initiate download
            iteration_start = time.time()
            response = requests.get(download_url, stream=True)

            # Determine download size
            total_bytes = int(response.headers.get('content-length', 0))
            total_mb = round((total_bytes / (1024 * 1024)), 0)

            # Print download size
            if total_bytes == 0:
                print('\tCould not determine file size.')
            elif total_mb == 0:
                print(f'\tDownload size is {total_bytes} bytes.')
            else:
                print(f'\tDownload size is {total_mb} mb.')

            # Download file
            block_size = 4096
            progress_bar = tqdm(total=total_bytes, unit='iB', unit_scale=True)
            with open(download_file, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            end_timing(iteration_start)
        except:
            print(f'File {count} of {len(download_items[url_column])} not available for download. Check url.')
            print('----------')
    else:
        print(f'File {count} of {len(download_items[url_column])} already exists.')
        print('----------')

    # Increase count
    count += 1

# Extract zip file contents
zip_files = glob.glob(os.path.join(download_folder, '*.zip'))
count = 1
for zip_file in zip_files:
    # Extract contents from archive
    try:
        print(f'Unzipping archive {count} of {len(zip_files)}...')
        iteration_start = time.time()
        shutil.unpack_archive(zip_file, extract_folder, 'zip')
        end_timing(iteration_start)
    except:
        print(f'{os.path.split(zip_file)[1]} is not an archive.')
        print('----------')

    # Increase count
    count += 1
