# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download File from Google Drive
# Author: Timm Nawrocki
# Last Updated: 2019-12-03
# Usage: Must be executed in a Python 3.7 environment with Google Drive API v2.
# Description: "Download File From Google Drive" is a function that downloads a file from Google Drive by file id.
# ---------------------------------------------------------------------------

# Define a function to download data files from Google Drive
def download_from_drive(service, file_id, file_title, output_file):
    """
    Description: downloads a file from Google Drive by file ID.
    Inputs: file_id -- ID of the file to download.
            output_directory -- directory in which to save the downloaded file.
    Returned Value: Return a files to local disk for the file on Google Drive
    Preconditions: files containing imagery tiles must have been exported to Google Drive from Google Earth Engine
    """

    # Import packages
    from googleapiclient.http import MediaIoBaseDownload
    import io

    # Create request, file handler, and downloader
    print(f'\tSaving {file_title}...')
    request = service.files().get_media(fileId=file_id)
    file_handler = io.FileIO(output_file, 'wb')
    downloader = MediaIoBaseDownload(file_handler, request, chunksize=16384*16384)
    # Download file and report progress
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print('\t\tDownload {0}%...'.format(int(status.progress() * 100)))
    file_handler.close()