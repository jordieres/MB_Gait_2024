# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 17:50:59 2024

@author: marbo
"""


import pandas as pd
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D
from scipy import signal
import plotly.graph_objects as go
from data_processor import DataProcessor


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
        self.data_processor = DataProcessor(self.data, self.verbosity)

    
    def plot_data(self, data_dict):

         # Plot 1: Heel Pressure (S0) - Left and Right Foot
         fig1 = go.Figure()
         fig1.add_trace(go.Scatter(
             x=data_dict['left']['_time'], 
             y=data_dict['left']['S2'], 
             mode='lines', 
             name='Left Foot Heel Pressure S2', 
             line=dict(color='purple')
         ))
         fig1.add_trace(go.Scatter(
             x=data_dict['right']['_time'], 
             y=data_dict['right']['S2'], 
             mode='lines', 
             name='Right Foot Heel Pressure S0', 
             line=dict(color='green')
         ))
         fig1.update_layout(
             title='Heel Pressure (S0) - Left and Right Foot',
             xaxis_title='Time',
             yaxis_title='Heel Pressure (S0)',
             legend=dict(x=0.8, y=1),
             template='plotly_white'
         )
         fig1.show()
     
        
     
         # Plot 3: Heel and Toe Pressure (S0 and S1) for Right Foot
         fig3 = go.Figure()
         fig3.add_trace(go.Scatter(
             x=data_dict['right']['_time'], 
             y=data_dict['right']['S0'], 
             mode='lines', 
             name='Right Foot Heel Pressure S0', 
             line=dict(color='purple')
         ))
         fig3.add_trace(go.Scatter(
             x=data_dict['right']['_time'], 
             y=data_dict['right']['S1'], 
             mode='lines', 
             name='Right Foot Toe Pressure S1', 
             line=dict(color='green')
         ))
         fig3.update_layout(
             title='Heel Pressure (S0) and Toe Pressure (S1) for Right Foot',
             xaxis_title='Time',
             yaxis_title='Heel and Toe Pressure (S0 and S1)',
             legend=dict(x=0.8, y=1),
             template='plotly_white'
         )
         fig3.show()

    
        # Plot 4: Acceleration Data for Left Foot
         fig4 = go.Figure()
         fig4.add_trace(go.Scatter(
            x=data_dict['left']['_time'], 
            y=data_dict['left']['Ax'],
            mode='lines', 
            name='Acceleration X', 
            line=dict(color='red')
        ))
         fig4.add_trace(go.Scatter(
            x=data_dict['left']['_time'], 
            y=data_dict['left']['Ay'],
            mode='lines', 
            name='Acceleration Y', 
            line=dict(color='green')
        ))
         fig4.add_trace(go.Scatter(
            x=data_dict['left']['_time'], 
            y=data_dict['left']['Az'],
            mode='lines', 
            name='Acceleration Z', 
            line=dict(color='blue')
        ))
         fig4.update_layout(
            title='Acceleration Over Time in X, Y, Z',
            xaxis_title='Time',
            yaxis_title='Acceleration',
            legend=dict(x=0.8, y=1),
            template='plotly_white'
        )
         fig4.show()
    
        # Plot 5: Gyroscope Data for Left Foot
         fig5 = go.Figure()
         fig5.add_trace(go.Scatter(
             x=data_dict['left']['_time'], 
             y=data_dict['left']['Gx'],
            mode='lines', 
            name='Gyroscope X', 
            line=dict(color='red')
        ))
         fig5.add_trace(go.Scatter(
             x=data_dict['left']['_time'], 
             y=data_dict['left']['Gy'],
            mode='lines', 
            name='Gyroscope Y', 
            line=dict(color='green')
        ))
         fig5.add_trace(go.Scatter(
             x=data_dict['left']['_time'], 
             y=data_dict['left']['Gz'],
            mode='lines', 
            name='Gyroscope Z', 
            line=dict(color='blue')
        ))
         fig5.update_layout(
            title='Gyroscope Values',
            xaxis_title='Time',
            yaxis_title='Gyroscope',
            legend=dict(x=0.8, y=1),
            template='plotly_white'
        )
         fig5.show()
    
        # Plot 6: Magnetometer Data and Heading
         fig6 = go.Figure()
         mag_x = data_dict['left']['Mx']
         mag_y = data_dict['left']['My']
         mag_z = data_dict['left']['Mz']
         time_values = data_dict['left']['_time']
    
         fig6.add_trace(go.Scatter(
            x=time_values, 
            y=mag_x, 
            mode='lines', 
            name='Magnetometer X', 
            line=dict(color='red')
        ))
         fig6.add_trace(go.Scatter(
            x=time_values, 
            y=mag_y, 
            mode='lines', 
            name='Magnetometer Y', 
            line=dict(color='green')
        ))
         fig6.add_trace(go.Scatter(
            x=time_values, 
            y=mag_z, 
            mode='lines', 
            name='Magnetometer Z', 
            line=dict(color='blue')
        ))
         fig6.update_layout(
            title='Magnetometer Data for Left Foot',
            xaxis_title='Time',
            yaxis_title='Magnetic Field Strength (µT)',
            legend=dict(x=0.8, y=1),
            template='plotly_white'
        )
         fig6.show()
        
     

 
    def cadence(self):
        """
        Detect steps using pressure data (S2) and calculate cadence for both feet.
    
        Returns:
        - cadence_dict: A dictionary containing the average cadence for each foot.
        """
        # Initialize dictionary to store cadence for each foot
        cadence_dict = {}
        
        # Iterate over both feet
        for foot in ['left', 'right']:
            if self.verbosity > 1:
                
                print(f"\nProcessing cadence data for {foot} foot...")
    
            # Extract the heel pressure data (S2) and time data
            S2 = self.data[foot]['S2'].values  # Convert to numpy array
            time = pd.to_datetime(self.data[foot]['_time']).astype('int64') / 1e9  # Convert time to seconds
    
            # Detect peaks in the S2 data (adjust prominence as needed)
            peaks, _ = find_peaks(S2, prominence=50)  # Adjust prominence for clear peaks
    
            # Calculate time differences between consecutive peaks
            peak_times = time[peaks]
            time_differences = np.diff(peak_times)  # Time per step (in seconds)
    
            # Check for valid step detection
            if len(time_differences) == 0:
                cadence_dict[foot] = None
                if self.verbosity > 1:
                    print(f"No steps detected for {foot} foot.")
                continue
    
            # Calculate average time per step (mean time difference)
            avg_time_per_step = np.mean(time_differences)
    
            # Calculate cadence (steps per minute)
            cadence = 60 / avg_time_per_step
            cadence_dict[foot] = cadence
    
            if self.verbosity > 1:
                print(f"Cadence for {foot} foot: {cadence:.2f} steps per minute.")
        
   
  
        return cadence_dict

         
    def calculate_step_length(self):
        """
        Calculate the average step length for each foot.
    
        Returns:
        - dict_step_length: A dictionary containing the average step length (in meters) for each foot.
        """
        # Dictionary to store the average step length for each foot
        dict_step_length = {}
    
        # Get the cadence data for each foot using the previous function
        cadence_dict = self.cadence()
    
        # Iterate over both feet
        print()
        for foot in ['left', 'right']:
            if self.verbosity > 1:
                print(f"\nCalculating step length for {foot} foot...")
    
            # Retrieve latitude and longitude data for the foot
            latitudes = self.data[foot]['lat']
            longitudes = self.data[foot]['lng']
    
            # Ensure there are valid coordinates
            if len(latitudes) == 0 or len(longitudes) == 0:
                dict_step_length[foot] = None
                if self.verbosity > 1:
                    print(f"No valid coordinates found for {foot} foot.")
                continue
    
            # Get the first and last coordinates
            coord1 = (latitudes.iloc[0], longitudes.iloc[0])
            coord2 = (latitudes.iloc[-1], longitudes.iloc[-1])
    
            # Calculate the total distance traveled using the haversine formula
            total_distance = self.data_processor.haversine(coord1, coord2)
    
            # Get the cadence for this foot
            cadence = cadence_dict.get(foot, None)
            if cadence is None or cadence == 0:
                dict_step_length[foot] = None
                if self.verbosity > 1:
                    print(f"Unable to calculate cadence for {foot} foot.")
                continue
    
            # Calculate the total number of steps using cadence
            total_steps = (total_distance * cadence) / 60.0
    
            # Calculate the average step length (in meters)
            avg_step_length = total_distance / total_steps
            dict_step_length[foot] = avg_step_length
    
            if self.verbosity > 1:
                print(f"Average step length for {foot} foot: {avg_step_length:.2f} meters. (If trajectory is not a perfect straight line the average step length is shorter)")
        print()
        # Return the dictionary with step lengths
        return dict_step_length


    def calculate_double_support_time(self):
        """
        Calculate the average time (in seconds) where both feet are on the ground.
        Adjusts for differences in sample lengths by removing evenly spaced samples from the longer series.
    
        Returns:
        - average_double_support_time: Average time where both feet are on the ground in a single step (in seconds).
        """
        if self.verbosity > 1:
            print("Calculating average double support time by adjusting for sample differences...")
    
        # Retrieve heel pressure data for both feet
        left_S2 = self.data['left']['S2'].values
        right_S2 = self.data['right']['S2'].values
        left_time = pd.to_datetime(self.data['left']['_time']).astype('int64') / 1e9  # Convert to seconds
        right_time = pd.to_datetime(self.data['right']['_time']).astype('int64') / 1e9  # Convert to seconds
    
        # Check which series is longer and adjust
        if len(left_time) > len(right_time):
            excess_samples = len(left_time) - len(right_time)
            indices_to_remove = np.round(np.linspace(0, len(left_time) - 1, excess_samples, endpoint=False)).astype(int)
            left_time = np.delete(left_time, indices_to_remove)
            
            left_S2 = np.delete(left_S2, indices_to_remove)
        elif len(right_time) > len(left_time):
            excess_samples = len(right_time) - len(left_time)
            indices_to_remove = np.round(np.linspace(0, len(right_time) - 1, excess_samples, endpoint=False)).astype(int)
            right_time = np.delete(right_time, indices_to_remove)
            right_S2 = np.delete(right_S2, indices_to_remove)


        # Now both time series are of equal length
        if self.verbosity > 1:
            print("Adjusted left and right foot data to have the same number of samples.")
    
        # Convert heel pressure data to binary signals
        left_binary = (left_S2 > np.mean(left_S2)).astype(int)  # High pressure = 1, Low pressure = 0
        right_binary = (right_S2 > np.mean(right_S2)).astype(int)
    
        # Multiply binary signals to find overlap (both feet on the ground)
        overlap_signal = left_binary * right_binary
    
        # Identify continuous intervals where both feet are on the ground
        overlap_times = []
        in_overlap = False
        start_time = None
    
        for i, value in enumerate(overlap_signal):
            if value == 1 and not in_overlap:
                # Start of an overlap interval
                in_overlap = True
                start_time = left_time[i]  # Use left_time or right_time (now both are aligned)
            elif value == 0 and in_overlap:
                # End of an overlap interval
                in_overlap = False
                overlap_times.append(left_time[i] - start_time)
    
        # Add the last interval if it ends with an overlap
        if in_overlap and start_time is not None:
            overlap_times.append(left_time.iloc[-1] - start_time)
    
        # Calculate average double support time
        if len(overlap_times) == 0:
            average_double_support_time = 0
        else:
            average_double_support_time = np.mean(overlap_times)
            total_double_support_time = np.sum(overlap_times)
            percentage_double_support_time = 100*total_double_support_time/(left_time.iloc[-1] - left_time.iloc[0])
        if self.verbosity > 1:
            print(f"Average double support time: {average_double_support_time:.2f} seconds.")
            print(f"Percentage of double support time: {percentage_double_support_time:.2f} % [28%-40% is considered the normal window]")
            print()
        return average_double_support_time, percentage_double_support_time



    def gait_analysis(self):
        
        gait_dict={}
        cadence=self.cadence()
        step_length=self.calculate_step_length()
        double_support_time=self.calculate_double_support_time()
        gait_dict['cadence']=cadence
        gait_dict['step_length']=step_length
        gait_dict['average_double_support'] = double_support_time[0]
        gait_dict['average_double_support'] = double_support_time[1]
        
        return gait_dict
