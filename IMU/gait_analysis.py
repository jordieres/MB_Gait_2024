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

    
    def plot_data(self, data_dict):

         # Plot 1: Heel Pressure (S0) - Left and Right Foot
         fig1 = go.Figure()
         fig1.add_trace(go.Scatter(
             x=data_dict['left']['_time'], 
             y=data_dict['left']['S0'], 
             mode='lines', 
             name='Left Foot Heel Pressure S0', 
             line=dict(color='purple')
         ))
         fig1.add_trace(go.Scatter(
             x=data_dict['right']['_time'], 
             y=data_dict['right']['S0'], 
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
        
        
        
        
        

