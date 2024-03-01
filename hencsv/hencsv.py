##################################################################
# How to reload this module
# import importlib
# importlib.reload(hencsv)
##################################################################
import pandas as pd
import csv
import os
import sys
import shutil
import time
import keyboard
from tabulate import tabulate

import utils as utl
import csv_commands as csvc

input_dir = utl.input_dir

input_dir2 = utl.input_dir2

output_dir = utl.output_dir

tmp_dir = utl.tmp_dir

def process_main_menu_prompt(df, filename):
    utl.clear_screen()
    
    utl.print_first_n_lines(df, filename)

    prompt = input(f"\rSelect command:\n- {csvc.command_prompts()}\n- ({csvc.default_command_prompts()})\n> ")
    return prompt.lower()

def process_file(filename):
    input_file_path, _, _, tmp_file_path = utl.file_paths(filename)

    utl.clear_screen()

    if os.path.exists(tmp_file_path):
        restore = input(f"\nTmp file found for: {filename}\n  edit original? (y/n): ")
        if restore == 'y':
            print(f"\rRestoring original input file {filename}")
            shutil.copy(input_file_path, tmp_file_path)
    else:
        shutil.copy(input_file_path, tmp_file_path)

    df = pd.read_csv(tmp_file_path) 
    
    undo_stack = []
    command_stack = []
    
    while True:
        prompt = process_main_menu_prompt(df, tmp_file_path)

        if prompt in csvc.command_registry or prompt == 'u':
            df, undo_stack, command_stack = csvc.execute_command_with_undo(prompt, df, filename, undo_stack, command_stack)
        elif prompt in csvc.default_command_registry:
            return csvc.execute_default_command(prompt, df, filename, undo_stack, command_stack)
        else:
            print("Error command not recognized.")
        time.sleep(0.6)

def display_file_list(filelist, current_filename):
    utl.clear_screen()
    print(f"Editing files in {utl.input_dir}/: ")
    
    for filename in filelist:
        if filename == current_filename:
            print(f"\033[1m> {filename}\033[0m")
        else:
            print(f"  {filename}")

def main():
    """ Read through every csv file in csv_files dir and process file
    """
    filelist = os.listdir(utl.input_dir)

    for filename in filelist:
        display_file_list(filelist, filename)
        input_file_path, _, output_file_path, tmp_file_path = utl.file_paths(filename)

        answer = input("\nPress any key to continue or 'q' to quit... ")
        if answer == 'q': return
        
        if not process_file(filename): return

        shutil.copy(tmp_file_path, output_file_path)
        print(f"\rCopied file to {output_file_path}")
        time.sleep(0.4)
                
if __name__ == "__main__":
    main()