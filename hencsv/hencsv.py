import pandas as pd
import csv
import os
import sys
import shutil
import time

import utils as utl
import csv_commands as csvc

def process_main_menu_prompt(df, filename):
    utl.clear_screen()
    utl.print_first_n_lines(df, filename)
    prompt = input(f"\rSelect command:\n- {csvc.command_prompts()}\n- ({csvc.default_command_prompts()})\n> ")
    return prompt.lower()

def process_file(filename):
    _, _, _, tmp_file_path = utl.file_paths(filename)
    df = pd.read_csv(tmp_file_path) 
    undo_stack, command_stack = [], []
    
    while True:
        prompt = process_main_menu_prompt(df, tmp_file_path)
        if prompt in csvc.command_registry or prompt == 'u':
            df, undo_stack, command_stack = csvc.execute_command_with_undo(prompt, df, filename, undo_stack, command_stack)
        elif prompt in csvc.default_command_registry:
            return csvc.execute_default_command(prompt, df, filename, undo_stack, command_stack)
        else:
            print("Error command not recognized.")
        time.sleep(0.6)

def display_file_menu(filelist, current_filename):
    utl.clear_screen()
    print(f"Editing files in {utl.input_dir}/: ")
    
    for filename in filelist:
        print(f"\033[1m> {filename}\033[0m" if filename == current_filename else f"  {filename}")
    
    answer = input("\nPress any key to continue or 'q' to quit... ")
    return False if answer == 'q' else True

def main():
    """ Read through every csv file in csv_files dir and process file
    """
    filelist = os.listdir(utl.input_dir)

    for filename in filelist:
        if not display_file_menu(filelist, filename): return
        if not process_file(filename): return
        utl.copy_tmp_csv_to_output_dir(filename)
        time.sleep(0.4)
                
if __name__ == "__main__":
    main()