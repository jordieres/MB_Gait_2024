# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 19:30:00 2024

@author: marbo
"""
import pickle
import os
import pandas as pd

class DataLoader:
    """
    A class to load a saved DataFrame from a pickle file.
    """

    def __init__(self, verbosity=0):
        """
        Initialize the DataLoader with verbosity level.

        Parameters:
        ----------
        verbosity : int
            Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output).
        """
        self.verbosity = verbosity

    def load_from_pickle(self, file_path=None, filename=''):
        """
        Loads the DataFrame from a pickle file. Allows specifying file path and name.

        Parameters:
        ----------
        file_path : str, optional
            The directory where the file is located. Default is the current directory.
        filename : str, optional
            The name of the pickle file. Default is 'movements_df.pkl'.

        Returns:
        -------
        pd.DataFrame or None
            The loaded DataFrame if successful, or None if loading failed.
        """
        if file_path is None:
            file_path = os.getcwd()  # Default to current directory if no path is provided
            
        filepath = os.path.join(file_path, filename)
        
        try:
            with open(filepath, 'rb') as f:
                df = pickle.load(f)
            if self.verbosity > 0:
                print(f"DataFrame successfully loaded from {filepath}")
            if self.verbosity > 1:
                print(f"Pickle file contains {len(df)} records.")
            return df
        except Exception as e:
            if self.verbosity > 0:
                print(f"Failed to load DataFrame from {filepath}.")
            if self.verbosity > 1:
                print(f"Error details: {str(e)}")
            return None