# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 18:56:58 2024

@author: marbo
"""
import pickle
import os

class DataSaver:
    """
    A class to save the processed movement DataFrame to a file.
    """

    def __init__(self, output_dir='data', filename='movements_df.pkl', verbosity=0):
        """
        Initialize the DataSaver with a default output directory, file name, and verbosity level.

        Parameters:
        ----------
        output_dir : str
            The directory where the file should be saved.
        filename : str
            The name of the pickle file.
        verbosity : int
            Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output).
        """
        self.output_dir = output_dir
        self.filename = filename
        self.verbosity = verbosity

        # Create the directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_to_pickle(self, df):
        """
        Saves the DataFrame to a pickle file.

        Parameters:
        ----------
        df : pd.DataFrame
            The DataFrame to save.
        """
        filepath = os.path.join(self.output_dir, self.filename)
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(df, f)
            if self.verbosity > 0:
                print(f"DataFrame successfully saved to {filepath}")
            if self.verbosity > 1:
                print(f"Pickle file saved with {len(df)} records.")
        except Exception as e:
            if self.verbosity > 0:
                print(f"Failed to save DataFrame to {filepath}.")
            if self.verbosity > 1:
                print(f"Error details: {str(e)}")
