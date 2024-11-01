.. TFM_Sclerosis documentation master file, created by
   sphinx-quickstart on Mon Sep 30 16:50:23 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Code Documentation
==================

Data Fetcher Module
===================

The `data_fetcher` module contains the `DataFetcher` class, which is used to retrieve data from InfluxDB for analysis.

Module Overview
---------------

.. automodule:: data_fetcher
    :members:
    :undoc-members:
    :show-inheritance:

Classes
-------

DataFetcher
^^^^^^^^^^^

.. autoclass:: data_fetcher.DataFetcher
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

    This class is responsible for fetching data from InfluxDB, configured to pull specific data based on query tokens and date ranges.

    **Attributes:**

        - `qtok` (str): Query token for the InfluxDB query.
        - `pie` (str): Foot side ("Right" or "Left").
        - `start_date` (str): Start date for the query.
        - `end_date` (str): End date for the query.
        - `token` (str): InfluxDB token.
        - `org` (str): InfluxDB organization name.
        - `url` (str): InfluxDB URL.
        - `verbose` (int): Controls verbosity of output.

    **Methods:**

        - `build_query()`: Constructs the InfluxDB query string.
        - `fetch_data()`: Executes the query and returns the data as a pandas DataFrame.

Methods
--------------

build_query
^^^^^^^^^^^

.. automethod:: data_fetcher.DataFetcher.build_query
    :noindex:

    Constructs and returns a query string to fetch data from InfluxDB based on the instance's configuration attributes.

fetch_data
^^^^^^^^^^

.. automethod:: data_fetcher.DataFetcher.fetch_data
    :noindex:

    Fetches data by executing the constructed query and returns it as a pandas DataFrame. Displays progress messages if verbosity is enabled.


Data Processor Module
=====================

The `data_processor` module contains the `DataProcessor` class, which is used to process movement data. It handles calculations for distances, speeds, and movement IDs, corrects coordinates, and converts UTC timestamps to local times based on geolocation data.

Module Overview
---------------

.. automodule:: data_processor
    :members:
    :undoc-members:
    :show-inheritance:

Classes
-------

DataProcessor
^^^^^^^^^^^^^

.. autoclass:: data_processor.DataProcessor
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

    This class processes and cleans movement data for further analysis, such as identifying unique movements, calculating distances and speeds, correcting coordinates, and assigning movement IDs.

    **Attributes:**

        - `data` (pandas.DataFrame): Input data with movement details, including '_time', 'lat', and 'lng'.
        - `verbose` (int): Level of verbosity for output messages.
        - `tf` (TimezoneFinder): Tool to find the timezone based on geolocation data.

    **Methods:**

        - `haversine(coord1, coord2)`: Calculates the great-circle distance between two coordinates.
        - `calculate_speed(coord1, coord2, time1, time2)`: Determines the speed between two points based on distance and time.
        - `correct_point(data, i, speed_threshold)`: Checks and corrects coordinates based on speed anomalies.
        - `correct_coordinates_with_speed(data, speed_threshold=30)`: Corrects coordinates in the DataFrame based on excessive speed.
        - `get_coordinates(data, i)`: Retrieves coordinates for a point and its neighbors in the DataFrame.
        - `convert_utc_to_local(row)`: Converts UTC timestamp to local time based on latitude and longitude.
        - `identify_movements()`: Identifies unique movements by filtering out duplicate consecutive coordinates.
        - `calculate_distances_and_speeds(movements_df)`: Adds calculated distances and speeds between consecutive points.
        - `assign_movement_ids(movements_df, time_spacing=120)`: Assigns unique IDs to each movement segment.
        - `calculate_avg_speeds(movements_df)`: Computes the average speed for each movement segment.
        - `process_data(time_spacing=120)`: Performs the full data processing workflow.

Methods
--------------

haversine
^^^^^^^^^

.. automethod:: data_processor.DataProcessor.haversine
    :noindex:

    Calculates the great-circle distance between two points on Earth.

calculate_speed
^^^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.calculate_speed
    :noindex:

    Calculates the speed between two points based on distance and time. Returns infinity if time difference is zero to avoid division by zero.

correct_point
^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.correct_point
    :noindex:

    Checks if the point at a given index needs correction based on speed thresholds. If so, averages the surrounding points to correct the outlier.

correct_coordinates_with_speed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.correct_coordinates_with_speed
    :noindex:

    Iterates through the DataFrame to identify and correct anomalous points based on excessive speeds.

get_coordinates
^^^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.get_coordinates
    :noindex:

    Retrieves latitude and longitude for three consecutive points: the previous, current, and next points.

convert_utc_to_local
^^^^^^^^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.convert_utc_to_local
    :noindex:

    Converts UTC timestamp to local time using latitude and longitude to identify the appropriate timezone.

identify_movements
^^^^^^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.identify_movements
    :noindex:

    Identifies unique movements by excluding consecutive duplicate coordinates, returning a sorted DataFrame.

calculate_distances_and_speeds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.calculate_distances_and_speeds
    :noindex:

    Calculates distances, time differences, and speeds between consecutive points and adds them to the DataFrame.

assign_movement_ids
^^^^^^^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.assign_movement_ids
    :noindex:

    Assigns unique movement IDs based on time and distance thresholds to segment continuous movements.

calculate_avg_speeds
^^^^^^^^^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.calculate_avg_speeds
    :noindex:

    Calculates average speed for each movement segment, skipping the initial data point.

process_data
^^^^^^^^^^^^

.. automethod:: data_processor.DataProcessor.process_data
    :noindex:

    Executes the full data processing pipeline, including data cleaning, movement segmentation, speed calculation, and time conversion to local time based on geolocation.



Map Generator Module
====================

This module provides the `MapGenerator` class, which is designed for visualizing movements data using Folium and Plotly. The class can produce interactive maps with customizable markers and lines representing speed and movement across locations.

.. module:: map_generator
   :synopsis: Module for generating movement maps using Plotly.

Classes
-------

.. autoclass:: MapGenerator
   :members:
   :undoc-members:
   :show-inheritance:

   Class Attributes
   ----------------

   - **movements_df** (pandas.DataFrame): Holds movement data, including latitude, longitude, time, speed, and movement ID.
   - **verbose** (int): Sets verbosity level for printed details (0: no output, 1: basic output, 2: detailed output).

Methods
-------

.. automethod:: MapGenerator.__init__

   Initializes the `MapGenerator` with movement data and verbosity setting.

   Parameters:
      - **movements_df** (pandas.DataFrame): Data containing latitude, longitude, timestamps, movement ID, and speed.
      - **verbose** (int, optional): Verbosity level (default: 0).

.. automethod:: MapGenerator._print

   Helper method to print messages conditionally, based on verbosity.

   Parameters:
      - **message** (str): Message to print.
      - **level** (int, optional): Verbosity threshold (default: 1).

.. automethod:: MapGenerator.generate_plotly_map

   Creates an interactive map using Plotly, displaying markers and lines colored by speed and movement ID. The map visualizes movements across locations within a date range, labeled with local times and time zones.

   Parameters:
      - **qtok** (str): Unique identifier for the movement session (e.g., user or session ID).
      - **start_date** (str): Start date of movement data in "YYYY-MM-DD" format.
      - **end_date** (str): End date of movement data in "YYYY-MM-DD" format.

   Returns:
      None. The map is saved as an HTML file, including interactivity and color-coded data based on speed.

Main Ext GPS Module
====================

This module is a command-line interface for fetching, processing, and visualizing movement data using configurable options such as verbosity, date range, and output settings. The main function coordinates data retrieval, processing, and map generation.

.. module:: main_script
   :synopsis: Command-line script for fetching, processing, and visualizing movement data.

Classes
-------

.. autoclass:: VAction
   :members:
   :undoc-members:
   :show-inheritance:

   Handles verbosity levels for argparse options, allowing flexibility in setting output detail by parsing the number of `-v` flags.

   Attributes
   ----------
   values : int
       Holds the verbosity level based on the number of 'v' flags provided.

   Methods
   -------
   
   .. automethod:: VAction.__init__
   
      Initializes the custom argparse action for verbosity level handling.

      Parameters:
         - **option_strings** (list): List of option flags (e.g., `["-v", "--verbose"]`).
         - **dest** (str): Destination variable for storing the verbosity level.
         - **help** (str, optional): Help text for this argument.

   .. automethod:: VAction.__call__

      Sets the verbosity level according to the argument string provided (e.g., `"vv"` for level 2).

      Parameters:
         - **parser** (ArgumentParser): The argparse parser instance.
         - **args** (Namespace): Parsed arguments namespace.
         - **values** (str): Verbosity level string (e.g., `"vv"`).
         - **option_string** (str, optional): The option flag used (e.g., `"-v"`).

Functions
---------

.. autofunction:: main

   Main function to run the data processing workflow. This function parses command-line arguments and performs the following steps:

   1. Loads configuration settings.
   2. Parses command-line arguments for date range, verbosity, and other parameters.
   3. Fetches data via the `DataFetcher` class.
   4. Processes data using the `DataProcessor`.
   5. Generates an interactive movement map with `MapGenerator`.
   6. Saves the data to a pickle file.
   7. Outputs a summary using the `Output` class.

   Command-Line Arguments
   ----------------------

      - **-f**, **--from**: Starting date in "YYYY-MM-DD" format.
      - **-u**, **--until**: Ending date in "YYYY-MM-DD" format.
      - **-v**, **--verbose**: Sets verbosity level for output (e.g., `-v` for basic, `-vv` for detailed).
      - **-q**, **--qtok**: Unique identifier for movement data (e.g., user or session ID).
      - **-p**, **--pie**: Selects foot type (`"Right"` or `"Left"`).
      - **-o**, **--output**: Output verbosity level (0 to 2, with 2 as default).
      - **-t**, **--time-spacing**: Time spacing in seconds for segmenting data (default: 120).

   Returns
   -------
   None. Outputs are printed to the console and saved to an HTML file for interactive visualization.