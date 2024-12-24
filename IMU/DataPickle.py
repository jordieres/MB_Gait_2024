# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 10:52:15 2024

@author: marbo
"""
import pickle
import os
import pandas as pd

class DataPickle:
    """
    A unified class for loading and saving data (e.g., DataFrames, dictionaries) using pickle files.
    """

    def __init__(self, verbosity=0, output_dir='data', filename='data.pkl', load_on_init=False):
        """
        Initialize the DataPickle class with verbosity level, default output directory, filename, 
        and optionally load data upon initialization.

        Parameters:
        ----------
        verbosity : int
            Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output).
        output_dir : str
            The default directory for saving and loading pickle files.
        filename : str
            The default name for pickle files.
        load_on_init : bool, optional
            Whether to load data from the specified file immediately upon initialization.
        """
        self.verbosity = verbosity
        self.output_dir = output_dir
        self.filename = filename
        self.data = None

        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Optionally load data during initialization
        if load_on_init:
            self.load_from_pickle()

    def save_to_pickle(self, data, file_path=None, filename=None):
        """
        Saves the provided data (e.g., dictionary, DataFrame) to a pickle file.
        """
        filepath = file_path or self.output_dir
        filename = filename or self.filename
        full_path = os.path.join(filepath, filename)

        try:
            with open(full_path, 'wb') as f:
                pickle.dump(data, f)
            if self.verbosity > 0:
                print(f"Data successfully saved to {full_path}")
            if self.verbosity > 1:
                print(f"Pickle file saved with {len(data)} records (or data entries).")
        except Exception as e:
            if self.verbosity > 0:
                print(f"Failed to save data to {full_path}.")
            if self.verbosity > 1:
                print(f"Error details: {str(e)}")

    def load_from_pickle(self, file_path=None, filename=None):
        """
        Loads data (e.g., dictionary, DataFrame) from a pickle file.
        """
        filepath = file_path or self.output_dir
        filename = filename or self.filename
        full_path = os.path.join(filepath, filename)

        try:
            with open(full_path, 'rb') as f:
                self.data = pickle.load(f)
            if self.verbosity > 0:
                print(f"Data successfully loaded from {full_path}")
            if self.verbosity > 1 and isinstance(self.data, (dict, list, pd.DataFrame)):
                print(f"Loaded data contains {len(self.data)} records.")
            return self.data
        except Exception as e:
            if self.verbosity > 0:
                print(f"Failed to load data from {full_path}.")
            if self.verbosity > 1:
                print(f"Error details: {str(e)}")
            return None