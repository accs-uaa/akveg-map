import glob
import os
import time
import pandas as pd
from akutils import *

# Set root directory
drive = 'C:/'
root_folder = 'Users/timmn'

# Define folder structure
input_folder = os.path.join(drive, root_folder, 'Downloads/test')

input_files = glob.glob(f'{input_folder}/*/*.parquet')

count = 1
for input_file in input_files:
    print(f'Reading file {count} of {len(input_files)}...')
    iteration_start = time.time()
    input_data = pd.read_parquet(input_file)
    end_timing(iteration_start)
    count += 1
