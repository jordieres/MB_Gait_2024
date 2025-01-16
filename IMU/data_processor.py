# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:05:03 2024

@author: marbo
"""

import pandas as pd
import numpy as np
import pytz
from timezonefinder import TimezoneFinder
from geopy.distance import geodesic

class DataProcessor:
    """
    A class to process movement data by calculating distances, speeds, movement IDs,
    correcting anomalous coordinates, and converting UTC times to local times based on location.

    Attributes
    ----------
    data : pandas.DataFrame
        The input DataFrame containing movement data with columns like '_time', 'lat', and 'lng'.
    verbose : int
        The verbosity level (0, 1, or 2) to control the amount of logging.
    tf : TimezoneFinder
        An instance of TimezoneFinder to find time zones based on latitude and longitude.
    movements_df : pandas.DataFrame
        This DataFrame contains the transformations made over the input data DataFrame

    Methods
    -------
    haversine(coord1, coord2):
        Calculates the great-circle distance between two points on the Earth's surface.
    calculate_speed(coord1, coord2, time1, time2):
        Calculates the speed between two coordinates over a time interval.
    correct_point(data, i, speed_threshold):
        Checks if the point at index i should be corrected based on speed thresholds.
    correct_coordinates_with_speed(data, speed_threshold=30):
        Corrects middle coordinates if the speed between points exceeds a threshold.
    get_coordinates(data, i):
        Retrieves coordinates for points at indices i-1, i, and i+1.
    convert_utc_to_local(row):
        Converts UTC time to local time based on latitude and longitude.
    identify_movements():
        Identifies unique movements where latitude or longitude changes.
    calculate_distances_and_speeds(movements_df):
        Calculates distances, time differences, and speeds for movement data.
    assign_movement_ids(movements_df, time_spacing=120):
        Assigns movement IDs based on distance and time thresholds.
    calculate_avg_speeds(movements_df):
        Calculates average speeds for each movement ID.
    process_data():
        Processes the data through all steps and returns the final DataFrame.
    """

    def __init__(self, data, verbose=0):
        """
        Initializes the DataProcessor with the provided data and verbosity level.

        Parameters
        ----------
        data : pandas.DataFrame
            A DataFrame containing movement data with columns '_time', 'lat', and 'lng'.
        verbose : int, optional
            Verbosity level for logging (default is 0, meaning no output).
        """
        self.data = data
        self.verbose = verbose
        self.tf = TimezoneFinder()
        self.movements_df = pd.DataFrame()
        

    @staticmethod
    def haversine(coord1, coord2):
        """
        Calculates the great-circle distance between two coordinates on Earth using the Haversine formula.

        Parameters
        ----------
        coord1 : tuple of float
            The (latitude, longitude) of the first point.
        coord2 : tuple of float
            The (latitude, longitude) of the second point.

        Returns
        -------
        float
            The distance between the two points in meters.
        """
        return geodesic(coord1, coord2).meters

    def calculate_speed(self, coord1, coord2, time1, time2):
        """
        Calculates the speed between two points based on the distance and time difference.

        Parameters
        ----------
        coord1 : tuple of float
            The (latitude, longitude) of the first point.
        coord2 : tuple of float
            The (latitude, longitude) of the second point.
        time1 : pandas.Timestamp
            The timestamp of the first point.
        time2 : pandas.Timestamp
            The timestamp of the second point.

        Returns
        -------
        float
            The speed between the two points in kilometers per hour.
            Returns infinity if the time difference is zero to avoid division by zero.
        """
        distance_km = self.haversine(coord1, coord2) / 1000  # Convert meters to kilometers
        time_diff_hours = (time2 - time1).total_seconds() / 3600  # Convert seconds to hours

        if time_diff_hours == 0:
            return np.inf  # Avoid division by zero

        return distance_km / time_diff_hours

    def correct_point(self, data, i, speed_threshold):
        """
        Determines if the point at index i is an outlier based on speed thresholds
        and corrects it by averaging surrounding points if necessary.

        Parameters
        ----------
        data : pandas.DataFrame
            The DataFrame containing movement data.
        i : int
            The index of the current point to evaluate.
        speed_threshold : float
            The speed threshold in km/h to determine anomalies.

        Returns
        -------
        bool
            True if a correction was made, False otherwise.
        """
        coord1, coord2, coord3 = self.get_coordinates(data, i)
        
        time1, time2, time3 = data.loc[i - 1, '_time'], data.loc[i, '_time'], data.loc[i + 1, '_time']

        speed1 = self.calculate_speed(coord1, coord2, time1, time2)
        speed2 = self.calculate_speed(coord2, coord3, time2, time3)
        speed3 = self.calculate_speed(coord1, coord3, time1, time3)

        if (speed1 > speed_threshold or speed2 > speed_threshold) and speed3 < speed_threshold:
            # Correct the middle point by averaging the coordinates of the surrounding points
            avg_lat = (coord1[0] + coord3[0]) / 2
            avg_lng = (coord1[1] + coord3[1]) / 2
            data.at[i, 'lat'] = avg_lat
            data.at[i, 'lng'] = avg_lng
            return True  # Correction was made

        return False  # No correction needed

    def correct_coordinates_with_speed(self, speed_threshold):
        """
        Iterates over the DataFrame to correct any anomalous coordinates based on excessive speeds.

        Parameters
        ----------
        data : pandas.DataFrame
            The DataFrame containing movement data.
        speed_threshold : float, optional
            The speed threshold in km/h to determine anomalies (default is 30 km/h).

        Returns
        -------
        pandas.DataFrame
            The DataFrame with corrected coordinates.
        """
        corrections = sum(
            self.correct_point(self.data, i, speed_threshold) for i in range(1, len(self.data) - 1)
        )

        if self.verbose > 1:
            print(f"Corrected {corrections} rows due to speed anomalies.")

        return self.data

    def get_coordinates(self, data, i):
        """
        Retrieves the coordinates for three consecutive points: previous (i-1), current (i), and next (i+1).

        Parameters
        ----------
        data : pandas.DataFrame
            The DataFrame containing movement data.
        i : int
            The index of the current point.

        Returns
        -------
        tuple
            A tuple containing three tuples of coordinates: (coord1, coord2, coord3).
        """
        coord1 = (data.loc[i - 1, 'lat'], data.loc[i - 1, 'lng'])
        coord2 = (data.loc[i, 'lat'], data.loc[i, 'lng'])
        coord3 = (data.loc[i + 1, 'lat'], data.loc[i + 1, 'lng'])
        return coord1, coord2, coord3

    def convert_utc_to_local(self, row):
        """
        Converts a UTC timestamp to local time based on the latitude and longitude in the row.

        Parameters
        ----------
        row : pandas.Series
            A row from the DataFrame containing 'lat', 'lng', and 'time'.

        Returns
        -------
        tuple
            A tuple containing the localized time (pandas.Timestamp) and the timezone string.
            If the timezone cannot be determined, returns (None, 'Unknown').
        """
        lat, lng, utc_time = row['lat'], row['lng'], row['time']
        
        timezone_str = self.tf.timezone_at(lat=lat, lng=lng)
        
        if timezone_str:
            local_tz = pytz.timezone(timezone_str)
            local_time = utc_time.tz_convert(local_tz)
            return local_time, timezone_str
        
        # Return NaT for local_time if timezone can't be found
        return pd.NaT, 'Unknown'

    def identify_movements(self):
        """
        Identifies unique movements by filtering out consecutive duplicate coordinates.
      
        """
        movements = [{
            'time': self.data['_time'].iloc[0],
            'lat': self.data['lat'].iloc[0],
            'lng': self.data['lng'].iloc[0]
        }]
        movements.extend(
            {
                'time': self.data['_time'].iloc[i + 1],
                'lat': self.data['lat'].iloc[i + 1],
                'lng': self.data['lng'].iloc[i + 1]
            }
            for i in range(len(self.data) - 1)
            if self.data['lat'].iloc[i] != self.data['lat'].iloc[i + 1] or
               self.data['lng'].iloc[i] != self.data['lng'].iloc[i + 1]
        )
        
        self.movements_df = pd.DataFrame(movements).sort_values(by='time').reset_index(drop=True)
        
        if self.verbose > 1:
            print(f"Identified and sorted {len(self.movements_df)} unique movements.")


    def calculate_distances_and_speeds(self):
        """
        Calculates distances between consecutive points, time differences, and speeds.

        """
        # Calculate distances between consecutive points
        distances = [0] + [
            self.haversine(
                (self.movements_df['lat'].iloc[i - 1], self.movements_df['lng'].iloc[i - 1]),
                (self.movements_df['lat'].iloc[i], self.movements_df['lng'].iloc[i])
            )
            for i in range(1, len(self.movements_df))
        ]
        self.movements_df['distance_m'] = distances
        self.movements_df['time_diff'] = self.movements_df['time'].diff().dt.total_seconds()
        self.movements_df['speed_m_s'] = self.movements_df['distance_m'] / self.movements_df['time_diff']
        
        self.movements_df.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.movements_df.fillna(0, inplace=True)
        
        if self.verbose > 1:
            print("Calculated distances, time differences, and speeds.")

    def assign_movement_ids(self, time_spacing=120):
        """
        Assigns movement IDs based on distance and time thresholds to segment movements.

        Parameters
        ----------
        
        time_spacing : int, optional
            The threshold in seconds for time or distance to start a new movement (default is 120 seconds).

        
        """
        movement_id = 0
        movement_list = []

        for i in range(len(self.movements_df)):
            if self.movements_df['distance_m'].iloc[i] > time_spacing or \
               self.movements_df['time_diff'].iloc[i] > time_spacing:
                movement_id += 1
            movement_list.append(movement_id)

        self.movements_df['movement_id'] = movement_list

        if self.verbose > 0:
            print(f"Assigned movement IDs based on time and distance (threshold: {time_spacing} seconds).")

    def calculate_avg_speeds(self):
        """
        Calculates the average speed for each movement ID.

        
        """
        # Group by movement_id and calculate average speed, skipping the first speed (which is 0 or invalid)
        avg_speeds = self.movements_df.groupby('movement_id')['speed_m_s'].apply(
            lambda x: x.iloc[1:].mean() if len(x) > 1 else 0
        )
        self.movements_df['avg_speed_m_s'] = self.movements_df['movement_id'].map(avg_speeds)
        
        if self.verbose > 0:
            print("Calculated average speeds for each movement.")

    def process_data(self, time_spacing=120, speed_threshold=30):
        """
        Processes the movement data through all steps: cleaning, calculating distances and speeds,
        correcting anomalies, assigning movement IDs, and converting times.

        Parameters
        ----------
        time_spacing : int, optional
            The threshold in seconds for time or distance to start a new movement (default is 120 seconds).
        speed_threshold : float, optional
            The speed threshold in km/h to identify and correct speed anomalies (default is 30 km/h).

        Returns
        -------
        pandas.DataFrame
            The processed DataFrame with additional columns:
            'distance_m', 'time_diff', 'speed_m_s', 'movement_id', 'avg_speed_m_s',
            'local_time', 'local_timezone'.
        """
        if self.verbose > 0:
            print("\nStarting data processing...")

        self.data[['lat', 'lng']] = self.data[['lat', 'lng']].astype(float)
        
        if self.verbose > 1:
            print("Converted 'lat' and 'lng' columns to float.")

        self.identify_movements()  # Step 2 & 3: Identify unique movements and sort them
        self.calculate_distances_and_speeds()  # Step 4: Calculate distances, time differences, and speeds
        self.correct_coordinates_with_speed(speed_threshold=speed_threshold)  # Step 5: Correct coordinates based on speed anomalies
        self.assign_movement_ids(time_spacing)  # Step 6: Assign movement IDs
        self.calculate_avg_speeds()  # Step 7: Calculate average speeds

        # Step 8: Convert UTC times to local times
        self.movements_df[['local_time', 'local_timezone']] = self.movements_df.apply(
            lambda row: self.convert_utc_to_local(row),
            axis=1,
            result_type="expand"
        )

        if self.verbose > 1:
            print("Converted UTC times to local times based on coordinates.")
            print("Final processed DataFrame:")
            print(self.movements_df.head())

        return self.movements_df
