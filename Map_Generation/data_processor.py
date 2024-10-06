# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:05:03 2024

@author: marbo
"""

import pandas as pd
import numpy as np
from pytz import timezone


class DataProcessor:
    """
   A class used to process movement data, calculate distances, speed, and movement IDs.

   Attributes:
   ----------
   data : pandas.DataFrame
       A DataFrame containing the movement data with columns like latitude, longitude, and time.
    verbose : int
           The verbosity level (0, 1, or 2).
           
   Methods:
   -------
   haversine(lat1, lon1, lat2, lon2):
       Calculates the great-circle distance between two points on the Earth's surface.
   
   process_data():
       Processes the data by calculating distances between points, time differences,
       speed, and grouping points into movements based on distance and time thresholds.
   """
   
   
    def __init__(self, data, verbose=0):
        """
        Initializes the DataProcessor with a DataFrame.

        Parameters:
        ----------
        data : pandas.DataFrame
            A DataFrame containing columns '_time', 'lat', and 'lng' representing timestamps,
            latitude, and longitude, respectively.
        verbose : int, optional
            The verbosity level (default is 0, meaning no output).
        """
        self.data = data
        self.verbose = verbose
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """
       Calculates the Haversine distance between two geographic coordinates.

       Parameters:
       ----------
       lat1 : float
           Latitude of the first point.
       lon1 : float
           Longitude of the first point.
       lat2 : float
           Latitude of the second point.
       lon2 : float
           Longitude of the second point.

       Returns:
       -------
       distance : float
           The distance between the two points in meters.
       """
        R = 6371000  # Earth radius in meters
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c  # Distance in meters
        return distance
    
    
    
    def process_data(self):
        """
       Processes the movement data to generate movement IDs, calculate distances, speed, 
       and other movement-related statistics.

       Steps:
       ------
       1. Sets UTC time to CEST or EST time according to the time of the year
       2. Converts latitude and longitude to float.
       3. Identifies unique movements where lat/lng change.
       4. Sorts movements chronologically.
       5. Calculates the distance between consecutive points using the Haversine formula.
       6. Computes the time difference between consecutive points.
       7. Calculates speed (distance/time).
       8. Assigns movement IDs based on thresholds for distance and time.
       9. Computes average speed for each movement.

       Returns:
       -------
       movements_df : pandas.DataFrame
           A DataFrame containing processed data with added columns for distance, time difference,
           speed, and movement ID, as well as the average speed for each movement.
       """
        if self.verbose > 0:
            print("\nStarting data processing...")
       
        self.data['_time_EST'] = self.data['_time'].dt.tz_convert('Europe/Madrid')
        if self.verbose > 1:
            print("Converted UTC time to Europe/Madrid time zone.")
          
        self.data[['lat', 'lng']] = self.data[['lat', 'lng']].astype(float)
        if self.verbose > 1:
            print("Converted lat/lng columns to float.")  
            
        list_movements = [{
            'time': self.data['_time_EST'].iloc[0],
            'lat': self.data['lat'].iloc[0],
            'lng': self.data['lng'].iloc[0]
        }]
        
        # Filter for unique movements
        for i in range(len(self.data) - 1):
            if self.data['lat'].iloc[i] != self.data['lat'].iloc[i + 1] or self.data['lng'].iloc[i] != self.data['lng'].iloc[i + 1]:
                list_movements.append({
                    'time': self.data['_time_EST'].iloc[i + 1],
                    'lat': self.data['lat'].iloc[i + 1],
                    'lng': self.data['lng'].iloc[i + 1]
                })
                
        movements_df = pd.DataFrame(list_movements)
        movements_df = movements_df.sort_values(by='time', ascending=True).reset_index(drop=True)
        if self.verbose > 1:
            print(f"Identified and sorted {len(movements_df)} unique movements in space.")
            
        # Calculate distances
        distances = []
        for i in range(1, len(movements_df)):
            dist = self.haversine(movements_df['lat'].iloc[i - 1], movements_df['lng'].iloc[i - 1],
                                  movements_df['lat'].iloc[i], movements_df['lng'].iloc[i])
            distances.append(dist)
       
        if self.verbose > 1:
            print("Calculated distances between consecutive points.")
        
        movements_df['distance_m'] = [0] + distances  # First distance is 0 since there's no previous point
        movements_df['time_diff'] = movements_df['time'].diff().dt.total_seconds()
        movements_df['speed_m_s'] =  movements_df['distance_m'] /  movements_df['time_diff']
        movements_df.fillna(0, inplace=True)
        if self.verbose > 1:
            print("Calculated time differences and speeds.")
            
        movement_id = 0
        movement_list = []
        time_spacing = 120 #Used to be 60, adjust if needed.
        for i in range(len(movements_df)):
            if movements_df['distance_m'][i] > time_spacing or movements_df['time_diff'][i] > time_spacing: 
                movement_id += 1
            movement_list.append(movement_id)
        movements_df['movement_id'] = movement_list
        if self.verbose > 0:
            print(f"Assigned movement IDs according to time between steps (set to {time_spacing}).")
            
        average_speeds_dict = {}
        for i in movements_df['movement_id'].unique():
            
            individual_movement = movements_df[movements_df['movement_id'] == i]
            individual_movement = individual_movement.sort_values(by='time', ascending=True).reset_index(drop=True)
            
            if len(individual_movement) > 1:
                individual_movement_without_first = individual_movement.drop(individual_movement.index[0])
                average_speed = individual_movement_without_first['speed_m_s'].sum()/len(individual_movement_without_first)
            else:
                average_speed = 0
            
            average_speeds_dict[i] = average_speed
        average_speeds_list=[]
        for i in range(len(movements_df)):
            average_speeds_list.append(average_speeds_dict[movements_df['movement_id'][i]])
          
        movements_df['avg_speed_m_s'] = average_speeds_list
        if self.verbose > 0:
            print("Processed all data and calculated average speeds for each movement.")
            
        if self.verbose > 1:
            print("Final processed DataFrame:")
            print(movements_df.head())
        return movements_df


