import pickle
import os

class DataSaver:
    """
    A class to save any processed data to a file, including dictionaries.
    """

    def __init__(self, output_dir='data', filename='data.pkl', verbosity=0):
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

    def save_to_pickle(self, data):
        """
        Saves any data (e.g., dictionary, DataFrame) to a pickle file.

        Parameters:
        ----------
        data : any
            The data to save (e.g., dictionary, DataFrame).
        """
        filepath = os.path.join(self.output_dir, self.filename)
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            if self.verbosity > 0:
                print(f"Data successfully saved to {filepath}")
            if self.verbosity > 1:
                print(f"Pickle file saved with {len(data)} records (or data entries).")
        except Exception as e:
            if self.verbosity > 0:
                print(f"Failed to save data to {filepath}.")
            if self.verbosity > 1:
                print(f"Error details: {str(e)}")
