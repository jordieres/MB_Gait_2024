# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 13:57:56 2025

@author: marbo
"""

import ahrs
from ahrs.common.orientation import q_prod, q_conj, acc2q, am2q, q2R, q_rot
import pyquaternion
import pandas as pd
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from geopy.distance import geodesic
from scipy.signal import butter, filtfilt



class AHRSIMU:
    """
    A class to analyze motion trajectories using IMU data provided in a DataFrame.

    Attributes:
        data (DataFrame): A DataFrame containing IMU data with required columns.
        sample_period (float): Sampling period in seconds derived from the '_time' column.
    """

    REQUIRED_COLUMNS = ['_time', 'lat', 'lng', 'Ax', 'Ay', 'Az', 'Gx', 'Gy', 'Gz', 'Mx', 'My', 'Mz']

    def __init__(self, data, sampling_rate=50):
        """
        Initializes the AHRSIMU with the provided DataFrame.

        Args:
            data (DataFrame): A DataFrame containing IMU data with columns '_time', 'lat', 'lng',
                              'Ax', 'Ay', 'Az', 'Gx', 'Gy', 'Gz', 'Mx', 'My', 'Mz'.
            sampling_rate (int): Sampling rate in Hz (default is 50 Hz).

        Raises:
            ValueError: If the DataFrame does not contain the required columns.
        """
        if not all(col in data.columns for col in self.REQUIRED_COLUMNS):
            raise ValueError(f"DataFrame must contain the following columns: {self.REQUIRED_COLUMNS}")

        self.data = data
        self.sampling_rate = sampling_rate
        self.samplePeriod = 1 / self.sampling_rate  # Sampling period in seconds
        self.time = data['_time'].values
        self.accelerometer = data[['Ax', 'Ay', 'Az']].values
        self.gyroscope = data[['Gx', 'Gy', 'Gz']].values
        
        self.stationary = None
        self.quaternion = None
        self.velocity = None
        self.position = None

    def high_pass_filter(self, data, cutoff=0.1, fs=50, order=2):
        # If cutoff is a pandas Series, get its first value (assuming it's scalar-like)
        
        if isinstance(cutoff, (np.ndarray, pd.Series)):
            cutoff = cutoff.iloc[0] if isinstance(cutoff, pd.Series) else cutoff[0]
        
        # Ensure cutoff is a positive value
        if cutoff <= 0:
            raise ValueError("Cutoff frequency must be greater than 0")
        
        # Calculate the Nyquist frequency
        nyquist = 0.5 * fs
        
        # Normalize the cutoff frequency by the Nyquist frequency
        normalized_cutoff = cutoff / nyquist
        
        # Design the high-pass filter
        b, a = butter(order, normalized_cutoff, btype='high', analog=False)
        
        # Apply the filter using filtfilt (zero-phase filtering)
        return filtfilt(b, a, data, axis=0)

    def ahrs_imu_trajectory(self):
        


        #xIMUdata = xIMU.xIMUdataClass(filePath, 'InertialMagneticSampleRate', 1/samplePeriod)
        time = self.data['_time']
        gyrX = self.data['Gx']
        gyrY = self.data['Gz']
        gyrZ = self.data['Gy']

        accX = self.data['Ax']
        accY = self.data['Az']
        accZ = (self.data['Ay'])


 
         #xIMUdata = xIMU.xIMUdataClass(filePath, 'InertialMagneticSampleRate', 1/samplePeriod)
        time = self.data['_time']
        gyrX = self.data['Gx']
        gyrY = self.data['Gz']
        gyrZ = self.data['Gy']
        
        accX = self.data['Ax']
        accY = self.data['Az']
        accZ = ((self.data['Ay']) - 1)
        
        
# =============================================================================
#         accZ[accZ > 0] *= 3
#         accZ[abs(accZ) < 0.5] *= 0
#          
#         accX = self.high_pass_filter(accX, cutoff=0.5, fs=50, order=2)  # Adjust cutoff and fs
#         accX *= 4
#         
#         accY = self.high_pass_filter(accY, cutoff=0.5, fs=50, order=2)  # Adjust cutoff and fs
#         accZ = self.high_pass_filter(accZ, cutoff=0.5, fs=50, order=2)  # Adjust cutoff and fs
#         accZ[accZ < 0] *= 0
#         accZ[accZ > 1] *= 2.5
#         gyrX = self.high_pass_filter(gyrX, cutoff=0.5, fs=50, order=2)  # Adjust cutoff and fs
#         gyrY = self.high_pass_filter(gyrY, cutoff=0.5, fs=50, order=2)  # Adjust cutoff and fs
#         gyrY[gyrY > 150] *= 2
#         gyrZ = self.high_pass_filter(gyrZ, cutoff=0.5, fs=50, order=2)  # Adjust cutoff and fs
# =============================================================================
        
        
        
        startTime = time.iloc[0]
        stopTime = time.iloc[-1]
        
        indexSel = np.all([time>=startTime,time<=stopTime], axis=0)
        time = time[indexSel]
        gyrX = gyrX[indexSel]
        gyrY = gyrY[indexSel]
        gyrZ = gyrZ[indexSel]
        accX = accX[indexSel]
        accY = (accY[indexSel])
        accZ = accZ[indexSel]
        
    
    
        # Compute accelerometer magnitude
        acc_mag = np.sqrt(accX*accX+accY*accY+accZ*accZ)
    
        # HP filter accelerometer data
        filtCutOff = 0.5
        b, a = signal.butter(1, (2*filtCutOff)/(1/self.samplePeriod), 'highpass')
        acc_magFilt = signal.filtfilt(b, a, acc_mag, padtype = 'odd', padlen=3*(max(len(b),len(a))-1))
    
        # Compute absolute value
        acc_magFilt = np.abs(acc_magFilt)
    
        # LP filter accelerometer data
        filtCutOff = 5
        b, a = signal.butter(1, (2*filtCutOff)/(1/self.samplePeriod), 'lowpass')
        acc_magFilt = signal.filtfilt(b, a, acc_magFilt, padtype = 'odd', padlen=3*(max(len(b),len(a))-1))
    
    
        # Threshold detection
        stationary = acc_magFilt < 0.05
    
        # Create the figure
        fig = go.Figure()
        
        # Plot gyroscope data
        fig.add_trace(go.Scatter(x=time, y=gyrX, mode='lines', name='Gyro X', line=dict(color='red', width=1)))
        fig.add_trace(go.Scatter(x=time, y=gyrY, mode='lines', name='Gyro Y', line=dict(color='green', width=1)))
        fig.add_trace(go.Scatter(x=time, y=gyrZ, mode='lines', name='Gyro Z', line=dict(color='blue', width=1)))
        
        # Update layout for gyroscope plot
        fig.update_layout(
            title="Gyroscope",
            xaxis_title="Time (s)",
            yaxis_title="Angular Velocity (degrees/s)",
            legend_title="Axes",
            showlegend=True
        )
        # Show the plot in an interactive window
        fig.show()
        
        fig = go.Figure()
        # Plot accelerometer data
        fig.add_trace(go.Scatter(x=time, y=accX, mode='lines', name='Acc X', line=dict(color='red', width=1)))
        fig.add_trace(go.Scatter(x=time, y=accY, mode='lines', name='Acc Y', line=dict(color='green', width=1)))
        fig.add_trace(go.Scatter(x=time, y=accZ, mode='lines', name='Acc Z', line=dict(color='blue', width=1)))
        
        # Plot the filtered accelerometer magnitude and stationary data
        fig.add_trace(go.Scatter(x=time, y=acc_magFilt, mode='lines', name='Filtered Acc', line=dict(color='black', dash='dot', width=2)))
        fig.add_trace(go.Scatter(x=time, y=stationary, mode='lines', name='Stationary', line=dict(color='black', width=1)))
        
        # Update layout for accelerometer plot
        fig.update_layout(
            title="Accelerometer",
            xaxis_title="Time (s)",
            yaxis_title="Acceleration (g)",
            legend_title="Axes",
            showlegend=True
        )
        
        # Show the plot in an interactive window
        fig.show()
    
        # Compute orientation
        quat  = np.zeros((time.size, 4), dtype=np.float64)
    
        # initial convergence
        initPeriod = 2
        indexSel = time <= time[0] + pd.to_timedelta(initPeriod, unit='s')
        gyr=np.zeros(3, dtype=np.float64)
        acc = np.array([np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])
        mahony = ahrs.filters.Mahony(Kp=1, Ki=0,KpInit=1, frequency=1/self.samplePeriod)
        q = np.array([1.0,0.0,0.0,0.0], dtype=np.float64)
        for i in range(0, 2000):
            q = mahony.updateIMU(q, gyr=gyr, acc=acc)
    
        # For all data
        for t in range(0,time.size):
            if(stationary[t]):
                mahony.Kp = 0.5
            else:
                mahony.Kp = 0
            gyr = np.array([gyrX[t],gyrY[t],gyrZ[t]])*np.pi/180
            acc = np.array([accX[t],accY[t],accZ[t]])
            quat[t,:]=mahony.updateIMU(q,gyr=gyr,acc=acc)
    
        # -------------------------------------------------------------------------
        # Compute translational accelerations
    
        # Rotate body accelerations to Earth frame
        acc = []
        for x,y,z,q in zip(accX,accY,accZ,quat):
            acc.append(q_rot(q_conj(q), np.array([x, y, z])))
        acc = np.array(acc)
        acc = acc - np.array([0,0,1])
        acc = acc * 9.81
    
        # Compute translational velocities
        # acc[:,2] = acc[:,2] - 9.81
    
        # acc_offset = np.zeros(3)
        vel = np.zeros(acc.shape)
        for t in range(1,vel.shape[0]):
            vel[t,:] = vel[t-1,:] + acc[t,:]*self.samplePeriod
            if stationary[t] == True:
                vel[t,:] = np.zeros(3)
    
        # Compute integral drift during non-stationary periods
        velDrift = np.zeros(vel.shape)
        stationaryStart = np.where(np.diff(stationary.astype(int)) == -1)[0]+1
        stationaryEnd = np.where(np.diff(stationary.astype(int)) == 1)[0]+1
        for i in range(0,stationaryEnd.shape[0]):
            driftRate = vel[stationaryEnd[i]-1,:] / (stationaryEnd[i] - stationaryStart[i])
            enum = np.arange(0,stationaryEnd[i]-stationaryStart[i])
            drift = np.array([enum*driftRate[0], enum*driftRate[1], enum*driftRate[2]]).T
            velDrift[stationaryStart[i]:stationaryEnd[i],:] = drift
    
        # Remove integral drift
        vel = vel - velDrift
        # Create the figure
        fig = go.Figure()
        
        # Plot velocity data
        fig.add_trace(go.Scatter(x=time, y=vel[:, 0], mode='lines', name='Vel X', line=dict(color='red', width=1)))
        fig.add_trace(go.Scatter(x=time, y=vel[:, 1], mode='lines', name='Vel Y', line=dict(color='green', width=1)))
        fig.add_trace(go.Scatter(x=time, y=vel[:, 2], mode='lines', name='Vel Z', line=dict(color='blue', width=1)))
        
        # Update layout for velocity plot
        fig.update_layout(
            title="Velocity",
            xaxis_title="Time (s)",
            yaxis_title="Velocity (m/s)",
            legend_title="Axes",
            showlegend=True
        )
        
        # Show the plot in an interactive window
        fig.show()
    
        # -------------------------------------------------------------------------
        # Compute translational position
        pos = np.zeros(vel.shape)
        for t in range(1,pos.shape[0]):
            pos[t,:] = pos[t-1,:] + vel[t,:]*self.samplePeriod
    
        # Create the figure
        fig = go.Figure()
        
        # Plot position data
        fig.add_trace(go.Scatter(x=time, y=pos[:, 0], mode='lines', name='Pos X', line=dict(color='red', width=1)))
        fig.add_trace(go.Scatter(x=time, y=pos[:, 1], mode='lines', name='Pos Y', line=dict(color='green', width=1)))
        fig.add_trace(go.Scatter(x=time, y=pos[:, 2], mode='lines', name='Pos Z', line=dict(color='blue', width=1)))
        
        # Update layout for position plot
        fig.update_layout(
            title="Position",
            xaxis_title="Time (s)",
            yaxis_title="Position (m)",
            legend_title="Axes",
            showlegend=True
        )
        
        # Show the plot in an interactive window
        fig.show()
    
        # -------------------------------------------------------------------------
        # Plot 3D foot trajectory
    
        posPlot = pos
        quatPlot = quat
    
        extraTime = 20
        onesVector = np.ones(int(extraTime*(1/self.samplePeriod)))
    
        # Create the figure for 3D trajectory
        fig = go.Figure()
        
        # Add trajectory plot
        fig.add_trace(go.Scatter3d(x=posPlot[:, 0], y=posPlot[:, 1], z=posPlot[:, 2], mode='lines', line=dict(color='blue', width=2)))
        
        # Set limits for axes based on min/max of position
        min_, max_ = np.min(np.min(posPlot, axis=0)), np.max(np.max(posPlot, axis=0))
        fig.update_layout(
            title="Trajectory",
            scene=dict(
                xaxis_title="X Position (m)",
                yaxis_title="Y Position (m)",
                zaxis_title="Z Position (m)",
                xaxis=dict(range=[min_, max_]),
                yaxis=dict(range=[min_, max_]),
                zaxis=dict(range=[min_, max_])
            ),
            showlegend=False
        )
        
        # Show the plot in an interactive window
        fig.show()

       # Extract magnetometer data
        Mx = self.data['Mx']
        My = self.data['My']
        Mz = self.data['Mz']
        time = self.data['_time']  # Assuming time is available in the data
        
        # Create the figure
        fig = go.Figure()
        
        # Plot magnetometer data
        fig.add_trace(go.Scatter(x=time, y=Mx, mode='lines', name='Mx', line=dict(color='red', width=1)))
        fig.add_trace(go.Scatter(x=time, y=My, mode='lines', name='My', line=dict(color='green', width=1)))
        fig.add_trace(go.Scatter(x=time, y=Mz, mode='lines', name='Mz', line=dict(color='blue', width=1)))
        
        # Update layout for the magnetometer plot
        fig.update_layout(
            title="Magnetometer Data",
            xaxis_title="Time (s)",
            yaxis_title="Magnetic Field (Gauss)",
            legend_title="Axes",
            showlegend=True
        )
        
        # Show the plot
        fig.show()
        
        
    def plot_2d_trajectory_with_imu(self, imu_data, output_html_file="trajectory_with_imu_map.html"):
        """
        Plots the 2D IMU trajectory alongside the GPS trajectory on a real-world map.
        
        Args:
            imu_data (pd.DataFrame): DataFrame with columns ['x', 'y'] representing the IMU's X-Y trajectory.
            output_html_file (str): Path to the output HTML file for the visualization.
        """
        # Ensure lat/lng are numeric
        self.data['lat'] = pd.to_numeric(self.data['lat'], errors='coerce')
        self.data['lng'] = pd.to_numeric(self.data['lng'], errors='coerce')
        self.data.dropna(subset=['lat', 'lng'], inplace=True)
    
        # Extract lat/lng
        lat = self.data['lat'].values
        lng = self.data['lng'].values
        
        def calculate_initial_bearing(lat1, lon1, lat2, lon2):
            """
            Calculate the initial bearing (in degrees) between two geographic coordinates.
            
            Args:
                lat1, lon1: Latitude and longitude of the first point in degrees.
                lat2, lon2: Latitude and longitude of the second point in degrees.
            
            Returns:
                Initial bearing in degrees (0° to 360°).
            """
            # Convert degrees to radians
            lat1 = np.radians(lat1)
            lon1 = np.radians(lon1)
            lat2 = np.radians(lat2)
            lon2 = np.radians(lon2)
            
            # Calculate difference in longitudes
            delta_lon = lon2 - lon1
            
            # Calculate initial bearing
            x = np.sin(delta_lon) * np.cos(lat2)
            y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(delta_lon)
            
            # Calculate the initial bearing in radians and convert to degrees
            initial_bearing = np.degrees(np.arctan2(x, y))
            
            # Normalize the bearing to the range [0, 360)
            initial_bearing = (initial_bearing + 360) % 360
    
            return initial_bearing
        
        lat1 = self.data['left']['lat'].iloc[0]  # First latitude
        lon1 = self.data['left']['lng'].iloc[0]  # First longitude
        lat2 = self.data['left']['lat'].iloc[-1]  # Last latitude
        lon2 = self.data['left']['lng'].iloc[-1]  # Last longitude
        
        # Calculate the initial bearing using the first and last coordinates
        initial_bearing = calculate_initial_bearing(lat1, lon1, lat2, lon2)
        
        print(f"Initial bearing: {initial_bearing}°")
    
        # Convert IMU trajectory to global frame using the bearing
        def rotate_trajectory(x, y, angle):
            """Rotate trajectory by a given angle (in degrees)."""
            angle_rad = np.radians(angle)
            x_rot = x * np.cos(angle_rad) - y * np.sin(angle_rad)
            y_rot = x * np.sin(angle_rad) + y * np.cos(angle_rad)
            return x_rot, y_rot
    
        # Rotate IMU trajectory
        imu_x, imu_y = rotate_trajectory(imu_data['x'].values, imu_data['y'].values, initial_bearing)
    
        # Scale IMU trajectory to match the GPS trajectory distances
        gps_distance = geodesic((lat[0], lng[0]), (lat[-1], lng[-1])).meters
        imu_distance = np.sqrt(np.sum(np.diff(imu_x)**2 + np.diff(imu_y)**2))
        print(imu_distance)
        scale_factor = gps_distance / imu_distance if imu_distance > 0 else 1
        imu_x *= scale_factor
        imu_y *= scale_factor
    
        # Offset IMU trajectory to start at the first GPS point
        imu_lat = lat[0] + imu_y / 111320  # Convert meters to degrees latitude
        imu_lng = lng[0] + imu_x / (111320 * np.cos(np.radians(lat[0])))  # Convert meters to degrees longitude
    
        # Plot GPS and IMU trajectories
        fig = go.Figure()
    
        # Add GPS trajectory
        fig.add_trace(go.Scattermapbox(
            lat=lat,
            lon=lng,
            mode='lines+markers',
            marker=dict(size=8, color='blue'),
            line=dict(width=2, color='blue'),
            name="GPS Trajectory"
        ))
    
        # Add IMU trajectory
        fig.add_trace(go.Scattermapbox(
            lat=imu_lat,
            lon=imu_lng,
            mode='lines+markers',
            marker=dict(size=8, color='red'),
            line=dict(width=2, color='red', dash='dash'),
            name="IMU Trajectory"
        ))
    
        # Configure map layout
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=lat.mean(), lon=lng.mean()),
                zoom=15
            ),
            title="2D Trajectory with IMU on Real-World Map",
            margin=dict(l=0, r=0, t=30, b=0)
        )
    
        # Save map to HTML
        fig.write_html(output_html_file)
        print(f"Map with IMU trajectory saved to {output_html_file}")


