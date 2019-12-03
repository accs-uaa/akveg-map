# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Data from Drive
# Author: Timm Nawrocki
# Last Updated: 2019-12-03
# Usage: Must be executed in a Python 3.7 installation with Google API Python Client and PyDrive installed.
# Description: "Download Data from Drive" programmatically downloads batches of data from Google Drive. The script can be used to download spectral data processed into a Google Drive folder from Google Earth Engine.
# ---------------------------------------------------------------------------

# Import packages
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from package_GeospatialProcessing import download_from_drive
from package_GeospatialProcessing import list_from_drive
import pickle
import time

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

# Set root directory
drive = 'L:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Set data folder
data_folder = os.path.join(root_folder, 'Data/imagery/sentinel-2/unprocessed')

# Define target Google Drive folder
google_folder = '1KSwPnPWmf0PGJWM0kVX1TFCL28FyyUt2' # Beringia_Sentinel-2

# Change working directory to credentials folder
credentials_folder = os.path.join(root_folder, 'Administrative/Credentials')
os.chdir(credentials_folder)

# Create persistent credentials
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json', SCOPES)
        creds = flow.run_local_server(port=8080)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# Build a Google Drive instance
drive_service = build('drive', 'v2', credentials=creds)

# List all files in Google Drive Folder
file_id_list = list_from_drive(drive_service, google_folder)

# Subset list
file_id_subset = file_id_list[:]
total = len(file_id_subset)

# Download all files in Google Drive Folder
count = 1
for file_id in file_id_subset:

    # Get file title metadata by file id
    file_meta = drive_service.files().get(fileId=file_id).execute()
    file_title = file_meta['title']
    # Generate download file path
    output_file = os.path.join(data_folder, file_title)

    # Start download file iteration if file does not exist.
    if os.path.exists(output_file) == 0:

        # Start timing function
        iteration_start = time.time()
        # Download file
        print(f'Downloading file {count} of {total}...')
        download_from_drive(drive_service, file_id, file_title, output_file)
        # End timing
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        # Report success
        print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')

    # If file exists then skip download file iteration
    else:
        print(f'File {count} of {total} already exists...')

    # Increase count
    count += 1
