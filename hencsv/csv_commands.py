import pandas as pd
import csv
import os
import sys
import shutil

import utils as utl

default_command_registry = {}
command_registry = {}

def register_default_command(command_key):
    def decorator(command_func):
        default_command_registry[command_key] = command_func
        return command_func
    return decorator

def register_command(command_key):
    def decorator(command_func):
        input_func_name = command_func.__name__ + '_input'
        command_registry[command_key] = (command_func, input_func_name)
        return command_func
    return decorator

def execute_default_command(command_key, *args):
    if command_key in default_command_registry:
        command_func = default_command_registry[command_key]
        return command_func(*args)
    else:
        raise ValueError(f"Command '{command_key}' not found in default commands registry.")

def execute_command(command_key, df, filename):
    if command_key in command_registry:
        command_func, input_func_name = command_registry[command_key]
        if input_func_name in globals():
            input_func = globals()[input_func_name]
            args = input_func()
            return command_func(df, filename, *args), args 
        else:
            raise ValueError(f"Input function {input_func_name} not found for command {command_func.__name__}")
    else:
        raise ValueError(f"Command '{command_key}' not found in commands registry.")

def execute_command_with_undo(command_key, df, filename, undo_stack, command_stack):
    if command_key == 'u':
        df, undo_stack, command_stack = undo(df, undo_stack, command_stack)
    else: 
        old_df = df.copy()
        df, command_args = execute_command(command_key, df, filename)
        if not old_df.equals(df):
            undo_stack.append(old_df)
            command_stack.append((command_key, command_args))
    return df, undo_stack, command_stack

def command_prompts():
    max_key_length = max(len(key) for key in command_registry.keys())
    prompt = '\n- '.join([f"{command_key:<{max_key_length+1}} for {command_func.__name__}" for command_key, (command_func, _) in command_registry.items()])
    return prompt

def default_command_prompts():
    prompt = ', '.join([f"'{command_key}' to {command_func.__name__}" for command_key, command_func in default_command_registry.items()])
    prompt = "'u' to undo, " + prompt
    return prompt

def undo(df, undo_stack, command_stack):
    if undo_stack:
        df = undo_stack.pop()
        command_stack.pop()
        print("\rUndid last command")
    else:
        print("\rNothing to undo!")
    return df, undo_stack, command_stack
    
@register_default_command('s')
def save(df, filename, *args):
    utl.write_tmp_csv_file(df, filename)
    return True

@register_default_command('a')
def apply_all(df, current_filename, undo_stack, command_stack):
    input_files, _, _, tmp_files = utl.files_in_dirs()

    for filename in input_files:
        if filename != current_filename:
            input_file, _, _, tmp_file = utl.file_paths(filename)
            
            new_df = pd.read_csv(tmp_file if os.path.exists(tmp_file) else input_file)
            for command_key, args in command_stack:
                new_df = command_registry[command_key][0](new_df, filename, *args)

            save(new_df, filename)
    save(df, current_filename)
    return True

@register_default_command('sk')
def skip(*args):
    return True

@register_default_command('q')
def quit(*args):
    return False

@register_command('dsp')
def display_original(df, filename, *args):
    input_file_path, _, _, tmp_file_path = utl.file_paths(filename)
    df_original = pd.read_csv(input_file_path)
    utl.print_first_n_lines(df_original, input_file_path, n=10)
    input("\rPress any key to continue...")
    return df

def display_original_input():
    return ()

###########################################
######### CUSTOM COMMANDS BELOW ###########
###########################################
@register_command('rst')
def restore_original(df, filename, *args):
    input_file_path, _, _, tmp_file_path = utl.file_paths(filename)
    shutil.copy(input_file_path, tmp_file_path)
    df = pd.read_csv(tmp_file_path)
    print(f"\rRestored to original file: {input_file_path}")
    return df

def restore_original_input():
    return ()

@register_command('mc')
def merge_cols(df, filename, start_index, end_index, new_column_name = ''):
    # Store the columns to be merged in a separate DataFrame
    merged_columns = df.iloc[:, start_index:end_index+1]

    # Merge the specified columns, replacing NaN with an empty string
    merged_column = df.iloc[:, start_index:end_index+1].fillna('').apply(lambda row: ''.join(str(cell) for cell in row), axis=1)

    # Remove the merged columns from the DataFrame
    df = df.drop(df.columns[start_index:end_index+1], axis=1)

    # Insert the merged column into the DataFrame
    df.insert(start_index, new_column_name, merged_column)

    print("\rSuccessfully merged columns")

    return df

def merge_cols_input():
    start_index = input("\rEnter the 0-indexed start column to merge: ")
    start_index = int(start_index)
    
    end_index = input("\rEnter the 0-indexed end column to merge: ")
    end_index = int(end_index)

    new_column_name = input("\rEnter the new column name: ")

    return (start_index, end_index, new_column_name)

# Note replaces entire string if any substring matches target
@register_command('srp')
def string_replace(df, filename, target_replacement):
    target, replacement = target_replacement.split('/')
    df = df.applymap(lambda cell: replacement if target in str(cell) else cell)
    print(f"\rReplaced {target} with {replacement}")
    return df

def string_replace_input():
    target_replacement = input("\rEnter the target and replacement strings separated by a slash (/): ")
    return (target_replacement,)

# Joins columns from two separate csvs
@register_command('jn')
def join_columns(df, filename, filename2, insertion_index, start_column, end_column):

    df2 = pd.read_csv(filename2)

    df2_cols = df2.iloc[:, start_column:end_column]

    df = pd.concat([df.iloc[:, :insertion_index], df2_cols, df.iloc[:, insertion_index:]], axis=1)

    return df

def join_columns_input():
    filename2 = utl.dir_tab_completion(f"\rEnter a csv file from {utl.input_dir2} (use tab completion): ",utl.input_dir2)

    df = pd.read_csv(filename2)

    utl.print_first_n_lines(df, filename2, n=10)
    
    insertion_index = int(input(f"Enter the 0-indexed insertion point for file1: "))
    start_column = int(input(f"Enter the 0-index start column for file2: "))
    end_column = int(input(f"Enter the 0-index end column for file2: "))

    return (filename2, insertion_index, start_column, end_column)