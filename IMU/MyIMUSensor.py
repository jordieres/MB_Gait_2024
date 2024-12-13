# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 14:59:52 2024

@author: marbo
"""

import numpy as np
from skinematics.imus import IMU_Base


class MyIMUSensor(IMU_Base):
    def get_data(self, in_file=None, in_data=None):
        """
        Retrieves IMU data from a file or dictionary and sets the relevant attributes.
        This method should be implemented according to the specific data format.
        """
        if in_file:
            # For example, read data from a file (e.g., CSV, TXT)
            self.source = in_file
            # Load data using numpy, assuming CSV format with columns for acc, omega, and mag
            # Example of reading from a CSV file:
            data = np.loadtxt(in_file, delimiter=',')
            self.acc = data[:, :3]  # First 3 columns for acceleration
            self.omega = data[:, 3:6]  # Next 3 columns for angular velocity
            if data.shape[1] >= 9:
                self.mag = data[:, 6:9]  # Optional: Next 3 columns for magnetic field
            else:
                self.mag = np.zeros_like(self.acc)  # If mag data is not available, set to zero
            self.rate = 50 
        elif in_data:
            # If data is passed directly as a dictionary

            
            self.rate = 50
            self.acc= in_data['acc']
            self.omega = in_data['omega']
            if 'mag' in in_data.keys():
                self.mag = in_data['mag']
            self.source = None
            self._set_info()
            
        else:
            raise ValueError("Must provide either in_file or in_data")
            
    