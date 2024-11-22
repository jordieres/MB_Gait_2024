import pandas as pd
import numpy as np

class Interpolator:
    def __init__(self, data_dict, verbosity=0):
        """
        Initialize the Interpolator with the given data dictionary.
        
        :param data_dict: Dictionary containing the data (e.g., accelerometer, pressure data).
        :param verbosity: Verbosity level (0: silent, 1: basic, 2: detailed).
        """
        self.data_dict = data_dict
        self.left_keys = [key for key in data_dict if "left" in key]
        self.right_keys = [key for key in data_dict if "right" in key]
        self.verbosity = verbosity

        if self.verbosity >= 1:
            print(f"Interpolator initialized with verbosity level {self.verbosity}.")

    def interpolate_data(self):
        """
        Interpolates the data in the group (left or right) with fewer data points.
        After interpolation, both groups (left and right) will have the same number of data points.
        """
        # Calculate the number of data points in each group
        left_count = len(self.data_dict['pressure_heel_left'])
        right_count = len(self.data_dict['pressure_heel_right'])

        if self.verbosity >= 2:
            print(f"Left count: {left_count}, Right count: {right_count}")

        # Determine which group has fewer data points
        if left_count > right_count:
            target_group = self.right_keys
            target_count = left_count
        else:
            target_group = self.left_keys
            target_count = right_count

        if self.verbosity >= 1:
            print(f"Interpolating {len(target_group)} keys in the group with fewer data points.")

        # Interpolate data for the group with fewer data points
        for key in target_group:
            if self.verbosity >= 2:
                print(f"Processing key: {key}")

            if len(self.data_dict[key].keys()) == 3:
                for sub_key in self.data_dict[key].keys():
                    start_time = self.data_dict[key][sub_key]['_time'].min()
                    end_time = self.data_dict[key][sub_key]['_time'].max()

                    # Convert the min and max datetime to Unix timestamp
                    start_timestamp = start_time.timestamp()
                    end_timestamp = end_time.timestamp()

                    # Create a new index with evenly spaced values
                    new_index_numeric = np.linspace(start_timestamp, end_timestamp, target_count)

                    # Convert the numeric timestamps back to datetime
                    new_index = pd.to_datetime(new_index_numeric, unit='s')

                    # Interpolate the '_value' column
                    interpolated_values = np.interp(new_index_numeric, 
                                                    self.data_dict[key][sub_key]['_time'].values.astype(np.int64) / 10**9, 
                                                    self.data_dict[key][sub_key]['_value'])

                    # Create the new dataframe with interpolated data
                    sub_key_interpolated = pd.DataFrame({
                        '_time': new_index,
                        '_value': interpolated_values
                    })
                    
                    # Reindex and update data
                    self.data_dict[key][sub_key] = self.data_dict[key][sub_key].reindex(range(len(sub_key_interpolated['_time'])))
                    self.data_dict[key][sub_key]['_time'] = sub_key_interpolated['_time'].reset_index(drop=True)
                    self.data_dict[key][sub_key]['_value'] = sub_key_interpolated['_value'].reset_index(drop=True)

                    if self.verbosity >= 2:
                        print(f"Sub-key {sub_key} processed with {len(sub_key_interpolated['_time'])} interpolated values.")
            else:
                start_time = self.data_dict[key]['_time'].min()
                end_time = self.data_dict[key]['_time'].max()

                # Convert the min and max datetime to Unix timestamp
                start_timestamp = start_time.timestamp()
                end_timestamp = end_time.timestamp()

                # Create a new index with evenly spaced values
                new_index_numeric = np.linspace(start_timestamp, end_timestamp, target_count)

                # Convert the numeric timestamps back to datetime
                new_index = pd.to_datetime(new_index_numeric, unit='s')

                # Interpolate the '_value' column
                interpolated_values = np.interp(new_index_numeric, 
                                                self.data_dict[key]['_time'].values.astype(np.int64) / 10**9, 
                                                self.data_dict[key]['_value'])

                # Create the new dataframe with interpolated data
                key_interpolated = pd.DataFrame({
                    '_time': new_index,
                    '_value': interpolated_values
                })
                
                # Reindex and update data
                self.data_dict[key] = self.data_dict[key].reindex(range(len(key_interpolated['_time'])))
                self.data_dict[key]['_time'] = key_interpolated['_time'].reset_index(drop=True)
                self.data_dict[key]['_value'] = key_interpolated['_value'].reset_index(drop=True)

                if self.verbosity >= 2:
                    print(f"Key {key} processed with {len(key_interpolated['_time'])} interpolated values.")

        if self.verbosity >= 1:
            print("Interpolation complete.")

    def get_interpolated_data(self):
        """
        Returns the interpolated data dictionary.
        
        :return: Interpolated data dictionary.
        """
        return self.data_dict