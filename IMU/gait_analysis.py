# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 17:50:59 2024

@author: marbo
"""

import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D
from scipy import signal

class GaitAnalysis:
    def __init__(self, data, verbosity=0):
        """
        Initialize the GaitAnalysis class with the provided data.
        
        Args:
            data (pd.DataFrame): The dataframe containing sensor data.
            verbosity (int): Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output).
        """
        self.data = data
        self.verbosity = verbosity

    def preprocess_data(self):
        """
        Preprocess and separate data based on sensor types and foot placement (Right/Left).
        
        This method filters the data to create separate DataFrames for acceleration, gyroscope, 
        magnetometer, and pressure data for both the right and left foot, stored in a dictionary.
        
        Returns:
            dict: A dictionary containing the processed DataFrames.
        """
        if self.verbosity > 0:
            print("Starting data preprocessing...")

        data_dict = {}

        # Separate acceleration data for each foot
        data_dict['acc_data_right'] = {
            'x': self.data[(self.data['_field'] == 'Ax') & (self.data['Foot'] == 'Right')],
            'y': self.data[(self.data['_field'] == 'Ay') & (self.data['Foot'] == 'Right')],
            'z': self.data[(self.data['_field'] == 'Az') & (self.data['Foot'] == 'Right')],
        }
        data_dict['acc_data_left'] = {
            'x': self.data[(self.data['_field'] == 'Ax') & (self.data['Foot'] == 'Left')],
            'y': self.data[(self.data['_field'] == 'Ay') & (self.data['Foot'] == 'Left')],
            'z': self.data[(self.data['_field'] == 'Az') & (self.data['Foot'] == 'Left')],
        }
        
        # Separate gyroscope data for each foot
        data_dict['gyro_data_right'] = {
            'x': self.data[(self.data['_field'] == 'Gx') & (self.data['Foot'] == 'Right')],
            'y': self.data[(self.data['_field'] == 'Gy') & (self.data['Foot'] == 'Right')],
            'z': self.data[(self.data['_field'] == 'Gz') & (self.data['Foot'] == 'Right')],
        }
        data_dict['gyro_data_left'] = {
            'x': self.data[(self.data['_field'] == 'Gx') & (self.data['Foot'] == 'Left')],
            'y': self.data[(self.data['_field'] == 'Gy') & (self.data['Foot'] == 'Left')],
            'z': self.data[(self.data['_field'] == 'Gz') & (self.data['Foot'] == 'Left')],
        }
        
        # Separate magnetometer data for each foot
        data_dict['magnetometer_data_right'] = {
            'x': self.data[(self.data['_field'] == 'Mx') & (self.data['Foot'] == 'Right')],
            'y': self.data[(self.data['_field'] == 'My') & (self.data['Foot'] == 'Right')],
            'z': self.data[(self.data['_field'] == 'Mz') & (self.data['Foot'] == 'Right')],
        }
        data_dict['magnetometer_data_left'] = {
            'x': self.data[(self.data['_field'] == 'Mx') & (self.data['Foot'] == 'Left')],
            'y': self.data[(self.data['_field'] == 'My') & (self.data['Foot'] == 'Left')],
            'z': self.data[(self.data['_field'] == 'Mz') & (self.data['Foot'] == 'Left')],
        }
        
        # Separate pressure data for each foot
        data_dict['pressure_heel_right'] = self.data[(self.data['_field'] == 'S0') & (self.data['Foot'] == 'Right')]
        data_dict['pressure_heel_left'] = self.data[(self.data['_field'] == 'S0') & (self.data['Foot'] == 'Left')]
        
        data_dict['pressure_toe_1_right'] = self.data[(self.data['_field'].isin(['S1'])) & (self.data['Foot'] == 'Right')]
        data_dict['pressure_toe_1_left'] = self.data[(self.data['_field'].isin(['S1'])) & (self.data['Foot'] == 'Left')]
        data_dict['pressure_toe_2_right'] = self.data[(self.data['_field'].isin(['S2'])) & (self.data['Foot'] == 'Right')]
        data_dict['pressure_toe_2_left'] = self.data[(self.data['_field'].isin(['S2'])) & (self.data['Foot'] == 'Left')]

        # Verbose output
        if self.verbosity > 0:
            print("Data preprocessing completed.")
        
        if self.verbosity > 1:
            for key in data_dict:
                print(f"{key}: {len(data_dict[key])} records")

        return data_dict

    def plot_data(self, data_dict):
        # Get the all values for Left and Right Foot Heel Pressure (S0)
        pressure_heel_left = data_dict['pressure_heel_left']
        pressure_heel_right = data_dict['pressure_heel_right']
        
        # Plotting the last 250 values for both left and right foot
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('Heel Pressure (S0) - Left and Right Foot', fontsize=16)
        
        # Plot Left Foot Heel Pressure S0 values over time
        ax.plot(pressure_heel_left['_time'], pressure_heel_left['_value'], label='Left Foot Heel Pressure S0', color='purple')
        
        # Plot Right Foot Heel Pressure S0 values over time
        ax.plot(pressure_heel_right['_time'], (pressure_heel_right['_value']), label='Right Foot Heel Pressure S0', color='green')
        
        # Customize plot
        ax.set_xlabel('Time')
        ax.set_ylabel('Heel Pressure (S0)')
        ax.legend(loc='upper right')
        ax.grid(True)
        
        plt.show()
        

        
        pressure_heel_left_closer = data_dict['pressure_heel_left'][4100:4900]
        pressure_heel_right_closer = data_dict['pressure_heel_right'][250:1750]
        
        # Plotting the last 250 values for both left and right foot
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('Heel Pressure (S0) - A closer look', fontsize=16)
        
        # Plot Left Foot Heel Pressure S0 values over time
        ax.plot(pressure_heel_left_closer['_time'], pressure_heel_left_closer['_value'], label='Left Foot Heel Pressure S0', color='purple')
        
        # Plot Right Foot Heel Pressure S0 values over time
        ax.plot(pressure_heel_right_closer['_time'], (pressure_heel_right_closer['_value']), label='Right Foot Heel Pressure S0', color='green')
        
        # Customize plot
        ax.set_xlabel('Time')
        ax.set_ylabel('Heel Pressure (S0)')
        ax.legend(loc='upper right')
        ax.grid(True)
        
        plt.show()
            
       
        
        
        
       

        # Get the first all values for Right Foot Heel Pressure (S0) and toe pressure (S1)
        
        pressure_heel_right = data_dict['pressure_heel_right']
        pressure_toe_right = data_dict['pressure_toe_1_right']
        
        
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('Heel Pressure (S0) and tow pressure (S1) for right foot', fontsize=16)
        
        # Plot Left Foot Heel Pressure S0 values over time
        ax.plot( pressure_heel_right['_time'],pressure_heel_right['_value'], label='Right Foot Heel Pressure S0', color='purple')
        
        # Plot Right Foot Heel Pressure S0 values over time
        ax.plot(pressure_toe_right['_time'], (pressure_toe_right['_value']), label='Right Foot Toe Pressure S1', color='green')
        
        # Customize plot
        ax.set_xlabel('Time')
        ax.set_ylabel('Heel and Toe Pressure (S0 and S1)')
        ax.legend(loc='upper right')
        ax.grid(True)
        
        plt.show()
        
        # Get the first 500 values for Right Foot Heel Pressure (S0) and toe pressure (S1)
        
        pressure_heel_right_first_500 = data_dict['pressure_heel_right'].head(500)
        pressure_toe_right_first_500 = data_dict['pressure_toe_1_right'].head(500)
        
        
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('Heel Pressure (S0) and tow pressure (S1) for right foot first 500', fontsize=16)
        
        # Plot Left Foot Heel Pressure S0 values over time
        ax.plot( pressure_heel_right_first_500['_time'],pressure_heel_right_first_500['_value'], label='Right Foot Heel Pressure S0', color='purple')
        
        # Plot Right Foot Heel Pressure S0 values over time
        ax.plot(pressure_toe_right_first_500['_time'], (pressure_toe_right_first_500['_value']), label='Right Foot Toe Pressure S1', color='green')
        
        # Customize plot
        ax.set_xlabel('Time')
        ax.set_ylabel('Heel and Toe Pressure (S0 and S1) first 500')
        ax.legend(loc='upper right')
        ax.grid(True)
        
        plt.show()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('Heel Pressure (S0) and tow pressure (S1) for right foot first 50', fontsize=16)
        
        # Plot Left Foot Heel Pressure S0 values over time
        ax.plot( pressure_heel_right_first_500['_time'][:100],pressure_heel_right_first_500['_value'][:100]-281, label='Right Foot Heel Pressure S0', color='purple')
        
        # Plot Right Foot Heel Pressure S0 values over time
        ax.plot(pressure_toe_right_first_500['_time'][:100], (pressure_toe_right_first_500['_value'][:100]), label='Right Foot Toe Pressure S1', color='green')
        
        # Customize plot
        ax.set_xlabel('Time')
        ax.set_ylabel('Heel and Toe Pressure (S0 and S1) first 50')
        ax.legend(loc='upper right')
        ax.grid(True)
                # Increase the number of x-axis ticks for better granularity
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=10, maxticks=20))  # Adjust the number of ticks
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))  # Format to hours, minutes, and seconds
        
        plt.xticks(rotation=45)  # Rotate labels for better readability
        plt.tight_layout()
        plt.show()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data_dict['acc_data_left']['x']['_time'][:500], data_dict['acc_data_left']['x']['_value'][:500], label='Acceleration X', color='r')
        ax.plot(data_dict['acc_data_left']['y']['_time'][:500], data_dict['acc_data_left']['y']['_value'][:500], label='Acceleration Y', color='g')
        ax.plot(data_dict['acc_data_left']['z']['_time'][:500], data_dict['acc_data_left']['z']['_value'][:500], label='Acceleration Z', color='b')
        ax.set_xlabel('Time')
        ax.set_ylabel('Acceleration')
        plt.title("Acceleration Over Time in X, Y, Z")
        plt.legend()
        plt.grid(True)
        plt.show()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data_dict['gyro_data_left']['x']['_time'][:500], data_dict['gyro_data_left']['x']['_value'][:500], label='Gyroscope values X', color='r')
        ax.plot(data_dict['gyro_data_left']['y']['_time'][:500], data_dict['gyro_data_left']['y']['_value'][:500], label='Gyroscope values Y', color='g')
        ax.plot(data_dict['gyro_data_left']['z']['_time'][:500], data_dict['gyro_data_left']['z']['_value'][:500], label='Gyroscope values Z', color='b')
        ax.set_xlabel('Time')
        ax.set_ylabel('Gyroscope values')
        plt.title("Gyroscope values")
        plt.legend()
        plt.grid(True)
        plt.show()

        # Example values for magnetometer data
        mag_x = data_dict['magnetometer_data_left']['x']['_value'][:7000]
        mag_y = data_dict['magnetometer_data_left']['y']['_value'][:7000]
        mag_z = data_dict['magnetometer_data_left']['z']['_value'][:7000]
        
        # Calculate the heading (yaw angle) in radians and then convert to degrees
        heading = np.arctan2(mag_y, mag_x)  # Compute the heading
        heading_degrees = np.degrees(heading)  # Convert to degrees for easier interpretation
        
        time_values = data_dict['magnetometer_data_left']['x']['_time'][:7000]  # Assuming you have time data
        plt.figure(figsize=(12, 6))
        plt.plot(time_values, mag_x, label='Magnetometer X')
        plt.plot(time_values, mag_y, label='Magnetometer Y')
        plt.plot(time_values, mag_z, label='Magnetometer Z')
        plt.xlabel('Time')
        plt.ylabel('Magnetic Field Strength (µT)')
        plt.title('Magnetometer Data for Left Foot')
        plt.legend()
        plt.grid(True)
        plt.show()
        
        
# =============================================================================
# 
#     def detect_steps(self):
#         """
#         Detect steps using vertical acceleration data (Az) and calculate cadence.
#         """
#         az_right = self.acc_data_right[][].values.astype(float)
#         az_left = self.acc_data_left[self.acc_data_left['_field'] == 'Az']['_value'].values.astype(float)
#         # Detect peaks in vertical acceleration (Az) corresponding to foot strikes
#         print(az_right)
#         plt.plot(self.acc_data_right[self.acc_data_right['_field'] == 'Az']['_value'].astype(float), label='Az Right Foot', color='blue')
#     
#                
#         self.peaks, _ = find_peaks(az_right, height=0.5, distance=50)  # Adjust height and distance thresholds
#         self.step_times = self.time[self.peaks]
#         step_intervals = np.diff(self.step_times)
#     
#         # Calculate cadence (steps per minute)
#         self.cadence = 60 / np.mean(step_intervals) if len(step_intervals) > 0 else 0
#         return self.cadence
# =============================================================================
# =============================================================================

# =============================================================================
#     def calculate_stride_length_and_speed(self):
#         """
#         Calculate stride length and walking speed based on acceleration data.
#         """
#         az = self.acc_data[self.acc_data['_field'] == 'Az']['_value'].values.astype(float)
# 
#         # Estimate displacement (simplified as integration of acceleration)
#         displacement = np.trapz(az[self.peaks])
#         self.stride_length = displacement / len(self.peaks) if len(self.peaks) > 0 else 0
# 
#         # Speed = Stride Length * Cadence
#         self.speed = self.stride_length * self.cadence / 60  # in meters per second
#         return self.stride_length, self.speed
# 
#     def analyze_foot_pressure(self):
#         """
#         Analyze foot pressure data to determine footstrike pattern (heel, midfoot, forefoot).
#         """
#         pressure_sensors = ['S0', 'S1', 'S2']
#         pressure_dict = {}
# 
#         # Extract pressure sensor data (S0, S1, S2)
#         for sensor in pressure_sensors:
#             pressure_dict[sensor] = self.pressure_data[self.pressure_data['_field'] == sensor]['_value'].values
# 
#         # Determine footstrike pattern
#         footstrike_pattern = []
#         for i in range(len(self.time)):
#             if pressure_dict['S0'][i] > pressure_dict['S1'][i] and pressure_dict['S0'][i] > pressure_dict['S2'][i]:
#                 footstrike_pattern.append('heel strike')
#             elif pressure_dict['S1'][i] > pressure_dict['S0'][i] and pressure_dict['S1'][i] > pressure_dict['S2'][i]:
#                 footstrike_pattern.append('midfoot strike')
#             else:
#                 footstrike_pattern.append('forefoot strike')
# 
#         # Calculate the percentage of each footstrike type
#         heel_strike_percent = footstrike_pattern.count('heel strike') / len(footstrike_pattern) * 100
#         midfoot_strike_percent = footstrike_pattern.count('midfoot strike') / len(footstrike_pattern) * 100
#         forefoot_strike_percent = footstrike_pattern.count('forefoot strike') / len(footstrike_pattern) * 100
# 
#         return heel_strike_percent, midfoot_strike_percent, forefoot_strike_percent
# 
#     def plot_gait_data(self):
#         """
#         Plot relevant gait data (e.g., acceleration, footstrike points) for visual analysis.
#         """
#         az = self.acc_data[self.acc_data['_field'] == 'Az']['_value'].values
# 
#         # Plot vertical acceleration and detected foot strikes
#         plt.figure(figsize=(10, 6))
#         plt.plot(self.time, az, label='Vertical Acceleration (Az)')
#         plt.plot(self.time[self.peaks], az[self.peaks], 'x', label='Foot Strikes')
#         plt.title('Vertical Acceleration and Foot Strikes')
#         plt.xlabel('Time (s)')
#         plt.ylabel('Acceleration (m/s^2)')
#         plt.legend()
#         plt.show()
# 
#     def plot_pressure_distribution(self):
#         """
#         Plot pressure sensor data to visually inspect foot pressure distribution.
#         """
#         pressure_sensors = ['S0', 'S1', 'S2']
#         pressure_dict = {}
# 
#         for sensor in pressure_sensors:
#             pressure_dict[sensor] = self.pressure_data[self.pressure_data['_field'] == sensor]['_value'].values
# 
#         plt.figure(figsize=(10, 6))
#         for sensor in pressure_sensors:
#             plt.plot(self.time, pressure_dict[sensor], label=sensor)
#         plt.legend()
#         plt.title('Foot Pressure Distribution')
#         plt.xlabel('Time')
#         plt.ylabel('Pressure')
#         plt.show()
# =============================================================================
