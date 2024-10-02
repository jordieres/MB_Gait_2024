**Movement Data Analyzer**

This project is designed to fetch, process, and visualize movement data based on input parameters such as time range, location, and identifiers. The program fetches data from a specified API, processes it to identify movements, and generates visualizations using Plotly.

**Overview**
The Movement Data Analyzer allows you to:

1. Fetch movement data from an API.
2. Process the data to calculate movement statistics such as speed, distance, and duration.
3. Generate interactive maps using Plotly and Folium that visualize movement points and routes.
4. Control the verbosity of the output to obtain more or less detailed logs of the data processing and visualization.

**Features**
Data Fetching: Retrieve movement data based on date ranges, identifiers (qtok), and other filters.
Data Processing: Calculate distances, speeds, and other movement metrics using geospatial data.
Map Visualization: Generate interactive maps with movement paths and detailed tooltips.
Customizable Verbosity: Optionally view detailed processing steps and logs through command-line verbosity levels.

**Requirements**
The following libraries are required to run the program:

Python 3.x
pandas
numpy
argparse
plotly
Any additional dependencies can be installed from the requirements.txt if provided.

**Usage:**

From Spyder IDE
runfile('path/main.py', wdir='C:/Users/marbo/Documents', args='-f 2024-06-16 -u 2024-06-17 -v 2 -q MGM-202406-79 -p Right')

From Prompt:
python main.py -f 2024-06-16 -u 2024-06-17 -v 2 -q MGM-202406-79 -p Right

**Configuration**
The program uses a TOML file for configuration. Ensure the configuration file (config.toml) is properly set up before running the program.

**DataFetcher Class:**
The DataFetcher class retrieves movement data from an external API based on the following parameters:

qtok: The unique identifier for the dataset.
pie: Indicates whether the data refers to the left or right foot.
start_date: The beginning of the analysis period.
end_date: The end of the analysis period.

**DataProcessor:**
Once the data is fetched, the DataProcessor class processes the raw data:

Haversine Formula: This is used to calculate distances between two points on the Earth’s surface.
Movement Calculation: The processor identifies unique movements and calculates metrics such as distance, speed, and movement duration.

**Map Generation**
Plotly Map:
The generate_plotly_map method generates an interactive map with movement lines and hover tooltips showing detailed information like average speed and duration.

**Verbosity**
The Verbosity class controls the level of information printed during execution:

Level 0: Minimal output.
Level 1+: More detailed logs (e.g., data summaries, step-by-step processing).
