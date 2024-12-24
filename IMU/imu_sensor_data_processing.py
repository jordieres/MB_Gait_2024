# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 17:03:53 2024

@author: marbo
"""

import numpy as np
import matplotlib.pyplot as plt
from MyIMUSensor import MyIMUSensor
import plotly.graph_objects as go

class IMUDataProcessor:
    """
    A class for processing IMU data, including extracting sensor data, calculating position,
    printing sensor data, and plotting trajectories.

    Attributes:
    ----------
    interpolated_data : dict
        A dictionary containing the IMU data, which includes accelerometer, gyroscope, and magnetometer data.
    filter_type : str
        The type of filter to use (default is 'analytical').
    right_sensor : MyIMUSensor
        An instance of the MyIMUSensor class for the right foot sensor data.
    left_sensor : MyIMUSensor
        An instance of the MyIMUSensor class for the left foot sensor data.

    Methods:
    --------
    extract_data():
        Extracts accelerometer, gyroscope, and magnetometer data for both sensors (left and right feet).
    calculate_position():
        Calculates the position of both the right and left sensors.
    print_sensor_data():
        Prints the sensor data for both the right and left foot, including acceleration, angular velocity, magnetic field, orientation (quaternion), position, and velocity.
    plot_trajectory_3d():
        Plots the 3D position trajectory of both the right and left foot sensors.
    plot_trajectory_2d():
        Plots the 2D position trajectory of both the right and left foot sensors.
    """

    def __init__(self, interpolated_data, filter_type='analytical', verbosity=0):
        """
        Initialize the IMUDataProcessor class with interpolated data and filter type.

        Parameters:
        ----------
        interpolated_data : dict
            The IMU data to process.
        filter_type : str, optional
            The type of filter to use for processing the data (default is 'analytical').
        verbosity : int, optional
            Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output) (default is 0).
        """
        self.interpolated_data = interpolated_data
        self.filter_type = filter_type
        self.right_sensor = None
        self.left_sensor = None
        self.verbosity = verbosity

    def extract_data(self):
        """
        Extracts accelerometer, gyroscope, and magnetometer data for both the right and left foot sensors.

        This method processes the raw IMU data into the required format and creates MyIMUSensor instances
        for both feet using the extracted data.
        """
        if self.verbosity > 0:
            print("Extracting data for right foot sensor...")
        
        right_data = {
            'acc': np.column_stack((
                np.array(self.interpolated_data['acc_data_right']['x']['_value']),
                -np.array(self.interpolated_data['acc_data_right']['y']['_value']),
                np.array(self.interpolated_data['acc_data_right']['z']['_value'])
            )),
            'omega': np.column_stack((
                np.array(self.interpolated_data['gyro_data_right']['x']['_value']),
                np.array(self.interpolated_data['gyro_data_right']['y']['_value']),
                np.array(self.interpolated_data['gyro_data_right']['z']['_value'])
            )),
            'mag': np.column_stack((
                np.array(self.interpolated_data['magnetometer_data_right']['x']['_value']),
                np.array(self.interpolated_data['magnetometer_data_right']['y']['_value']),
                np.array(self.interpolated_data['magnetometer_data_right']['z']['_value'])
            ))
        }
        self.right_sensor = MyIMUSensor(in_data=right_data)
        self.right_sensor.get_data(in_data=right_data)

        if self.verbosity > 0:
            print("Right foot data extraction complete.")

        if self.verbosity > 0:
            print("Extracting data for left foot sensor...")
        
        left_data = {
            'acc': np.column_stack((
                np.array(self.interpolated_data['acc_data_left']['x']['_value']),
                np.array(self.interpolated_data['acc_data_left']['y']['_value']),
                np.array(self.interpolated_data['acc_data_left']['z']['_value'])
            )),
            'omega': np.column_stack((
                np.array(self.interpolated_data['gyro_data_left']['x']['_value']),
                np.array(self.interpolated_data['gyro_data_left']['y']['_value']),
                np.array(self.interpolated_data['gyro_data_left']['z']['_value'])
            )),
            'mag': np.column_stack((
                np.array(self.interpolated_data['magnetometer_data_left']['x']['_value']),
                np.array(self.interpolated_data['magnetometer_data_left']['y']['_value']),
                np.array(self.interpolated_data['magnetometer_data_left']['z']['_value'])
            ))
        }
        self.left_sensor = MyIMUSensor(in_data=left_data)
        self.left_sensor.get_data(in_data=left_data)

        if self.verbosity > 0:
            print("Left foot data extraction complete.")

    def calculate_position(self):
        """
        Calculates the position of both the right and left foot sensors.

        This method calls the `calc_position()` method of both the right and left foot sensors.
        """
        if self.verbosity > 0:
            print("Calculating position for right foot...")
        self.right_sensor.calc_position()
        
        if self.verbosity > 0:
            print("Calculating position for left foot...")
        self.left_sensor.calc_position()

    def print_sensor_data(self):
        """
        Prints the sensor data for both the right and left foot, including acceleration,
        angular velocity, magnetic field, orientation (quaternion), position, and velocity.

        The output is printed for both the right and left foot sensors.
        """
        for foot, sensor in zip(['Right', 'Left'], [self.right_sensor, self.left_sensor]):
            print(f"\n{foot} Foot Data:")
            print(f"  Acceleration: {sensor.acc}")
            print(f"  Angular Velocity: {sensor.omega}")
            print(f"  Magnetic Field: {sensor.mag}")
            print(f"  Sampling Rate: {sensor.rate}")
            print(f"  Orientation (Quaternion): {sensor.quat}")
            print(f"  Position: {sensor.pos}")
            print(f"  Velocity: {sensor.vel}")

    def plot_trajectory_3d(self):
        """
        Plots the 3D position trajectory of both the right and left foot sensors using Plotly.
        """
        fig = go.Figure()
    
        # Add traces for each foot
        for foot, sensor, color in zip(['Right', 'Left'], [self.right_sensor, self.left_sensor], ['blue', 'red']):
            position = sensor.pos
            x, y, z = position[:, 0], position[:, 1], position[:, 2]
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                name=f"{foot} Foot Position Trajectory",
                line=dict(color=color)
            ))
    
        # Customize layout
        fig.update_layout(
            title="3D Position Trajectory",
            scene=dict(
                xaxis_title="X (m)",
                yaxis_title="Y (m)",
                zaxis_title="Z (m)"
            ),
            template="plotly_white",
            legend_title="Foot"
        )
    
        # Show plot
        fig.show()

    def plot_trajectory_2d(self):
        """
        Plots the 2D position trajectory of both the right and left foot sensors using Plotly.
        """
        fig = go.Figure()
    
        # Add traces for each foot
        for foot, sensor, color in zip(['Right', 'Left'], [self.right_sensor, self.left_sensor], ['blue', 'red']):
            position = sensor.pos
            x, y = position[:, 0], position[:, 1]
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                name=f"{foot} Foot Position Trajectory",
                line=dict(color=color)
            ))
    
        # Customize layout
        fig.update_layout(
            title="2D Position Trajectory",
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            template="plotly_white",
            legend_title="Foot",
            xaxis=dict(scaleanchor="y"),  # This ensures the x and y axes have the same scale
            yaxis=dict(constrain="range")  # Keeps the y-axis range in check if needed
        )
    
        # Show plot
        fig.show()
