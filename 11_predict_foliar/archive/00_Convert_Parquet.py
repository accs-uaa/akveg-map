import pandas as pd
import glob
import os
import time
from akutils import *

# Set root directory
drive = '/home'
root_folder = 'twnawrocki'

# Define folder structure
input_folder = os.path.join(drive, root_folder, 'data_output/covariate_tables')
parquet_folder = os.path.join(drive, root_folder, 'data_output/covariate_parquet')

# Define input files
input_files = glob.glob(f'{input_folder}/*/*.csv')

# Create parquet files if they do not already exist
count = 1
for input_file in input_files:
    # Define output folder
    grid_folder, file_name = os.path.split(input_file)
    grid_name = os.path.basename(grid_folder)
    output_folder = os.path.join(parquet_folder, grid_name)
    if os.path.exists(output_folder) == 0:
        os.mkdir(output_folder)

    # Define output file
    output_file = os.path.join(output_folder, (os.path.splitext(file_name)[0] + '.parquet'))

    if os.path.exists(output_file) == 0:
        print(f'Creating output file {count} of {len(input_files)}...')
        iteration_start = time.time()
        input_data = pd.read_csv(input_file)
        input_data.to_parquet(output_file, compression='brotli')
        end_timing(iteration_start)

    else:
        print(f'Output file {count} of {len(input_files)} already exists.')
    count += 1
