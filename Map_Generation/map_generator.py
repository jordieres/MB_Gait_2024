# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:06:07 2024

@author: marbo
"""


import plotly.graph_objects as go

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
        Different movement IDs are represented by different colors, and the map provides detailed
        information for each movement, such as start time, average speed, and duration.

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
        # Define a color map for different movement_ids
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
        unique_ids = self.movements_df['movement_id'].unique()
        
        self._print(f"Found {len(unique_ids)} unique movements.", level=2)
        
        for movement_id in unique_ids:
            # Filter data for the current movement_id
            group_df = self.movements_df[self.movements_df['movement_id'] == movement_id]
            text_labels = [f"Point {i}: {time}" for i, time in enumerate(group_df['time'])]
    
            # Get relevant data of the movement (first entry in the group)
            start_time = group_df['time'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')
            avg_speed = round(group_df['avg_speed_m_s'].iloc[0], 2)
            number_of_data_points = len(group_df)
            duration = round(group_df['time_diff'][1:].sum(), 1)
            hours, remainder = divmod(duration, 3600)  
            minutes, seconds = divmod(remainder, 60)
            
            self._print(f"Movement ID {movement_id}: Start: {start_time}, Avg Speed: {avg_speed}, "
                            f"Duration: {int(hours)}h {int(minutes)}m {int(seconds)}s, Data Points: {number_of_data_points}", level=2)  
            
            
            # Adding markers with labels
            fig.add_trace(go.Scattermapbox(
                lat=group_df['lat'],
                lon=group_df['lng'],
                mode='markers+text',  # Ensure markers and text are shown
                text=text_labels,  # Adding the labels
                marker=dict(size=10, color=colors[movement_id % len(colors)]),  # Use color based on movement_id
                textposition="top right",  # Adjust position of the text relative to the point
                hoverinfo='text',  # Show text on hover
                name=(
                    f'Movement ID {movement_id}<br>'  # Use <br> for line breaks
                    f'Start: {start_time}<br>' 
                    f'Average speed: {avg_speed} m/s<br>'
                    f'Duration: {duration} s<br>'
                    f'Number of Datapoints: {number_of_data_points}'
                ),  # Name with start time for the trace
                customdata=group_df['time'],  # Use customdata to hold additional info
                hovertemplate='<b>%{customdata}</b>'  # Custom hover template
            ))
    
            # Adding lines connecting the points for the same movement_id
            fig.add_trace(go.Scattermapbox(
                lat=group_df['lat'],
                lon=group_df['lng'],
                mode='lines',
                line=dict(width=2, color=colors[movement_id % len(colors)]),  # Same color as markers
                #name=f'Movement ID {movement_id} (Start: {start_time})'  # Ensure the same name for the line
                name=f'Movement ID {movement_id}',
                #showlegend=False
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
            showlegend=True,  # Show legend if you have multiple traces
            dragmode='zoom'  # Enables zoom with mouse drag
        )
    
        # Callback for click events to show labels
        fig.update_traces(marker=dict(size=10, opacity=0.5), selector=dict(mode='markers'))
    
        # Construct the file name using qtok, start_date, and end_date
        file_name = f"map_{qtok}_{start_date}_{end_date}.html"
    
        # Save the Plotly map to an HTML file
        fig.write_html(file_name, config={"scrollZoom": True})
        self._print(f"Map saved to {file_name}.", level=1)
    
    
