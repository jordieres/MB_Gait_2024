import argparse
import numpy as np
from gait_analysis import GaitAnalysis
from Interpolator import Interpolator
from TrajectoryAnalyzer import TrajectoryAnalyzer
from OrientationAnalyzer import OrientationAnalyzer
import matplotlib.pyplot as plt
from MyIMUSensor import MyIMUSensor
from imu_sensor_data_processing import IMUDataProcessor
from pathlib import Path
import os
from DataPickle import DataPickle
import plotly.io as pio
import pandas as pd


class VAction(argparse.Action):
    """
    Custom argparse action to handle verbosity levels. This class increments the verbosity level
    based on the number of 'v' characters in the provided argument.
    """
    def __init__(self, option_strings, dest, nargs=None, const=None,
                 default=None, type=None, choices=None, required=False,
                 help=None, metavar=None):
        """
        Initialize the custom action for verbosity handling.

        Parameters:
        ----------
        option_strings : list
            List of option strings (e.g., ["-v", "--verbose"]).
        dest : str
            Destination variable for storing the verbosity level.
        nargs : None, optional
            Number of arguments (not used here).
        const : None, optional
            Constant value (not used here).
        default : None, optional
            Default value for the verbosity level.
        type : None, optional
            Type of the input value (not used here).
        choices : None, optional
            Choices available for this argument (not used here).
        required : bool, optional
            Whether this argument is required.
        help : str, optional
            Help text for this argument.
        metavar : str, optional
            Argument name in help text.
        """
        super(VAction, self).__init__(option_strings, dest, nargs, const,
                                      default, type, choices, required,
                                      help, metavar)
        self.values = 0

    def __call__(self, parser, args, values, option_string=None):
        """
        Handles the call to set the verbosity level based on the argument provided.

        Parameters:
        ----------
        parser : ArgumentParser
            The argparse parser instance.
        args : Namespace
            Parsed arguments namespace.
        values : str
            Verbosity string (e.g., "vv" for verbosity level 2).
        option_string : str, optional
            The option string that was used (e.g., "-v").
        """
        if values is None:
            self.values += 1
        else:
            try:
                self.values = int(values)
            except ValueError:
                self.values = values.count('v') + 1
        setattr(args, self.dest, self.values)

def main():
    """
    Main function to handle the overall workflow of loading data, performing gait analysis, 
    interpolating data, computing trajectories, and analyzing orientation.

    The function parses command-line arguments, loads data from a pickle file, performs preprocessing, 
    interpolates the data to balance groups, computes trajectories, and analyzes the orientation using 
    magnetometer data.

    Returns:
    -------
    data_dict : dict
        Dictionary containing the processed data after gait analysis and interpolation.
    interpolated_data : dict
        Dictionary containing the interpolated data after balancing the left and right groups.
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Load a DataFrame from a pickle file.")
    parser.add_argument("-fp", "--file_path", type=str, required=True, help="The full path to the pickle file (including the filename).")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0, help="Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output)")
    parser.add_argument(
    "-flt", "--filter_type",
    type=str,
    choices=['analytical', 'kalman', 'madgwick', 'mahony', 'None'],
    default='analytical',
    help="Determines how the orientation gets calculated: "
         "'analytical' (default), 'kalman', 'madgwick', 'mahony', or 'None' for no calculation."
)
    # Parse arguments
    args = parser.parse_args()
    
    # Extract path and filename using pathlib
    file_path = Path(args.file_path).resolve()
    directory = file_path.parent
    filename = file_path.name

    if args.verbosity > 0:
        print(f"Resolved file path: {file_path}")
        print(f"Directory: {directory}")
        print(f"Filename: {filename}")
        
    # Initialize DataPickle with verbosity and output directory
    data_handler = DataPickle(output_dir=str(directory), verbosity=args.verbosity)

    # Load DataFrame from pickle
    raw_data = data_handler.load_from_pickle(filename=filename)
    print(len(raw_data['left']['_time']))
    print(len(raw_data['right']['_time']))
    print(raw_data['right']['lat'].unique())
    print(raw_data['right']['lng'].unique())
    if args.verbosity > 0:
        print("DataFrame successfully loaded from pickle.")
        
        # Print time range if 'time' column exists
        if '_time' in raw_data['left'].keys():
            start_time = raw_data['left']['_time'].iloc[0].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Keep two decimal places
            end_time = raw_data['left']['_time'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]    # Keep two decimal places
            print(f"Time range: {start_time} to {end_time}")
    
    if raw_data is not None:
        if args.verbosity > 0:
            print("Data loaded successfully for further processing.")
    
    # Run gait analysis
    # Instantiate GaitAnalysis with data and verbosity level from arguments
    gait_analysis = GaitAnalysis(raw_data, verbosity=args.verbosity)

    
    pio.renderers.default = 'browser'
    #gait_analysis.plot_data(raw_data)
    # Initialize Interpolator with data_dict and verbosity
    #interpolator = Interpolator(data_dict, verbosity=args.verbosity)
    
    # Interpolate data to balance the "left" and "right" groups
    #interpolator.interpolate_data()

    # Get the interpolated data
    #interpolated_data = interpolator.get_interpolated_data()
    
    # Run trajectory analysis
    #analyzer = TrajectoryAnalyzer(raw_data, dt=0.01, verbosity=args.verbosity)
    #trajectories = analyzer.compute_trajectories()
    #analyzer.plot_trajectories(trajectories)
    
    # Extract magnetometer data
    mag_x = raw_data['right']['Mx'].to_numpy()
    mag_y = raw_data['right']['My'].to_numpy()
    mag_z = raw_data['right']['Mz'].to_numpy()
    
    # Initialize the orientation analyzer with the magnetometer data
    orientation_analyzer = OrientationAnalyzer(mag_x, mag_y, mag_z, verbosity=args.verbosity)
    
    # Smooth the magnetometer data
    orientation_analyzer.smooth_data(window_size=5)  # You can adjust the window size
    
    # Compute heading from the magnetometer data
    heading = orientation_analyzer.compute_heading()
    
    # Detect turns in the heading
    turn_indices = orientation_analyzer.detect_turns(heading)
    
    # Plot heading and detected turns
    orientation_analyzer.plot_heading(heading, turn_indices)
    
    
    # Create an instance of IMUDataProcessor
    processor = IMUDataProcessor(raw_data, filter_type=args.filter_type, verbosity=args.verbosity)
    
    # Extract and process data
    processor.extract_data()
    
    
    # Store quaternions
    processor.right_sensor.set_qtype(args.filter_type)
    processor.left_sensor.set_qtype(args.filter_type)
    

    right_quaternions = processor.right_sensor.quat
    left_quaternions = processor.left_sensor.quat
    quaternions = {'right': right_quaternions, 'left': left_quaternions}
    
    processor.calculate_position()
    
    
    # Save quaternions using DataSaver
    input_path = Path(args.file_path)  # Updated from args.path and args.filename
    base_name = input_path.stem  # Filename without the extension
    directory = input_path.parent  # Parent directory of the file
    output_filename = f"{base_name}_{args.filter_type}_quaternions.pkl"
    data_handler.save_to_pickle(data=quaternions, filename=output_filename)
    
    
    # Print sensor data
    processor.print_sensor_data()
    
    # Plot 3D and 2D trajectories
    processor.plot_trajectory_3d()
    processor.plot_trajectory_2d()

    with pd.ExcelWriter('acceleration_data_cleaned.xlsx') as writer:
        # Convert data to pandas DataFrame for the right sensor
        df_right = pd.DataFrame(raw_data['right'], columns=['Ax','Ay', 'Az', 'Gx', 'Gy', 'Gz', 'Mx', 'My', 'Mz', '_time'])
        # Convert the _time column to string to preserve the full datetime with timezones
        df_right['_time'] = df_right['_time'].astype(str)
        df_right.to_excel(writer, sheet_name='Right', index=False)
        
        # Convert data to pandas DataFrame for the left sensor
        df_left = pd.DataFrame(raw_data['left'], columns=['Ax','Ay', 'Az', 'Gx', 'Gy', 'Gz', 'Mx', 'My', 'Mz', '_time'])
        # Convert the _time column to string to preserve the full datetime with timezones
        df_left['_time'] = df_left['_time'].astype(str)
        df_left.to_excel(writer, sheet_name='Left', index=False)
        
        # Convert data to pandas DataFrame for the coordinates
        df_coordinates = pd.DataFrame(raw_data['left'], columns=['lat', 'lng', '_time'])
        # Convert the _time column to string to preserve the full datetime with timezones
        df_coordinates['_time'] = df_coordinates['_time'].astype(str)
        df_coordinates.to_excel(writer, sheet_name='coordinates', index=False)


        

    
   
    return raw_data

if __name__ == "__main__":
    
    raw_data = main()


