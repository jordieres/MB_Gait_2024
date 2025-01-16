# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 17:03:53 2024

@author: marbo
"""

import numpy as np
import matplotlib.pyplot as plt
from MyIMUSensor import MyIMUSensor
import plotly.graph_objects as go
from scipy.spatial.transform import Rotation as R
from scipy.signal import butter, filtfilt



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


    
    def apply_low_pass_filter(self, data, cutoff=5, fs=50, order=4):
        """
        Applies a low-pass Butterworth filter to the input data.
    
        Parameters:
        ----------
        data : np.ndarray
            The input data, where each column represents a signal (e.g., Ax, Ay, Az).
        cutoff : float
            The cutoff frequency of the low-pass filter.
        fs : float
            The sampling rate of the data (in Hz).
        order : int
            The order of the Butterworth filter.
    
        Returns:
        -------
        np.ndarray
            The filtered data, with the same shape as the input.
        """
        b, a = butter(order, cutoff / (0.5 * fs), btype='low', analog=False)
        
        # Apply filter to each column independently
        filtered_data = np.zeros_like(data)
        for i in range(data.shape[1]):
            filtered_data[:, i] = filtfilt(b, a, data[:, i])
        
        return filtered_data
    
    
    def extract_data(self):
        """
        Extracts accelerometer, gyroscope, and magnetometer data for both the right and left foot sensors.

        This method processes the raw IMU data into the required format and creates MyIMUSensor instances
        for both feet using the extracted data.
        """

        #np.array([[1.0, 0.0, 0.0],
        #                 [0.0, 1.0, 0.0],
        #                 [0.0, 0.0, 1.0]])
        #R_init_right = np.transpose(R_init_right)[::-1]
        #theta = np.pi / 4  # 45 degrees in radians
        #rotation_matrix = np.array([[np.cos(theta), -np.sin(theta), 0],
                            #[np.sin(theta),  np.cos(theta), 0],
                            #[0,              0,             1]])

        # Apply the rotation
        #R_init_left = np.dot(rotation_matrix, R_init_left)
        R_init_right = np.array([
                            [0.0, 1.0, 0.0],  # x-axis points along the y-axis
                            [0.0, 0.0, 1.0],  # y-axis points along the z-axis
                            [1.0, 0.0, 0.0]])  # z-axis points along the x-axis
        R_init_left = np.array([
                            [0.0, 1.0, 0.0],  # x-axis points along the y-axis
                            [0.0, 0.0, 1.0],  # y-axis points along the z-axis
                            [1.0, 0.0, 0.0]])  # z-axis points along the x-axis
        
        R_init_right = np.array([[1.0, 0.0, 0.0],
                         [0.0, 1.0, 0.0],
                         [0.0, 0.0, 1.0]])  # z-axis points along the x-axis
        
        R_init_left = np.array([[1.0, 0.0, 0.0],
                         [0.0, 1.0, 0.0],
                         [0.0, 0.0, 1.0]])
        
        if self.verbosity > 0:
            print("Extracting data for right foot sensor and converting acceleration from g to m/s**2 and angles from dps to rds...")
        
        right_data = {
            'acc': np.column_stack((
                np.array(self.interpolated_data['right']['Ax']* 9.80665),
                np.array(self.interpolated_data['right']['Ay']* 9.80665)-9.80665,
                np.array(self.interpolated_data['right']['Az']* 9.80665)
            )),
            'omega': np.column_stack((
                np.array(self.interpolated_data['right']['Gx']* (np.pi / 180)),
                np.array(self.interpolated_data['right']['Gy']* (np.pi / 180)),
                np.array(self.interpolated_data['right']['Gz']* (np.pi / 180))
            )),
            'mag': np.column_stack((
                np.array(self.interpolated_data['right']['Mx']),
                np.array(self.interpolated_data['right']['My']),
                np.array(self.interpolated_data['right']['Mz'])
            ))
        }
        


        self.right_sensor = MyIMUSensor(in_data=right_data)
        self.right_sensor.get_data(R_init=R_init_right, rate=50, in_data=right_data)
        
       
            
        if self.verbosity > 0:
            print("Right foot data extraction complete.")

        if self.verbosity > 0:
            print("Extracting data for left foot sensor...")
        
        left_data = {
            'acc': np.column_stack((
                np.array(self.interpolated_data['left']['Ax']* 9.80665),
                np.array(self.interpolated_data['left']['Ay']* 9.80665)-9.80665,
                np.array(self.interpolated_data['left']['Az']* 9.80665)*(-1)
            )),
            'omega': np.column_stack((
                np.array(self.interpolated_data['left']['Gx']* (np.pi / 180)),
                np.array(self.interpolated_data['left']['Gy']* (np.pi / 180)),
                np.array(self.interpolated_data['left']['Gz']* (np.pi / 180))
            )),
            'mag': np.column_stack((
                np.array(self.interpolated_data['left']['Mx']),
                np.array(self.interpolated_data['left']['My']),
                np.array(self.interpolated_data['left']['Mz']*(-1))
            ))
        }
        

        
        self.left_sensor = MyIMUSensor(in_data=left_data)
        self.left_sensor.get_data(R_init=R_init_left, rate=50, in_data=left_data)
        if self.verbosity > 1:
            print("Left Sensor R_init (before applying 90° rotation):")
            print(self.left_sensor.R_init)
            
        if self.verbosity > 0:
            print("Left foot data extraction complete.")

        #if self.verbosity > 0:
        #    print("Applying 90-degree rotation to the initial orientation of the left foot sensor.")
        #rotation_matrix = R.from_euler('z', -90, degrees=True).as_matrix()  # -90 degrees rotation around Z-axis
        #self.left_sensor.R_init = rotation_matrix @ self.left_sensor.R_init  # Update R_init
        #if self.verbosity > 1:
        #    print("Left Sensor R_init (after applying 90° rotation):")
        #    print(self.left_sensor.R_init)
        #if self.verbosity > 0:
        #    print("Adjusted initial orientation of the left sensor.")
        
        
    
        
        
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
            x, z = position[:, 0], position[:, 2]
            fig.add_trace(go.Scatter(
                x=x, y=z,
                mode='lines',
                name=f"{foot} Foot Position Trajectory",
                line=dict(color=color)
            ))
    
        # Customize layout
        fig.update_layout(
            title="2D Position Trajectory",
            xaxis_title="X (m)",
            yaxis_title="Z (m)",
            template="plotly_white",
            legend_title="Foot",
            xaxis=dict(scaleanchor="y"),  # This ensures the x and y axes have the same scale
            yaxis=dict(constrain="range")  # Keeps the y-axis range in check if needed
        )
    
        # Show plot
        fig.show()
