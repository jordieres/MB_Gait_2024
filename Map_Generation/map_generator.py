# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:06:07 2024

@author: marbo
"""


import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np

class MapGenerator:
    """
    A class to generate maps visualizing movements using Folium and Plotly.
    
    Attributes:
    ----------
    movements_df : pandas.DataFrame
        A DataFrame containing movement data with columns such as 'lat', 'lng', 'time', and 'movement_id'.
    verbose : int
        Verbosity level (0, 1, or 2) that controls the level of detail printed.
    """
    
    
    def __init__(self, movements_df, verbose=0):
        """
        Initializes the MapGenerator with a DataFrame of movement data.
        
        Parameters:
        ----------
        movements_df : pandas.DataFrame
            A DataFrame containing columns for latitude, longitude, timestamps, movement ID, etc.
        verbose : int, optional
            Verbosity level (0: no output, 1: basic output, 2: detailed output), by default 0.
        """
        
        self.movements_df = movements_df
        self.verbose = verbose

    def _print(self, message, level=1):
            """ Helper method to print messages based on verbosity level. """
            if self.verbose >= level:
                print(message)


    def generate_plotly_map(self, qtok, start_date, end_date):
        """
        Generates an interactive Plotly map that visualizes movement data using markers and lines.
        Scatter points will have different colors for each movement ID, and lines will be colored by speed.
    
        Parameters:
        ----------
        qtok : str
            A unique identifier for the movement data (can represent a user or session).
        start_date : str
            The start date of the movements in a string format (YYYY-MM-DD).
        end_date : str
            The end date of the movements in a string format (YYYY-MM-DD).
    
        Returns:
        -------
        None
        """
        fig = go.Figure()
    
        self._print(f"\nGenerating map for {qtok} from {start_date} to {end_date}...", level=1)
    
        # List of colors for the different movement IDs
        colors = [
            'blue', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow',
            'black', 'brown', 'pink', 'grey', 'lightblue', 'lightgreen', 'darkred',
            'lightcoral', 'gold', 'darkblue', 'darkgreen', 'lime', 'teal', 'navy',
            'indigo', 'violet', 'salmon', 'khaki', 'lavender', 'chocolate',
            'darkorange', 'crimson', 'mediumvioletred', 'mediumseagreen',
            'steelblue', 'slategray', 'dimgray', 'tan', 'orchid', 'lightpink',
            'mediumslateblue', 'darkslategray', 'sandybrown', 'lightyellow',
            'lightslategray', 'aliceblue', 'powderblue', 'mediumturquoise'
        ]
    
        # Normalize speed for color scaling
        min_speed = self.movements_df['speed_m_s'].min()
        max_speed = self.movements_df['speed_m_s'].max()
    
        norm_speed = (self.movements_df['speed_m_s'] - min_speed) / (max_speed - min_speed)
        norm_speed = np.nan_to_num(norm_speed, nan=0)
        # Use Plotly's color scale to generate colors for speeds
        cmap = px.colors.sample_colorscale('Turbo', norm_speed)
    
        unique_ids = self.movements_df['movement_id'].unique()
        color_map = {movement_id: colors[i % len(colors)] for i, movement_id in enumerate(unique_ids)}  # Color by movement_id
    
        self._print(f"Found {len(unique_ids)} unique movements.", level=2)
    
        for movement_id in unique_ids:
            # Filter data for the current movement_id
            group_df = self.movements_df[self.movements_df['movement_id'] == movement_id]
            group_df['local_time'] = pd.to_datetime(group_df['local_time'], errors='coerce')
            text_labels = [
                f"Point {i}: {local_time}, Timezone: {local_timezone}"
                for i, (local_time, local_timezone)
                in enumerate(zip(group_df['local_time'].dt.strftime("%Y-%m-%d %H:%M:%S"), group_df['local_timezone']))
            ]
    
            # Get relevant data of the movement (first entry in the group)
            start_time = group_df['local_time'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')
            timezone = group_df['local_timezone'].iloc[0]
            avg_speed = round(group_df['avg_speed_m_s'].iloc[0], 2)
            number_of_data_points = len(group_df)
            duration = round(group_df['time_diff'][1:].sum(), 1)
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)
    
            self._print(f"Movement ID {movement_id}: Start: {start_time} {timezone}, Avg Speed: {avg_speed} m/s, "
                        f"Duration: {int(hours)}h {int(minutes)}m {int(seconds)}s, Data Points: {number_of_data_points}", level=2)
    
            # Adding scatter points for the movement
            fig.add_trace(go.Scattermapbox(
                lat=group_df['lat'],
                lon=group_df['lng'],
                mode='markers+text',  # Ensure markers and text are shown
                text=text_labels,  # Adding the labels
                marker=dict(
                    size=5,
                    color=color_map[movement_id],  # Color based on movement_id
                ),
                textposition="top right",  # Adjust position of the text relative to the point
                hoverinfo='text',  # Show text on hover
                name=f'Movement ID {movement_id}',  # Name for the legend
                customdata=group_df['time'],  # Use customdata to hold additional info
                hovertemplate='<b>%{customdata}</b>'  # Custom hover template
            ))
    
            # Adding lines between points, using the cmap for speed
            for i in range(len(group_df) - 1):  # Iterate through the points to draw lines between them
                speed_color = cmap[i + 1]  # Get the color corresponding to the speed
    
                fig.add_trace(go.Scattermapbox(
                    lat=[group_df['lat'].iloc[i], group_df['lat'].iloc[i + 1]],
                    lon=[group_df['lng'].iloc[i], group_df['lng'].iloc[i + 1]],
                    mode='lines',
                    line=dict(
                        width=3,
                        color=speed_color,  # Color based on the mapped color
                    ),
                    showlegend=False,  # Hide the line from the legend
                    hoverinfo='none',  # Hide hover info for lines
                    hovertemplate='',  # Disable hover template for lines
                ))
        # Define more intermediate tick values for the color scale
        tick_vals = [min_speed, min_speed + (max_speed - min_speed) / 4, 
                     min_speed + (max_speed - min_speed) / 2,
                     min_speed + 3 * (max_speed - min_speed) / 4, max_speed]
    
        tick_text = [f'{min_speed:.2f}', f'{min_speed + (max_speed - min_speed) / 4:.2f}', 
                     f'{min_speed + (max_speed - min_speed) / 2:.2f}', 
                     f'{min_speed + 3 * (max_speed - min_speed) / 4:.2f}', f'{max_speed:.2f}']
        # Add a dummy trace for the color scale
        fig.add_trace(go.Scattermapbox(
            lat=[None],  # Empty lat/lon to avoid plotting any point
            lon=[None],
            mode='markers',
            marker=dict(
                colorscale='Turbo',  # Use the same 'Turbo' color scale
                cmin=min_speed,  # Set the minimum of the color scale
                cmax=max_speed,  # Set the maximum of the color scale
                colorbar=dict(
                    title="Speed (m/s)",  # Title for the color bar
                    titleside='right',
                    tickvals=tick_vals,  # Show the min and max values
                    ticktext=tick_text,  # Format the tick text
                    len=0.75,  # Length of the colorbar
                    thickness=20,  # Thickness of the colorbar
                    x=1.05,  # Position it outside the plot on the right
                    y=0.5,  # Center the colorbar vertically
                ),
                showscale=True  # Ensure that the color scale is shown
            ),
            showlegend=False,  # Do not show this trace in the legend
            hoverinfo='none'  # No hover information for this trace
        ))
    
        self._print(f"Map generation complete for {qtok}.", level=1)
    
        title_text = f"Movements for {qtok} from {start_date} to {end_date}"
    
        # Update layout with mapbox style and centering
        fig.update_layout(
            title={
                'text': title_text,
                'y': 0.95,  # Position the title slightly downwards
                'x': 0.5,   # Center the title
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 24},  # Adjust font size
            },
            mapbox=dict(
                style="carto-positron",  # Style of the map
                center=dict(lat=self.movements_df['lat'].mean(), lon=self.movements_df['lng'].mean()),
                zoom=12,
            ),
            height=800,
            width=1200,
            showlegend=True,  # Show legend for scatter points
            dragmode='zoom',  # Enables zoom with mouse drag
            legend=dict(
                x=0,  # Move the legend to the left
                y=1,  # Position it near the top
                bgcolor="rgba(255,255,255,0.6)",  # Set a semi-transparent background
                bordercolor="Black",  # Add a border for visibility
                borderwidth=2
            )
        )
    
        # Adjust marker properties globally (optional)
        fig.update_traces(marker=dict(size=5, opacity=0.5), selector=dict(mode='markers'))
    
        # Construct the file name using qtok, start_date, and end_date
        sanitized_start = re.sub(r'[:]', '-', start_date)
        sanitized_end = re.sub(r'[:]', '-', end_date)
        file_name = f"map_{qtok}_{sanitized_start}_{sanitized_end}.html"
      
    
        # Save the Plotly map to an HTML file
        fig.write_html(file_name, config={"scrollZoom": True})
        self._print(f"Map saved to {file_name}.", level=1)
