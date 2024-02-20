#this program seperated the cycles in cyclic voltametery 
#the csv data file aquiered from Zahner potentiostat
# and has these columns: "Current/A", "Time/s", "Potential/V"

import pandas as pd
import numpy as np
import os
import glob
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from matplotlib.ticker import EngFormatter

REF_POTENTIAL = 0.53  # Reference potential vs. Hydrogen reference electrode

def load_data(filename, header_rows=12, sep=','):
    """Load CSV data, skipping the initial header rows."""
    try:
        df = pd.read_csv(filename, sep=sep, header=header_rows)
        return df
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None


def rename_columns(df: pd.DataFrame):
    """Rename columns for consistency and readability."""
    df.rename(columns={"Current/A": "Current", "Time/s": "Time", "Potential/V": "Potential"}, inplace=True)


def add_cycle_column(df: pd.DataFrame, starting_cycle=1):
    """Add a 'Cycle' column starting from the specified cycle."""
    df['Cycle'] = starting_cycle

def convert_potential_to_RHE(df: pd.DataFrame, ref_pot: float):
    """Convert and add a column for potential vs. RHE."""
    df['Potential (V vs. RHE)'] = df['Potential'] + ref_pot

def find_peak_indexes(df: pd.DataFrame, column_name: str):
    ''' this function find index of the peaks in a data selected column of a data frame'''
    target_array = (np.array(-df[column_name]) )
    # Find peaks
    peaks, _ = find_peaks(target_array)
    return peaks

def split_cycles(df: pd.DataFrame, peak_indexes: list):
    """Split the dataframe into cycles based on peak indexes."""
    cycles = []
    start_index = 0
    for peak in peak_indexes:
        cycles.append(df[start_index:peak+1])
        start_index = peak + 1
    cycles.append(df[start_index:])  # Add the last cycle
    return cycles

def save_and_plot_cycles(cycles, directory, filename, start_cycle=1):
    """Save each data of cycle to a CSV and plot it and save figure."""
    formatter0 = EngFormatter(unit='A')
    for i, cycle_df in enumerate(cycles[start_cycle-1:], start_cycle):
        cycle_df.to_csv(os.path.join(directory, f'Cycle{i}_{filename}'))
        plt.figure(figsize=(8, 6))
        plt.plot(cycle_df['Potential'], cycle_df['Current'], label=f'Cycle {i}')
        plt.ylabel('Current (A)')
        plt.xlabel('Potential (V vs. RHE)')
        ax = plt.gca()
        ax.yaxis.set_major_formatter(formatter0)
        plt.legend()
        plt.savefig(os.path.join(directory, f'Cycle{i}_{filename}.png'), dpi=300)
        plt.close()

def main():
    filePath = input('Input file directory:\n')
    filename = input('Input file name (including extension, e.g., .csv):\n')
    start_cycle = int(input('Enter Starting Cycle:\n'))
    full_path = os.path.join(filePath, filename)
    df = load_data(full_path)
    if df is not None:
        rename_columns(df)
        add_cycle_column(df, starting_cycle=start_cycle)
        convert_potential_to_RHE(df, REF_POTENTIAL)
        peak_indexes = find_peak_indexes(df, 'Potential')
        cycles = split_cycles(df, peak_indexes)
        save_and_plot_cycles(cycles, filePath, filename, start_cycle=start_cycle)

if __name__ == "__main__":
    main()
