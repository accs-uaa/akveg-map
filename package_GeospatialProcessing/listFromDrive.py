# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# List Files from Drive
# Author: Timm Nawrocki
# Last Updated: 2019-12-03
# Usage: Must be executed in a Python 3.7 environment with Google Drive API v2.
# Description: "List Files From Drive" is a function that creates a list of all files in a Google Drive folder by id.
# ---------------------------------------------------------------------------

# Define a function to create a list of all file IDs within a folder
def list_from_drive(service, folder_id):
    """
    Description: creates a list of files by ID belonging to a Google Drive folder.
    Inputs: service -- Drive API service instance.
            folder_id -- ID of the folder from which to list files.
    """
    # Create empty list to store file IDs
    file_id_list = []
    page_token = None
    # Search folder for files
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            children = service.children().list(folderId=folder_id, **param).execute()
            for child in children.get('items', []):
                file_id_list = file_id_list + [child['id']]
            page_token = children.get('nextPageToken')
            if not page_token:
                break
        except:
            print('An error occurred.')
            break
    # Return file ID list
    return file_id_list
