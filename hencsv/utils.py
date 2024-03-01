import os
import pandas as pd
import readline
import glob
from tabulate import tabulate

input_dir = 'csv_files'

input_dir2 = 'csv_files_2'

output_dir = 'csv_output_files'

tmp_dir = 'tmp_csv_files'

def file_paths(filename):
    paths = tuple([os.path.join(directory, filename) for directory in [input_dir, input_dir2, output_dir, tmp_dir]])
    return paths

def files_in_dirs():
    files = tuple(os.listdir(directory) for directory in [input_dir, input_dir2, output_dir, tmp_dir])
    return files

def read_csv_file(filename):
    input_file, _, _, _ = file_paths(filename)
    return pd.read_csv(input_file)

def write_csv_file(df, filename):
    _, _, output_file, _ = file_paths(filename)
    df.to_csv(output_file, index=False)
    print(f"\rSaved to {output_file}")

def write_tmp_csv_file(df, filename):
    _, _, _, tmp_file = file_paths(filename)
    df.to_csv(tmp_file, index=False)
    print(f"\rSaved to {tmp_file}")

def print_first_n_lines(df, input_file, n = 20):
    
    print(f"\nFirst {n} lines of {input_file}:")
    
    print(tabulate(df.head(n), headers='keys', tablefmt='pretty'))

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')