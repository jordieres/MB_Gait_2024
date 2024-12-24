.. TFM_Sclerosis documentation master file, created by
   sphinx-quickstart on Mon Sep 30 16:50:23 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Code Documentation
==================

GaitAnalysis Class
==================

The `GaitAnalysis` class is designed for analyzing gait data, including processing and visualizing sensor data (e.g., acceleration, gyroscope, magnetometer, pressure) for left and right feet.

Methods
--------

### __init__(self, data, verbosity=0)

Initializes the `GaitAnalysis` class with the provided data.

Arguments:
- **data** (`pd.DataFrame`): The dataframe containing sensor data.
- **verbosity** (`int`): Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output).

### preprocess_data(self)

Preprocesses and separates data based on sensor types and foot placement (Right/Left). Filters the data to create separate DataFrames for acceleration, gyroscope, magnetometer, and pressure data for both the right and left foot. All data is sorted by the `_time` column.

Returns:
- **dict**: A dictionary containing the processed DataFrames for the different sensor types and foot placements.

### plot_data(self, data_dict)

Plots various sensor data for both left and right feet. It creates multiple plots for heel pressure, toe pressure, acceleration, gyroscope, and magnetometer data. The plots can include specific slices of the data (e.g., the first 500 values or a detailed view of the data).

Arguments:
- **data_dict** (`dict`): A dictionary containing the processed data returned by the `preprocess_data()` method.

The following plots are generated:
- Heel Pressure (S0) for Left and Right Foot
- A closer look at the Heel Pressure (S0)
- Heel Pressure (S0) and Toe Pressure (S1) for Right Foot
- Accelerometer Data (X, Y, Z) for Left Foot
- Gyroscope Data (X, Y, Z) for Left Foot
- Magnetometer Data for Left Foot

Examples of Generated Plots:
1. Heel Pressure for Left and Right Foot:
   - Plots the pressure data from the heel sensors (S0) for both the left and right feet.
2. Heel Pressure for Right Foot with Toe Pressure (S1):
   - Plots the heel pressure (S0) and toe pressure (S1) for the right foot.
3. Accelerometer and Gyroscope Data:
   - Plots the X, Y, and Z values for both accelerometer and gyroscope data over time for the left foot.
4. Magnetometer Data for Left Foot:
   - Plots the X, Y, and Z magnetic field strength values over time and computes the heading (yaw angle) in degrees.

TrajectoryAnalyzer
========================

The `TrajectoryAnalyzer` class processes sensor data (accelerometer, gyroscope, and magnetometer) to compute and visualize the movement trajectories of two feet (typically left and right) during gait analysis.

Methods
-------

### `__init__(self, data, dt=0.01, verbosity=0)`
Initializes the `TrajectoryAnalyzer` class.

- **Parameters:**
  - `data`: A dictionary containing accelerometer, gyroscope, and magnetometer data.
  - `dt`: The sampling interval between sensor data points (in seconds). Default is 0.01.
  - `verbosity`: Defines the level of verbosity for print statements. (0: silent, 1: basic, 2: detailed).
  
- **Purpose**: Initializes the class with provided data, sampling interval, and verbosity level. Optionally prints initialization details based on verbosity.

---

### `low_pass_filter(self, data, alpha=0.1)`
Applies a simple low-pass filter to smooth out noisy sensor data.

- **Parameters:**
  - `data`: The signal (e.g., accelerometer data) to be filtered.
  - `alpha`: The smoothing factor, between 0 and 1, where values closer to 1 keep more of the original signal.
  
- **Returns**: The filtered signal.
- **Purpose**: Filters the input data using an exponential moving average to reduce high-frequency noise.

---

### `compute_yaw(self, gyro_yaw, mag_x, mag_y, alpha=0.98)`
Computes the yaw angle by fusing gyroscope and magnetometer data using a complementary filter.

- **Parameters:**
  - `gyro_yaw`: Yaw angle computed from the gyroscope.
  - `mag_x`: Magnetometer X-axis data.
  - `mag_y`: Magnetometer Y-axis data.
  - `alpha`: Weighting factor for the complementary filter, where higher values give more weight to the gyroscope data.

- **Returns**: The fused yaw angle.
- **Purpose**: Combines gyroscope and magnetometer data to estimate a more accurate yaw angle.

---

### `transform_to_global_frame(self, acc_x, acc_y, acc_z, orientation)`
Transforms acceleration data from the local sensor frame to a global frame using the sensor's orientation.

- **Parameters:**
  - `acc_x`, `acc_y`, `acc_z`: Acceleration values in the local X, Y, and Z axes.
  - `orientation`: A dictionary containing roll, pitch, and yaw angles.
  
- **Returns**: The transformed acceleration in the global frame (x, y, z).
- **Purpose**: Converts the sensor's local frame of reference to a global frame using the sensor's orientation.

---

### `integrate(self, data)`
Performs cumulative integration on the given data (typically acceleration) to compute velocity and position.

- **Parameters:**
  - `data`: The input data, which could be acceleration or velocity.
  
- **Returns**: The computed velocity and position arrays.
- **Purpose**: Integrates the data twice: once to get velocity (from acceleration) and once more to get position (from velocity).

---

### `compute_trajectories(self)`
Computes the trajectories for both the left and right feet based on accelerometer, gyroscope, and magnetometer data.

- **Returns**: A dictionary containing the computed trajectories for both feet, with position arrays for each axis (x, y, z).
  
- **Purpose**: Processes sensor data for each foot, applies filtering, computes orientation, transforms data to the global frame, integrates to find position, and stores the resulting trajectories.

---

### `plot_trajectories(self, trajectories)`
Plots the computed trajectories for both the left and right feet.

- **Parameters:**
  - `trajectories`: A dictionary containing the position data for the left and right feet.
  
- **Purpose**: Visualizes the X and Y positions of both feet in a 2D plot, showing their respective movement trajectories.

---

Usage Example
-------------

```python
# Initialize the trajectory analyzer with data, sampling interval, and verbosity level
analyzer = TrajectoryAnalyzer(data=my_data, dt=0.01, verbosity=1)

# Compute trajectories for both left and right feet
trajectories = analyzer.compute_trajectories()

# Plot the computed trajectories
analyzer.plot_trajectories(trajectories)

Interpolator
==================

The `Interpolator` class is used to interpolate sensor data for the left and right groups (e.g., left and right pressure sensors). The class ensures that both groups have the same number of data points after interpolation.

Methods
-------

### `__init__(self, data_dict, verbosity=0)`
Initializes the `Interpolator` class with the given data dictionary.

- **Parameters:**
  - `data_dict`: A dictionary containing the data to be interpolated (e.g., accelerometer, pressure data).
  - `verbosity`: Defines the level of verbosity for print statements. (0: silent, 1: basic, 2: detailed).

- **Purpose**: Initializes the class with the provided data dictionary and verbosity level. Optionally prints initialization details based on verbosity.

---

### `interpolate_data(self)`
Interpolates the data in the group (left or right) with fewer data points. After interpolation, both groups will have the same number of data points.

- **Purpose**: 
  - Finds which group (left or right) has fewer data points.
  - Interpolates the data of the smaller group to match the number of data points in the larger group.
  - Works with both simple and nested data structures (data with sub-keys).
  
- **Verbosity:**
  - Level 1 or higher: Prints a message indicating the interpolation has started and completed.
  - Level 2 or higher: Prints detailed information about the interpolation process for each key and sub-key.

---

### `get_interpolated_data(self)`
Returns the interpolated data dictionary.

- **Returns**: 
  - The dictionary containing the interpolated data for both the left and right groups.

- **Purpose**: Provides access to the interpolated data after the `interpolate_data()` method has been executed.

---

Usage Example
-------------

```python
# Initialize the interpolator with a data dictionary and verbosity level
interpolator = Interpolator(data_dict=my_data_dict, verbosity=1)

# Interpolate the data
interpolator.interpolate_data()

# Retrieve the interpolated data
interpolated_data = interpolator.get_interpolated_data()

OrientationAnalyzer Class
==========================

The `OrientationAnalyzer` class processes and analyzes magnetometer data to compute heading (yaw angle), detect turns, and visualize the heading over time. It provides methods for cleaning and smoothing data, as well as detecting significant changes in orientation.

Methods
-------

### `__init__(self, mag_x, mag_y, mag_z, verbosity=0)`
Initializes the `OrientationAnalyzer` with magnetometer data.

- **Parameters:**
  - `mag_x`: Magnetometer data along the X-axis.
  - `mag_y`: Magnetometer data along the Y-axis.
  - `mag_z`: Magnetometer data along the Z-axis.
  - `verbosity`: Level of verbosity for print statements (0: silent, 1: basic, 2: detailed).

- **Purpose**: Initializes the class with magnetometer data and an optional verbosity level for output.

---

### `remove_outliers(self, data, threshold=3)`
Removes outliers from the provided data using the Z-score method.

- **Parameters:**
  - `data`: The magnetometer data (x, y, or z axis).
  - `threshold`: Z-score threshold for detecting outliers.

- **Returns**: Cleaned data with outliers removed.
  
- **Purpose**: Filters out data points that deviate significantly (as defined by the threshold) from the mean, improving data quality for analysis.

---

### `clean_data(self)`
Cleans the magnetometer data by removing outliers from the X, Y, and Z axes.

- **Purpose**: Ensures that outliers are removed from all magnetometer data axes (X, Y, Z) before further processing.

---

### `smooth_data(self, window_size=1000)`
Smooths the magnetometer data using a simple moving average.

- **Parameters:**
  - `window_size`: Size of the moving window (number of samples to average).

- **Purpose**: Smooths the X, Y, and Z axis data to reduce noise, making the data more suitable for further analysis (e.g., heading computation).

---

### `compute_heading(self)`
Computes the heading (yaw angle) from the smoothed magnetometer data.

- **Returns**: Heading angles in radians.
  
- **Purpose**: Calculates the heading by normalizing the magnetometer data and using the `arctan2` function to compute the orientation angle.

- **Raises**: 
  - `ValueError` if the magnetometer data has not been smoothed.

---

### `detect_turns(self, heading, threshold=np.radians(15))`
Detects turns based on changes in the heading.

- **Parameters:**
  - `heading`: Array of heading angles (in radians).
  - `threshold`: Minimum change in heading (in radians) to be considered a turn.

- **Returns**: Indices where significant turns are detected.
  
- **Purpose**: Identifies turns by detecting where the change in heading exceeds a predefined threshold, which represents a turn in the motion.

---

### `plot_heading(self, heading, turn_indices=None)`
Plots the heading over time, highlighting the detected turns if provided.

- **Parameters:**
  - `heading`: Array of heading angles (in radians).
  - `turn_indices`: Indices where turns are detected.

- **Purpose**: Visualizes the heading angles over time and optionally marks the detected turns on the plot.

---

Usage Example
-------------

```python
# Initialize the OrientationAnalyzer with magnetometer data and verbosity level
analyzer = OrientationAnalyzer(mag_x=my_mag_x, mag_y=my_mag_y, mag_z=my_mag_z, verbosity=1)

# Clean and smooth the data
analyzer.smooth_data(window_size=500)

# Compute the heading
heading = analyzer.compute_heading()

# Detect turns in the heading data
turns = analyzer.detect_turns(heading, threshold=np.radians(15))

# Plot the heading with detected turns
analyzer.plot_heading(heading, turn_indices=turns)

MyIMUSensor Class
=================

This module defines a custom IMU sensor class, `MyIMUSensor`, which inherits from `IMU_Base`. It is designed to retrieve and process IMU data from a file or a dictionary. The data typically includes accelerometer, gyroscope (angular velocity), and magnetometer data, and the class organizes this data into relevant attributes.

Class: `MyIMUSensor`
---------------------

The `MyIMUSensor` class extends the `IMU_Base` class to provide functionality for loading and storing IMU data.

### **Attributes**:
- `acc`: Numpy array containing accelerometer data (3D acceleration).
- `omega`: Numpy array containing gyroscope data (angular velocity).
- `mag`: Numpy array containing magnetometer data (optional).
- `rate`: Sampling rate of the IMU sensor, set to 50 Hz by default.
- `source`: The source from which the IMU data was loaded (file path or `None` if data is passed directly).
  
### **Methods**:

#### `get_data(self, in_file=None, in_data=None)`
Retrieves IMU data from either a file or a dictionary and sets the relevant attributes for the accelerometer, gyroscope, and magnetometer data. The method should be implemented according to the specific data format.

**Parameters**:
- `in_file` (str, optional): Path to a file (e.g., CSV, TXT) containing the IMU data. If provided, the method will load data from the file.
- `in_data` (dict, optional): A dictionary containing IMU data. Keys should include 'acc', 'omega', and optionally 'mag'. If provided, the method will load data directly from the dictionary.

**Raises**:
- `ValueError`: If neither `in_file` nor `in_data` is provided.

**Example Usage**:
```python
# Example of loading data from a file
sensor = MyIMUSensor()
sensor.get_data(in_file="imu_data.csv")

# Example of loading data from a dictionary
data = {
    'acc': np.array([[0.0, 0.0, 9.81], [0.0, 0.0, 9.81]]),  # example acceleration data
    'omega': np.array([[0.0, 0.0, 0.0], [0.1, 0.1, 0.1]]),  # example angular velocity data
    'mag': np.array([[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]])      # optional example magnetic field data
}
sensor.get_data(in_data=data)


IMUDataProcessor
========================

The `IMUDataProcessor` class processes IMU (Inertial Measurement Unit) data, including accelerometer, gyroscope, and magnetometer data, to compute and visualize the movement trajectories of both feet (left and right).

Methods
-------

### `__init__(self, interpolated_data, filter_type='analytical', verbosity=0)`
Initializes the `IMUDataProcessor` class.

- **Parameters:**
  - `interpolated_data`: A dictionary containing the IMU data, including accelerometer, gyroscope, and magnetometer data.
  - `filter_type`: The type of filter to use for processing the data (default is 'analytical').
  - `verbosity`: Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output) (default is 0).

- **Purpose**: Initializes the class with the provided IMU data, filter type, and verbosity level. Optionally prints initialization details based on verbosity.

---

### `extract_data(self)`
Extracts accelerometer, gyroscope, and magnetometer data for both the right and left foot sensors.

- **Purpose**: This method processes the raw IMU data into the required format and creates `MyIMUSensor` instances for both feet using the extracted data. Optionally prints the progress based on verbosity.

---

### `calculate_position(self)`
Calculates the position of both the right and left foot sensors.

- **Purpose**: Calls the `calc_position()` method of both the right and left foot sensors to compute their respective positions based on the sensor data.

---

### `print_sensor_data(self)`
Prints the sensor data for both the right and left foot, including acceleration, angular velocity, magnetic field, orientation (quaternion), position, and velocity.

- **Purpose**: Displays the sensor data for both feet, including acceleration, angular velocity, magnetic field, sampling rate, orientation (quaternion), position, and velocity.

---

### `plot_trajectory_3d(self)`
Plots the 3D position trajectory of both the right and left foot sensors.

- **Purpose**: Generates a 3D plot showing the position trajectories of both feet using their calculated positions. Each foot is represented by a distinct color in the plot.

---

### `plot_trajectory_2d(self)`
Plots the 2D position trajectory of both the right and left foot sensors.

- **Purpose**: Generates a 2D plot showing the position trajectories of both feet using their calculated positions. Each foot is represented by a distinct color in the plot.

---

Usage Example
-------------

```python
# Initialize the IMU data processor with interpolated data, filter type, and verbosity level
imu_processor = IMUDataProcessor(interpolated_data=my_data, filter_type='analytical', verbosity=1)

# Extract sensor data for both right and left foot
imu_processor.extract_data()

# Calculate position for both right and left foot
imu_processor.calculate_position()

# Print the sensor data for both feet
imu_processor.print_sensor_data()

# Plot the 3D trajectory of both feet
imu_processor.plot_trajectory_3d()

# Plot the 2D trajectory of both feet
imu_processor.plot_trajectory_2d()


DataPickle Class
================

The `DataPickle` class is a unified interface for loading and saving data, such as DataFrames or dictionaries, using pickle files. It provides methods to handle file operations with configurable verbosity levels for feedback and debugging.

Methods
-------

### __init__(self, verbosity=0, output_dir='data', filename='data.pkl')

Initializes the `DataPickle` class with verbosity level, default output directory, and filename.

Arguments:
- **verbosity** (`int`): Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output).
- **output_dir** (`str`): The default directory for saving pickle files. Default is `'data'`.
- **filename** (`str`): The default name for pickle files. Default is `'data.pkl'`.

### save_to_pickle(self, data, file_path=None, filename=None)

Saves the provided data (e.g., dictionary, DataFrame) to a pickle file.

Arguments:
- **data** (`any`): The data to save (e.g., dictionary, DataFrame).
- **file_path** (`str`, optional): The directory where the file should be saved. If not specified, defaults to `output_dir`.
- **filename** (`str`, optional): The name of the pickle file. If not specified, defaults to `filename` set during initialization.

### load_from_pickle(self, file_path=None, filename=None)

Loads data (e.g., dictionary, DataFrame) from a pickle file.

Arguments:
- **file_path** (`str`, optional): The directory where the pickle file is located. If not specified, defaults to `output_dir`.
- **filename** (`str`, optional): The name of the pickle file. If not specified, defaults to `filename` set during initialization.

Returns:
- **any**: The loaded data (e.g., DataFrame, dictionary) if successful, or `None` if loading failed.

Examples of Usage
-----------------

### Saving Data

```python
data = {'key1': [1, 2, 3], 'key2': [4, 5, 6]}

# Initialize the DataPickle instance
data_pickle = DataPickle(verbosity=1, output_dir='output_data', filename='example.pkl')

# Save the data
data_pickle.save_to_pickle(data)


Main Script for Gait and Trajectory Analysis
============================================

This script performs an end-to-end workflow to load data, process it, and analyze various aspects of gait, trajectory, and orientation. The workflow includes loading data from a pickle file, performing gait analysis, interpolating data, computing trajectories, and analyzing the orientation based on magnetometer data.

Classes
--------

### `VAction`
A custom `argparse` action to handle verbosity levels. It increments the verbosity level based on the number of `v` characters in the provided argument.

- **Attributes**:
  - `values`: The verbosity level set by the user, determined by the count of `v` characters in the argument.

- **Methods**:
  - `__call__(self, parser, args, values, option_string=None)`: Determines the verbosity level based on the input and sets it in the parsed arguments.

---

Functions
---------

### `main()`
The main function that orchestrates the workflow of loading, processing, and analyzing data.

- **Returns**:
  - `interpolated_data`: Dictionary containing the interpolated data after balancing the left and right groups.
  - `quaternions`: Dictionary containing the quaternions for both left and right sensors.

- **Process**:
  1. **Argument Parsing**: Handles command-line arguments for file path and filename, verbosity level, and filter type.
  2. **Data Loading**: Loads data from a pickle file using the `DataLoader` class.
  3. **Gait Analysis**: Performs preprocessing on the data using the `GaitAnalysis` class.
  4. **Data Interpolation**: Balances the left and right groups using the `Interpolator` class.
  5. **Trajectory Analysis**: Computes the trajectories based on the interpolated data using the `TrajectoryAnalyzer` class.
  6. **Orientation Analysis**: Analyzes the heading and detects turns using the `OrientationAnalyzer` class based on magnetometer data.
  7. **IMU Data Processing**: Processes the IMU sensor data using `IMUDataProcessor` and stores quaternions.
  8. **Data Saving**: Saves the quaternions to a pickle file using `DataSaver`.
  9. **Plotting**: Plots 3D and 2D trajectories using `IMUDataProcessor`.

---

Usage Example
-------------
```bash
runfile('C:/Users/marbo/Documents/mainIMU.py', wdir='C:/Users/marbo/Documents', args='-fp output_data/cine_MGM-202406-79.pkl -v 2 -flt kalman')
