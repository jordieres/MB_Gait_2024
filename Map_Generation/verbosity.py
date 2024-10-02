# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 19:20:58 2024

@author: marbo
"""

class Verbosity:
    def __init__(self, level, qtok, start, end, raw_data, movements_df):
        """
        Initialize a Verbosity instance.

        Parameters:
        level (int): The verbosity level (0 to 3).
        qtok (str): Token for the process.
        start (str): Start date for the process.
        end (str): End date for the process.
        movements_df (DataFrame): A DataFrame containing movement data.
        
        Raises:
        ValueError: If level is not between 0 and 3.
        """
        if level < 0 or level > 3:
            raise ValueError("Verbosity level must be between 0 and 3.")
        self.level = level
        self.qtok = qtok
        self.start = start
        self.end = end
        self.raw_data = raw_data
        self.movements_df = movements_df

    def print_info(self):
        """Print information based on the verbosity level."""
        if self.level == 0:
            print("Process complete, check folder for html maps.")
        
        elif self.level == 1:
            raw_data_points = len(self.raw_data)
            number_of_movements = len(self.movements_df['movement_id'].unique())
            print("Process complete, check folder for html maps.")
            print(f"QTOK: {self.qtok}, Start Date: {self.start}, End Date: {self.end}")
            print(f"Number of raw data points: {raw_data_points}")
            print(f"Number of different movements detected: {number_of_movements}")
            
        elif self.level == 2:
            raw_data_points = len(self.raw_data)
            number_of_movements = len(self.movements_df['movement_id'].unique())
            print("Process complete, check folder for html maps.")
            print(f"QTOK: {self.qtok}, Start Date: {self.start}, End Date: {self.end}")
            print(f"Number of raw data points: {raw_data_points}")
            print(f"Number of different movements detected: {number_of_movements}")
            print("")
            unique_ids = self.movements_df['movement_id'].unique()
        
            for movement_id in unique_ids:
                # Filter data for the current movement_id
                group_df = self.movements_df[self.movements_df['movement_id'] == movement_id]
                
        
                # Get relevant data of the movement (first entry in the group)
               
                avg_speed = round(group_df['avg_speed_m_s'].iloc[0], 2)
                number_of_data_points = len(group_df)
                duration = round(group_df['time_diff'][1:].sum(), 1)               
                distance_travelled = round(group_df['distance_m'][1:].sum(), 2)  
                movement_start_time = group_df['time'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')
                movement_end_time = group_df['time'].iloc[number_of_data_points - 1].strftime('%Y-%m-%d %H:%M:%S')
                print(f"Movement {movement_id}:")
                print(f'\tNumber of data points: {number_of_data_points}')
                print(f'\tMovement start time: {movement_start_time}')
                print(f'\tMovement end time: {movement_end_time}')
                print(f'\tDuration: {duration} s')
                print(f'\tAverage_Speed: {avg_speed} m/s')
                print(f'\tDistance travelled: {distance_travelled} m')
                print("")
                
        elif self.level == 3:
            print("Otros objetos importantes")