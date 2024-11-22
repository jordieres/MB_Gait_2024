# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 20:31:23 2024

@author: marbo
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class TrajectoryAnalyzer:
    def __init__(self, data, dt=0.01, verbosity=0):
        """
        Initialize the trajectory analyzer.
        :param data: Dictionary containing accelerometer, gyroscope, and magnetometer data.
        :param dt: Sampling interval (in seconds).
        :param verbosity: Verbosity level (0: silent, 1: basic, 2: detailed).
        """
        self.data = data
        self.dt = dt
        self.verbosity = verbosity

        if self.verbosity >= 1:
            print(f"TrajectoryAnalyzer initialized with verbosity level {self.verbosity}.")

    def low_pass_filter(self, data, alpha=0.1):
        """
        Apply a simple low-pass filter to reduce noise.
        :param data: Input signal.
        :param alpha: Smoothing factor (0 < alpha < 1).
        :return: Filtered signal.
        """
        if self.verbosity >= 2:
            print(f"Applying low-pass filter with alpha={alpha}.")

        filtered = np.zeros_like(data)
        filtered[0] = data[0]
        for i in range(1, len(data)):
            filtered[i] = alpha * data[i] + (1 - alpha) * filtered[i - 1]

        if self.verbosity >= 2:
            print(f"Low-pass filter applied to data with {len(data)} samples.")

        return filtered

    def compute_yaw(self, gyro_yaw, mag_x, mag_y, alpha=0.98):
        """
        Fuse gyroscope and magnetometer data to compute yaw.
        :param gyro_yaw: Yaw angle from gyroscope.
        :param mag_x: Magnetometer X-axis data.
        :param mag_y: Magnetometer Y-axis data.
        :param alpha: Weighting factor for complementary filter.
        :return: Corrected yaw angle.
        """
        if self.verbosity >= 2:
            print("Computing yaw using gyroscope and magnetometer data.")

        yaw_mag = np.arctan2(mag_y, mag_x)
        yaw_fused = alpha * np.cumsum(gyro_yaw) * self.dt + (1 - alpha) * yaw_mag

        if self.verbosity >= 2:
            print("Yaw computation complete.")

        return yaw_fused

    def transform_to_global_frame(self, acc_x, acc_y, acc_z, orientation):
        """
        Transform acceleration data from local sensor frame to global frame using orientation.
        :param acc_x: Acceleration in X-axis (local frame).
        :param acc_y: Acceleration in Y-axis (local frame).
        :param acc_z: Acceleration in Z-axis (local frame).
        :param orientation: Orientation dictionary with roll, pitch, yaw.
        :return: Acceleration in global frame (x, y, z).
        """
        roll = orientation['roll']
        pitch = orientation['pitch']
        yaw = orientation['yaw']

        if self.verbosity >= 2:
            print(f"Transforming acceleration to global frame using orientation (roll={roll[-1]}, pitch={pitch[-1]}, yaw={yaw[-1]}).")

        acc_global_x = acc_x * np.cos(yaw) - acc_y * np.sin(yaw)
        acc_global_y = acc_x * np.sin(yaw) + acc_y * np.cos(yaw)
        acc_global_z = acc_z  # Assuming negligible rotation in the Z direction

        return acc_global_x, acc_global_y, acc_global_z

    def integrate(self, data):
        """
        Perform cumulative integration to compute velocity and position.
        :param data: Input acceleration or velocity signal.
        :return: Velocity and position signals.
        """
        if self.verbosity >= 2:
            print(f"Integrating data to compute velocity and position.")

        velocity = np.cumsum(data) * self.dt
        position = np.cumsum(velocity) * self.dt

        if self.verbosity >= 2:
            print(f"Integration complete, velocity and position calculated.")

        return velocity, position

    def compute_trajectories(self):
        """
        Compute trajectories for left and right foot using accelerometer, gyroscope, and magnetometer data.
        :return: Trajectories for left and right foot (dict with position arrays).
        """
        if self.verbosity >= 1:
            print("Computing trajectories for left and right feet.")

        trajectories = {}

        for foot in ['left', 'right']:
            if self.verbosity >= 1:
                print(f"Processing data for {foot} foot.")

            # Load data
            acc_x = self.data[f'acc_data_{foot}']['x']['_value'].to_numpy()
            acc_y = self.data[f'acc_data_{foot}']['y']['_value'].to_numpy()
            acc_z = self.data[f'acc_data_{foot}']['z']['_value'].to_numpy()

            gyro_x = self.data[f'gyro_data_{foot}']['x']['_value'].to_numpy()
            gyro_y = self.data[f'gyro_data_{foot}']['y']['_value'].to_numpy()
            gyro_z = self.data[f'gyro_data_{foot}']['z']['_value'].to_numpy()

            mag_x = self.data[f'magnetometer_data_{foot}']['x']['_value'].to_numpy()
            mag_y = self.data[f'magnetometer_data_{foot}']['y']['_value'].to_numpy()
            mag_z = self.data[f'magnetometer_data_{foot}']['z']['_value'].to_numpy()

            # Demean and filter acceleration data
            acc_x -= np.mean(acc_x)
            acc_y -= np.mean(acc_y)
            acc_z -= np.mean(acc_z)

            acc_x_filtered = self.low_pass_filter(acc_x)
            acc_y_filtered = self.low_pass_filter(acc_y)
            acc_z_filtered = self.low_pass_filter(acc_z)

            # Filter gyroscope data
            gyro_x_filtered = self.low_pass_filter(gyro_x)
            gyro_y_filtered = self.low_pass_filter(gyro_y)
            gyro_z_filtered = self.low_pass_filter(gyro_z)

            # Compute orientation from gyroscope and magnetometer
            orientation = {
                'roll': np.cumsum(gyro_x_filtered) * self.dt,
                'pitch': np.cumsum(gyro_y_filtered) * self.dt,
                'yaw': self.compute_yaw(gyro_z_filtered, mag_x, mag_y)
            }

            # Transform acceleration to global frame
            acc_global_x, acc_global_y, acc_global_z = self.transform_to_global_frame(
                acc_x_filtered, acc_y_filtered, acc_z_filtered, orientation)

            # Integrate acceleration to get velocity and position
            vel_x, pos_x = self.integrate(acc_global_x)
            vel_y, pos_y = self.integrate(acc_global_y)
            vel_z, pos_z = self.integrate(acc_global_z)

            # Invert X and Y directions for the left foot
            if foot == 'left':
                pos_x = -pos_x
                pos_y = -pos_y

            trajectories[foot] = {
                'x': pos_x,
                'y': pos_y,
                'z': pos_z
            }

        if self.verbosity >= 1:
            print("Trajectory computation complete.")

        return trajectories

    def plot_trajectories(self, trajectories):
        """
        Plot the computed trajectories for left and right feet.
        :param trajectories: Trajectories dictionary.
        """
        if self.verbosity >= 1:
            print("Plotting trajectories.")

        plt.figure(figsize=(12, 6))
        for foot in ['left', 'right']:
            plt.plot(trajectories[foot]['x'], trajectories[foot]['y'], label=f'{foot.capitalize()} Foot Trajectory')

        plt.title('Gait Trajectories')
        plt.xlabel('X Position (m)')
        plt.ylabel('Y Position (m)')
        plt.legend()
        plt.grid()

        if self.verbosity >= 1:
            print("Displaying plot.")

        plt.show()