# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 21:36:00 2025

@author: marbo
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from geopy.distance import geodesic
from scipy import signal
import ahrs
from scipy.signal import butter, filtfilt

class TrajectoryAnalyzerAHRS:
    
    def __init__(self, data, sample_period=0.02, verbosity=0):
        
        self.data = data  # DataFrame containing IMU and GPS data
        self.sample_period = sample_period  # Sampling period in seconds
        # Ensure lat and lng are numeric
        self.data['lat'] = pd.to_numeric(self.data['lat'], errors='coerce')
        self.data['lng'] = pd.to_numeric(self.data['lng'], errors='coerce')
        self.gps_lat = data['lat']  # GPS latitude
        self.gps_lng = data['lng']  # GPS longitude
        self.IMU_dict = {}
        self.verbosity = verbosity


    

    def high_pass_filter(self, data, cutoff=0.1, fs=50, order=2):
        """
        Applies a high-pass Butterworth filter to the input data.
    
        Parameters:
        ----------
        data : array-like
            The input signal to be filtered.
        cutoff : float, optional
            The cutoff frequency in Hz (must be > 0). Defaults to 0.1 Hz.
        fs : float, optional
            Sampling frequency in Hz. Defaults to 50 Hz.
        order : int, optional
            Filter order for sharper transitions. Defaults to 2.
    
        Returns:
        -------
        filtered_data : array-like
            The filtered signal, same shape as input.
    
        Raises:
        ------
        ValueError
            If cutoff frequency is <= 0.
        """
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


    def low_pass_filter(self, data, cutoff=3, fs=50, order=2):
        """
        Apply a low-pass filter to the data.
        
        Parameters:
        - data: array-like, the input data to filter
        - cutoff: float, the cutoff frequency for the low-pass filter (default: 3 Hz)
        - fs: float, the sampling frequency of the data (default: 50 Hz)
        - order: int, the order of the filter (default: 2)
        
        Returns:
        - The filtered data as a numpy array.
        """
        # If cutoff is a pandas Series or numpy array, get the first value (assuming scalar-like)
        if isinstance(cutoff, (np.ndarray, pd.Series)):
            cutoff = cutoff.iloc[0] if isinstance(cutoff, pd.Series) else cutoff[0]
        
        # Ensure cutoff is a positive value
        if cutoff <= 0:
            raise ValueError("Cutoff frequency must be greater than 0")
        
        # Calculate the Nyquist frequency
        nyquist = 0.5 * fs
        
        # Normalize the cutoff frequency by the Nyquist frequency
        normalized_cutoff = cutoff / nyquist
        
        # Design the low-pass filter
        b, a = butter(order, normalized_cutoff, btype='low', analog=False)
        
        # Apply the filter using filtfilt (zero-phase filtering)
        return filtfilt(b, a, data, axis=0)


    def calculate_imu_trajectory(self):
        """
        Calculates the IMU-derived translational positions, velocities, and orientations 
        in the global frame. This method applies filtering, computes stationary periods, 
        and integrates sensor data to estimate the trajectory.
    
        Filtering:
        ----------
        - High-pass and low-pass Butterworth filters are applied to accelerometer and gyroscope data.
        - Adjustable cutoff frequencies for both filters:
          - `cutoff_high`: High-pass filter cutoff frequency (default: 0.4 Hz).
          - `cutoff_low`: Low-pass filter cutoff frequency (default: 10 Hz).
    
        Computation:
        ------------
        - Acceleration magnitudes are calculated and filtered.
        - Stationary periods are identified using a magnitude threshold (`stationary_cutoff`).
        - Mahony filter estimates orientation quaternions.
        - Accelerations are rotated to the Earth frame, corrected for gravity, and integrated:
          - Velocities are computed and corrected for drift.
          - Positions are derived from velocity integration.
    
        Visualization:
        --------------
        Generates interactive plots for the following:
        - Filtered acceleration magnitudes and stationary periods.
        - Gyroscope and accelerometer data.
        - Velocity and position data over time.
        - 3D trajectory in global space.
        - Magnetometer data (if available).
    
        Returns:
        --------
        Updates the following instance attributes:
        - `IMU_dict`: Dictionary containing computed values:
            - `stationary`: Boolean array for stationary periods.
            - `acc_mag_filt`: Filtered acceleration magnitudes.
            - `vel`: Estimated velocities.
            - `pos`: Estimated positions.
            - `quat`: Orientation quaternions.
        - `imu_pos`: Estimated positions for further use or plotting.
    
        Raises:
        -------
        ValueError:
            If filtering or integration parameters are invalid.
    
        Notes:
        ------
        - Sensor data anomalies (e.g., saturation) can be corrected with additional adjustments in the code.
        - Ensure sampling period (`sample_period`) is set correctly to match the dataset.
        """
        # Extract IMU data
        time = self.data['_time']
        gyrX, gyrY, gyrZ = self.data['Gx'], self.data['Gz'], self.data['Gy']
        accX, accY, accZ = self.data['Ax'], self.data['Az'], self.data['Ay'] - 1
        
        if self.verbosity > 0:
            print("\nGravity effect removed from vertical acceleration axis")
        
        
        
        #Adjust:
        cutoff_high=0.4
        
        accX = self.high_pass_filter(accX, cutoff_high,  fs=50, order=2) 
        accY = self.high_pass_filter(accY, cutoff_high, fs=50, order=2)  
        accZ = self.high_pass_filter(accZ, cutoff_high, fs=50, order=2)  
        gyrX = self.high_pass_filter(gyrX, cutoff_high, fs=50, order=2)  
        gyrY = self.high_pass_filter(gyrY, cutoff_high, fs=50, order=2)  
        gyrZ = self.high_pass_filter(gyrZ, cutoff_high, fs=50, order=2)  
        
        if self.verbosity > 0:
            print(f"\nHigh_pass filter applied to IMU data. Cutoff frequency: {cutoff_high} Hz.")
            
        
        #Adjust:
        cutoff_low=10
        
        
        # Apply the low-pass filter with a cutoff of 3Hz for the acceleration and gyroscope data
        accX = self.low_pass_filter(accX, cutoff_low, fs=50, order=2)  
        accY = self.low_pass_filter(accY, cutoff_low, fs=50, order=2)  
        accZ = self.low_pass_filter(accZ, cutoff_low, fs=50, order=2)  
        gyrX = self.low_pass_filter(gyrX, cutoff_low, fs=50, order=2)  
        gyrY = self.low_pass_filter(gyrY, cutoff_low, fs=50, order=2)  
        gyrZ = self.low_pass_filter(gyrZ, cutoff_low, fs=50, order=2)  
        
        if self.verbosity > 0:
            print(f"Low_pass filter applied to IMU data. Cutoff frequency: {cutoff_low} Hz.")
            
        #The lines of code here are to be used to correct sensor saturation and other firmware malfunctions:
            
        #accX[accX < -1] *= 2
        #accZ[accZ < 0] *= 0
        #accZ[accZ > 1] *= 2.5
        #gyrY[gyrY > 150] *= 2.5
        #accX = accX*2.25
        #accZ[accZ > 0.1] *= 8
        #gyrY = (gyrY*2)+400
        
        
        if self.verbosity > 0:
            print("\nStarting to compute acceleration magnitudes...")
        
        # Compute stationary periods
        acc_mag = np.sqrt(accX**2 + accY**2 + accZ**2)
        filtCutOff = 0.4
        b, a = signal.butter(1, (2 * filtCutOff) / (1 / self.sample_period), 'highpass')
        acc_mag_filt = signal.filtfilt(b, a, acc_mag, padtype='odd', padlen=3*(max(len(b), len(a))-1))
        acc_mag_filt = np.abs(acc_mag_filt)
        b, a = signal.butter(1, (2 * 1.5) / (1 / self.sample_period), 'lowpass')
        acc_mag_filt = signal.filtfilt(b, a, acc_mag_filt, padtype='odd', padlen=3*(max(len(b), len(a))-1))
        
        
        
        
        sample_period = 0.02  # Adjust this value to match your data
        time_plot = np.arange(len(acc_mag_filt)) * sample_period
        
        if self.verbosity > 0:
        
            # Create the figure
            fig = go.Figure()
            
            # Add the filtered acceleration magnitude trace
            fig.add_trace(go.Scatter(
                x=time_plot,
                y=acc_mag_filt,
                mode='lines',
                name='Filtered Acceleration Magnitude',
                line=dict(color='blue', width=2)
            ))
            
            # Update layout
            fig.update_layout(
                title="Filtered Acceleration Magnitude Over Time",
                xaxis_title="Time (s)",
                yaxis_title="Acceleration Magnitude (g)",
                legend_title="Legend",
                template="plotly_white",
                showlegend=True
            )
            
            # Show the plot
            fig.show()               
        
        
            
        #Adjust:
        stationary_cutoff = 0.3
        stationary = acc_mag_filt < stationary_cutoff
        
        if self.verbosity > 0:
            print(f"\nAcceleration magnitudes below {stationary_cutoff} are considered stationary periods. Adjust stationary_cutoff variable if needed.")
            
            
            # Create the figure
            fig = go.Figure()
            
            # Add the filtered acceleration magnitude trace
            fig.add_trace(go.Scatter(
                x=time_plot,
                y=stationary,
                mode='lines',
                name='Stationary Periods',
                line=dict(color='blue', width=2)
            ))
            
            # Update layout
            fig.update_layout(
                title="Stationary Periods Over Time",
                xaxis_title="Time (s)",
                yaxis_title="Acceleration Magnitude (g)",
                legend_title="Legend",
                template="plotly_white",
                showlegend=True
            )
            
            # Show the plot
            fig.show()            
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
            fig.add_trace(go.Scatter(x=time, y=acc_mag_filt, mode='lines', name='Filtered Acc', line=dict(color='black', dash='dot', width=2)))
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
       
        # Estimate orientation using Mahony filter
        # Compute orientation
        
        if self.verbosity > 0:
            print('\nStarting to compute orientation...')
            
        quat  = np.zeros((time.size, 4), dtype=np.float64)
    
        # initial convergence
        initPeriod = 0
        indexSel = time <= time[0] + pd.to_timedelta(initPeriod, unit='s')
        gyr=np.zeros(3, dtype=np.float64)
        acc = np.array([np.mean(accX[indexSel]), np.mean(accY[indexSel]), np.mean(accZ[indexSel])])
        
        mahony = ahrs.filters.Mahony(Kp=1, Ki=0,KpInit=1, frequency=1/self.sample_period)
        
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

        # Rotate body accelerations to the Earth frame
        acc_earth = []
        for x, y, z, q in zip(accX, accY, accZ, quat):
            acc_earth.append(ahrs.common.orientation.q_rot(ahrs.common.orientation.q_conj(q), np.array([x, y, z])))
        acc_earth = np.array(acc_earth) - [0, 0, 1]
        acc_earth *= 9.81

        # Compute translational velocities
        acc[2] = acc[2] - 9.81
    
        
        # Integrate acceleration to compute velocity and position
        vel = np.zeros_like(acc_earth)
        for t in range(1, len(vel)):
            vel[t, :] = vel[t-1, :] + acc_earth[t, :] * self.sample_period
            if stationary[t]:
                vel[t, :] = 0

        if self.verbosity > 0:
            print('Velocity integration complete.')
            
            
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
        
        if self.verbosity > 0:
            
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
        
        
        pos = np.zeros_like(vel)
        for t in range(1, len(pos)):
            pos[t, :] = pos[t-1, :] + vel[t, :] * self.sample_period

        if self.verbosity > 0:
            
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
        
        # Plot 3D foot trajectory
    
        posPlot = pos
        quatPlot = quat
    
        extraTime = 20
        onesVector = np.ones(int(extraTime*(1/self.sample_period)))
        
        if self.verbosity > 0:
            
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
        
        if self.verbosity > 0:
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
        
        
        
        self.IMU_dict['stationary'] = stationary
        self.IMU_dict['acc_mag_filt'] = acc_mag_filt
        self.IMU_dict['vel'] = vel
        self.IMU_dict['pos'] = pos
        self.IMU_dict['quat'] = quat
        
        
        
        self.imu_pos = pos  # Save the IMU positions for plotting
        

    def plot_trajectory_with_map(self, output_html_file="trajectory_map.html"):
        """
        Plot the GPS trajectory and overlay the IMU trajectory on an interactive map.
        
        This function visualizes the GPS trajectory alongside the IMU trajectory by:
        - Extracting GPS latitude and longitude data.
        - Calculating the initial bearing to align the IMU trajectory with the GPS trajectory.
        - Scaling and transforming the IMU trajectory to match the GPS scale and coordinates.
        - Plotting both trajectories on an OpenStreetMap using Plotly's Scattermapbox.
        - Saving the resulting interactive map as an HTML file.
        
        Args:
            output_html_file (str): The name of the output HTML file to save the map. Defaults to "trajectory_map.html".
        
        Returns:
            dict: A dictionary containing details about the IMU and GPS trajectories, including the GPS distance.
        """
        # Extract GPS latitude and longitude
        gps_lat = self.gps_lat.to_numpy()
        gps_lng = self.gps_lng.to_numpy()
    
        # Calculate the initial bearing using the first and last GPS coordinates
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
    
        # Get the first and last GPS coordinates
        lat1, lon1 = gps_lat[0], gps_lng[0]  # First coordinates
        lat2, lon2 = gps_lat[-1], gps_lng[-1]  # Last coordinates
    
        # Calculate the initial bearing between the first and last GPS points
        initial_bearing = calculate_initial_bearing(lat1, lon1, lat2, lon2)
        
        # Transform IMU trajectory into the global frame
        imu_x = self.imu_pos[:, 0]
        imu_y = self.imu_pos[:, 1]
    
        # Rotate IMU trajectory by the calculated initial bearing
        imu_x_rot = imu_x * np.cos(np.radians(initial_bearing)) - imu_y * np.sin(np.radians(initial_bearing))
        imu_y_rot = imu_x * np.sin(np.radians(initial_bearing)) + imu_y * np.cos(np.radians(initial_bearing))
        
        # Scale the IMU trajectory to GPS units
        gps_dist = geodesic((lat1, lon1), (lat2, lon2)).meters
        imu_dist = np.sqrt(np.sum(np.diff(imu_x_rot)**2 + np.diff(imu_y_rot)**2))
        
        self.IMU_dict['gps_dist'] = gps_dist
        self.IMU_dict['gps_dist'] = gps_dist
        
        
        print(f"GPS Distance: {gps_dist} meters")
        print(f"IMU Distance: {imu_dist} meters")
        
        # Calculate the scaling factor
        scale_factor = gps_dist / imu_dist if imu_dist > 0 else 1
        print(f"Scaling Factor: {scale_factor}")
        
        # Apply the scaling factor
        imu_x_rot *= scale_factor
        imu_y_rot *= scale_factor
        
        # Convert IMU trajectory to latitude/longitude
        # Correct conversion from meters to latitude/longitude
        # For latitude, it's roughly 1 degree = 111320 meters.
        # For longitude, 1 degree = 111320 * cos(latitude) meters.
        
        # Convert IMU trajectory to latitude and longitude
        # Latitude conversion (constant value)
        imu_lat = lat1 + imu_y_rot / 111320  # Convert meters to degrees latitude
        
        # Longitude conversion (needs to account for latitude's effect)
        # cos(np.radians(lat1)) is the scaling factor for longitude
        imu_lng = lon1 + imu_x_rot / (111320 * np.cos(np.radians(lat1)))  # Convert meters to degrees longitude
        
        # Printing out intermediate results to help debug
        print(f"\nInitial Latitude: {lat1}, Longitude: {lon1}")
        print(f"IMU Lat: {imu_lat[:5]}, IMU Lng: {imu_lng[:5]}")  # Display first 5 converted values
    
        # Create the map plot
        fig = go.Figure()
    
        # GPS trajectory
        fig.add_trace(go.Scattermapbox(
            lat=gps_lat,
            lon=gps_lng,
            mode='lines+markers',
            marker=dict(size=8, color='blue'),
            line=dict(width=2, color='blue'),
            name="GPS Trajectory"
        ))
    
        # IMU trajectory
        fig.add_trace(go.Scattermapbox(
            lat=imu_lat,
            lon=imu_lng,
            mode='lines+markers',
            marker=dict(size=6, color='red'),
            line=dict(width=2, color='red'),
            name="IMU Trajectory"
        ))
    
        # Mapbox layout
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=gps_lat.mean(), lon=gps_lng.mean()),
                zoom=15
            ),
            title="Trajectory Map",
            showlegend=True
        )
    
        # Save the plot
        fig.write_html(output_html_file)
        print(f"Map saved to {output_html_file}")
        
        return self.IMU_dict