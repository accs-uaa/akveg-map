# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Data from Drive
# Author: Timm Nawrocki
# Last Updated: 2019-11-25
# Usage: Must be executed in a Python 3.7 installation with Google API Python Client and PyDrive installed.
# Description: "Download Data from Drive" programmatically downloads batches of data from Google Drive. The script can be used to download spectral data processed into a Google Drive folder from Google Earth Engine.
# ---------------------------------------------------------------------------

# Import packages
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import datetime
import time

# Set root directory
drive = 'N:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Set data folder
data_folder = os.path.join(root_folder, 'Data/imagery/sentinel-2/unprocessed')

# Define target Google Drive folder
google_folder = '1KSwPnPWmf0PGJWM0kVX1TFCL28FyyUt2' # Beringia_Sentinel 2

# Change working directory to credentials folder
credentials_folder = os.path.join(root_folder, 'Administrative/Credentials')
os.chdir(credentials_folder)

# Create authenticated GoogleAuth instance
gauth = GoogleAuth()
gauth.LocalWebserverAuth()

# Create Google Drive instance with authenticated GoogleAuth instance
drive = GoogleDrive(gauth)

# Get a list of files to download from the google folder
file_list = drive.ListFile({'q': f'"{google_folder}" in parents and trashed=false'}).GetList()
length = len(file_list)

# Change working directory to data folder
os.chdir(data_folder)

# Download all files in google drive folder
count = 1
for file in file_list:
    # Start file download iteration
    output = os.path.join(data_folder, file['title'])
    if os.path.exists(output) == 0:
        # Start timing function
        iteration_start = time.time()
        # Download file
        print(f'Downloading file {count} of {length}...')
        print(f'\tTarget: {file["title"]}...')
        file.GetContentFile(file['title'])
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')
    else:
        print(f'File {count} of {length} already exists...')
    count += 1
