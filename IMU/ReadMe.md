# IMU Data Processing and Analysis

## Introduction

The IMU Data Processing and Analysis program is a Python-based tool designed to load and process motion data, perform gait analysis, and compute orientation and trajectory from inertial measurement unit (IMU) sensors. The program interacts with pickle files containing sensor data and applies a series of analysis steps, including data interpolation, trajectory computation, and orientation analysis using magnetometer data.

## Setup & Installation

### Configuration

Before running the program, ensure that the configuration file (`config.toml`) is correctly set up. This file contains the necessary configuration for API interaction and other settings.

## Usage

### Command-Line Arguments

The program accepts the following command-line arguments:

- `-p` or `--path`: **Required**. The directory where the pickle file is located.
- `-f` or `--filename`: **Required**. The name of the pickle file.
- `-v` or `--verbosity`: **Optional**. Verbosity level for output:
    - **0**: No output.
    - **1**: Minimal output.
    - **2**: Detailed output.
- `-flt` or `--filter_type`: **Optional**. Specifies the filter type for orientation calculation. Choices are:
    - `analytical` (default)
    - `kalman`
    - `madgwick`
    - `mahony`
    - `None`

### Example Usage

#### From the Command Line

To run the program from the command line:

```bash
python main.py -p /path/to/data -f sensor_data.pkl -v 2 -flt kalman
```

#### From Spyder IDE

If you're using Spyder IDE, use the following code to run the script:

```python
runfile('path/main.py', wdir='C:/Users/marbo/Documents', args='-p /path/to/data -f sensor_data.pkl -v 2 -flt kalman')
```

### Main Script

The main function (`main.py`) processes the following steps:

1. **Argument Parsing**: The script begins by parsing command-line arguments using `argparse`.
2. **Data Loading**: It loads sensor data from a pickle file using the `DataLoader`.
3. **Data Preprocessing**: The data undergoes preprocessing through `GaitAnalysis` to clean and prepare it for further analysis.
4. **Data Interpolation**: The `Interpolator` balances the data for left and right sensor groups.
5. **Trajectory Analysis**: The program computes and optionally visualizes the movement trajectories using `TrajectoryAnalyzer`.
6. **Orientation Analysis**: Magnetometer data is processed to compute the heading and detect turns using `OrientationAnalyzer`.
7. **IMU Data Processing**: The IMU data is processed using `IMUDataProcessor`, where positions and quaternions are calculated.
8. **Data Saving**: The processed data, including quaternions, is saved to a pickle file using `DataSaver`.

### Verbosity Levels

The `verbosity` argument controls the output verbosity of the methods:

- **Level 0**: No output.
- **Level 1**: Minimal output, only essential information.
- **Level 2**: Detailed output, including intermediate steps and data.

### Filter Type

The `filter_type` argument controls how the orientation is calculated:

- **analytical** (default)
- **kalman**
- **madgwick**
- **mahony**
- **None**: No calculation.

### Output

The program will output the following data:

- **Interpolated Data**: The data after balancing the left and right sensor groups.
- **Quaternions**: The computed orientation data, saved in a pickle file.

### Comments

This program provides a comprehensive set of features for analyzing IMU data, including the ability to calculate and visualize movement trajectories, analyze orientation using magnetometer data, and process sensor data with advanced filtering techniques. It is highly customizable with different verbosity levels and filter options, allowing for flexible usage across various use cases.

```
