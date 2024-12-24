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
        self.preprocessed_data = None
        # Automatically preprocess the data upon initialization
        self.preprocess_data()
        
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
        sensor_fields = {
            "acc_data": ['Ax', 'Ay', 'Az'],
            "gyro_data": ['Gx', 'Gy', 'Gz'],
            "magnetometer_data": ['Mx', 'My', 'Mz']
        }
        
        # Loop through sensor types (acceleration, gyroscope, magnetometer)
        for sensor_type, fields in sensor_fields.items():
            for foot in ['Right', 'Left']:
                foot_key = f"{sensor_type}_{foot.lower()}"
                data_dict[foot_key] = {}
                for axis, field in zip(['x', 'y', 'z'], fields):
                    filtered_data = self.data[(self.data['_field'] == field) & (self.data['Foot'] == foot)]
                    data_dict[foot_key][axis] = filtered_data.sort_values(by='_time', ascending=True).reset_index(drop=True)
    
        # Process pressure data
        pressure_fields = ['S0', 'S1', 'S2']
        pressure_labels = ['pressure_heel', 'pressure_toe_1', 'pressure_toe_2']
        for label, field in zip(pressure_labels, pressure_fields):
            for foot in ['Right', 'Left']:
                foot_key = f"{label}_{foot.lower()}"
                filtered_data = self.data[(self.data['_field'] == field) & (self.data['Foot'] == foot)]
                data_dict[foot_key] = filtered_data.sort_values(by='_time', ascending=True).reset_index(drop=True)
    
        # Assign the preprocessed data to the class attribute
        self.preprocessed_data = data_dict
         
        
    def get_preprocessed_data(self):
       return self.preprocessed_data
    
    def plot_data(self, data_dict):
        # Plot 1: Heel Pressure (S0) - Left and Right Foot
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=data_dict['pressure_heel_left']['_time'], 
            y=data_dict['pressure_heel_left']['_value'], 
            mode='lines', 
            name='Left Foot Heel Pressure S0', 
            line=dict(color='purple')
        ))
        fig1.add_trace(go.Scatter(
            x=data_dict['pressure_heel_right']['_time'], 
            y=data_dict['pressure_heel_right']['_value'], 
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
    
        # Plot 2: A closer look at Heel Pressure (S0)
        fig2 = go.Figure()
        pressure_heel_left_closer = data_dict['pressure_heel_left']
        pressure_heel_right_closer = data_dict['pressure_heel_right']
        fig2.add_trace(go.Scatter(
            x=pressure_heel_left_closer['_time'], 
            y=pressure_heel_left_closer['_value'], 
            mode='lines', 
            name='Left Foot Heel Pressure S0', 
            line=dict(color='purple')
        ))
        fig2.add_trace(go.Scatter(
            x=pressure_heel_right_closer['_time'], 
            y=pressure_heel_right_closer['_value'], 
            mode='lines', 
            name='Right Foot Heel Pressure S0', 
            line=dict(color='green')
        ))
        fig2.update_layout(
            title='Heel Pressure (S0) - A closer look',
            xaxis_title='Time',
            yaxis_title='Heel Pressure (S0)',
            legend=dict(x=0.8, y=1),
            template='plotly_white'
        )
        fig2.show()
    
        # Plot 3: Heel and Toe Pressure (S0 and S1) for Right Foot
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=data_dict['pressure_heel_right']['_time'], 
            y=data_dict['pressure_heel_right']['_value'], 
            mode='lines', 
            name='Right Foot Heel Pressure S0', 
            line=dict(color='purple')
        ))
        fig3.add_trace(go.Scatter(
            x=data_dict['pressure_toe_1_right']['_time'], 
            y=data_dict['pressure_toe_1_right']['_value'], 
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
            x=data_dict['acc_data_left']['x']['_time'], 
            y=data_dict['acc_data_left']['x']['_value'], 
            mode='lines', 
            name='Acceleration X', 
            line=dict(color='red')
        ))
        fig4.add_trace(go.Scatter(
            x=data_dict['acc_data_left']['y']['_time'], 
            y=data_dict['acc_data_left']['y']['_value'], 
            mode='lines', 
            name='Acceleration Y', 
            line=dict(color='green')
        ))
        fig4.add_trace(go.Scatter(
            x=data_dict['acc_data_left']['z']['_time'], 
            y=data_dict['acc_data_left']['z']['_value'], 
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
            x=data_dict['gyro_data_left']['x']['_time'], 
            y=data_dict['gyro_data_left']['x']['_value'], 
            mode='lines', 
            name='Gyroscope X', 
            line=dict(color='red')
        ))
        fig5.add_trace(go.Scatter(
            x=data_dict['gyro_data_left']['y']['_time'], 
            y=data_dict['gyro_data_left']['y']['_value'], 
            mode='lines', 
            name='Gyroscope Y', 
            line=dict(color='green')
        ))
        fig5.add_trace(go.Scatter(
            x=data_dict['gyro_data_left']['z']['_time'], 
            y=data_dict['gyro_data_left']['z']['_value'], 
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
        mag_x = data_dict['magnetometer_data_left']['x']['_value']
        mag_y = data_dict['magnetometer_data_left']['y']['_value']
        mag_z = data_dict['magnetometer_data_left']['z']['_value']
        time_values = data_dict['magnetometer_data_left']['x']['_time']
    
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
        
        
        
        

