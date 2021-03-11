# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download Files From CSV
# Author: Timm Nawrocki
# Last Updated: 2021-03-10
# Usage: Can be executed in an Anaconda Python 3.7 distribution or an ArcGIS Pro Python 3.6 distribution.
# Description: "Download Files From CSV" contacts a server to download a series of files specified in a csv table. The full path to the download must be specified in the table.
# ---------------------------------------------------------------------------

# Define a function to download files from a csv
def download_from_csv(input_table, url_column, directory):
    """
    Description: downloads set of files specified in a particular column of a csv table.
    Inputs: input_table -- csv table containing rows for download items.
            url_column -- title for column containing download urls.
            destination -- folder to store download results.
    Returned Value: Function returns status messages only. Downloaded data are stored on drive.
    Preconditions: csv tables must be generated from web application tools or manually.
    """

    # Import packages
    import datetime
    import os
    import pandas as pd
    import time
    import urllib.request

    # Import a csv file with the download urls for the Arctic DEM tiles
    download_items = pd.read_csv(input_table)

    # Initialize download count
    n = len(download_items[url_column])
    print(f'Beginning download of {n} files...')
    count = 1

    # Loop through urls in the downloadURL column and download
    for url in download_items[url_column]:
        target = os.path.join(directory, os.path.split(url)[1])
        # Download file if it does not already exist on local disk
        if os.path.exists(target) == 0:
            try:
                print(f'\tDownloading {count} of {n} files...')
                iteration_start = time.time()
                # Download data
                filedata = urllib.request.urlopen(url)
                datatowrite = filedata.read()
                with open(target, 'wb') as file:
                    file.write(datatowrite)
                    file.close()
                # End timing
                iteration_end = time.time()
                iteration_elapsed = int(iteration_end - iteration_start)
                iteration_success_time = datetime.datetime.now()
                # Report success
                print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
                print('\t----------')
            except:
                print(f'\tFile {count} of {n} not available for download. Check url.')
                print('\t----------')
        else:
            print(f'\tFile {count} of {n} already exists...')
            print('\t----------')
        # Increase counter
        count += 1

    # Report end status
    print('Finished downloading tiles.')
