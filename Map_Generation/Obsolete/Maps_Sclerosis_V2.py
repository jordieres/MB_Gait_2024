# -*- coding: utf-8 -*-
"""




Created on Sun Sep 29 16:50:23 2024
@author: marbo
"""

#!/usr/bin/python3
import sys
import json
import cgi
import os
import gzip
import datetime
import shutil
import cgitb
import argparse
import pandas as pd
import numpy as np
from influxdb_client import InfluxDBClient
from itertools import islice
from subprocess import call
import matplotlib.pyplot as plt
import folium
from geopy.distance import geodesic
import plotly.express as px
import plotly.graph_objects as go

#Write in IDE Console: runfile('C:/Users/marbo/Documents/Maps_Sclerosis_V2.py', wdir='C:/Users/marbo/Documents', args='-f 2024-06-16 -u 2024-06-18 -q MGM-202406-79 -p Right')
# Change the arguments as needed. q = qtok, -p = pie (left or right)

# Custom action for handling verbose levels in argparse
class VAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, const=None,
                 default=None, type=None, choices=None, required=False,
                 help=None, metavar=None):
        super(VAction, self).__init__(option_strings, dest, nargs, const,
                                      default, type, choices, required,
                                      help, metavar)
        self.values = 0

    def __call__(self, parser, args, values, option_string=None):
        if values is None:
            self.values += 1
        else:
            try:
                self.values = int(values)
            except ValueError:
                self.values = values.count('v') + 1
        setattr(args, self.dest, self.values)


# Database settings
org = 'UPM'
database = 'SSL'
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'

# Token
tokenv2 = 'Zx2jR8PD6h3YlS7HVsY5Han1SzF_iz7uk8n5z9BYRZ5q50lk8r1L18N-nFZiGCa57oowLgl8656pVpCig-GANg=='
####Token para fechas anteriores: 
    # 1_lyKS1xcKU4NwneJiUsKTaa5gohz98YwYNzzM52LlQnUzBrMf18Tr9ujotYCVXNSkGntS9RJCUtYwBpU3cHSg==








# Parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--from", type=str, required=True, help="Date for starting the analysis. Format YYYY-MM-DD.")
ap.add_argument("-u", "--until", type=str, required=True, help="Date for ending the analysis. Format YYYY-MM-DD.")
ap.add_argument("-v", "--verbose", nargs='?', action=VAction, dest='verbose', help="Option for detailed information.")
ap.add_argument("-q", "--qtok", type=str, required=True, help="Enter the qtok value (e.g., 'MGM-202406-79').")
ap.add_argument("-p", "--pie", type=str, choices=["Right", "Left"], required=True, help="Enter the foot ('Right' or 'Left').")

args = vars(ap.parse_args())

# Get qtok and pie from arguments
qtok = args['qtok']
pie = args['pie']

# Set verbosity level
verbose = args['verbose'] if args['verbose'] else 0

# Date range for querying
desde = f"{args['from']}T00:00:00Z"
hasta = f"{args['until']}T23:59:59Z"



# InfluxDB query for after 11/03/2024
query = '''
from(bucket:"Gait/autogen")
  |> range(start: {start}, stop: {end})
  |> filter(fn: (r) => r["_measurement"] == "Gait")
  |> filter(fn: (r) => r["CodeID"] == "{qtok}" and r["type"] == "SCKS" and r["Foot"] == "{pie}")
  |> filter(fn: (r) => r["_field"] == "S0")
  |> yield()
'''.format(start=desde, end=hasta, qtok=qtok, pie=pie)


# Query para fechas anteriores: 
    # query = ' from(bucket:"SSL/autogen")\
#|> range(start: ' + desde + ', stop: ' + hasta + ')\
#|> filter(fn:(r) => r._measurement == "sensoria_socks" and \
#(r._field=="S0" or r._field=="S1" or r._field=="S2"))\
#|> yield()'
#
# Query InfluxDB
clnt = InfluxDBClient(url='https://apiivm78.etsii.upm.es:8086', token=tokenv2, org=org)
result = clnt.query_api().query(org=org, query=query)

# Convert result to DataFrame
res = pd.DataFrame()
for i in result:
    rs = [row.values for row in i.records]
    res = pd.concat([res, pd.DataFrame(rs)], axis=0)

res = res.drop(res.columns[[0]], axis=1)
res.reset_index(drop=True, inplace=True)
print(res)

# Convert latitude and longitude to float
res[['lat', 'lng']] = res[['lat', 'lng']].astype(float)

# Initialize the list to store movements
list_movements = [{
    'time': res['_time'].iloc[0],  # First time value
    'lat': res['lat'].iloc[0],     # First latitude value
    'lng': res['lng'].iloc[0]      # First longitude value
}]

# Loop through the DataFrame to detect movements
for i in range(len(res) - 1):
    if res['lat'].iloc[i] != res['lat'].iloc[i + 1] or res['lng'].iloc[i] != res['lng'].iloc[i + 1]:
        list_movements.append({
            'time': res['_time'].iloc[i + 1],  # Next time value
            'lat': res['lat'].iloc[i + 1],
            'lng': res['lng'].iloc[i + 1]
        })

# Convert list of movements to DataFrame
movements_df = pd.DataFrame(list_movements)
print(movements_df)

# Create folium map
pos_init = [res['lat'][0], res['lng'][0]]
m = folium.Map(location=pos_init, zoom_start=12)

# Add markers and polylines to the map
for i in range(len(movements_df)):
    point1 = (movements_df['lat'].iloc[i], movements_df['lng'].iloc[i])
    folium.Marker(point1, tooltip=f"Point: {i} | Time: {movements_df['time'].iloc[i]}").add_to(m)
    
    if i > 0:
        point0 = (float(movements_df['lat'].iloc[i - 1]), float(movements_df['lng'].iloc[i - 1]))
        folium.PolyLine([point0, point1], color="blue", weight=2.5, opacity=1).add_to(m)

# Save folium map to an HTML file
m.save("map_v1.html")

# Plotly map for visualization
fig = go.Figure()

# Add scatter points for each location with time in the label
text_labels = [f"Point {i}: {movements_df['time'].iloc[i]}" for i in range(len(movements_df))]

# Add markers to the Plotly map
fig.add_trace(go.Scattermapbox(
    lat=movements_df['lat'],
    lon=movements_df['lng'],
    mode='markers+text',
    text=text_labels,
    marker=dict(size=10, color='blue'),
    textposition="top center"
))

# Add lines connecting the points
fig.add_trace(go.Scattermapbox(
    lat=movements_df['lat'],
    lon=movements_df['lng'],
    mode='lines',
    line=dict(width=2, color='blue'),
))

# Update layout with mapbox style
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=15,
    mapbox_center={"lat": movements_df['lat'].mean(), "lon": movements_df['lng'].mean()},
    height=600
)

# Save the Plotly map to an HTML file
fig.write_html("map_v2.html")
