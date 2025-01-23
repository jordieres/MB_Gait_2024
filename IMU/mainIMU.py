import argparse

from gait_analysis import GaitAnalysis
from imu_sensor_data_processing import IMUDataProcessor
from pathlib import Path
from DataPickle import DataPickle
import plotly.io as pio
import pandas as pd

from TrajectoryAnalyzerAHRS import TrajectoryAnalyzerAHRS

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
    Main function to manage the workflow of loading data, performing gait analysis, 
    processing IMU data, computing trajectories, and saving results.

    This function performs the following steps:
    1. Parses command-line arguments for input file path, verbosity level, and filter type.
    2. Loads data from a pickle file using the `DataPickle` class.
    3. Performs gait analysis and processes IMU data based on the selected filter type.
    4. Computes and visualizes IMU and GPS trajectories.
    5. Saves processed data and results to pickle and Excel files.

    Command-Line Arguments:
    -----------------------
    -fp, --file_path : str
        The full path to the pickle file containing raw data.
    -v, --verbosity : int
        Verbosity level for output (0 = no output, 1 = minimal output, 2 = detailed output). Default is 0.
    -flt, --filter_type : str
        Filter type for IMU orientation calculation. Options:
        - 'analytical', 'kalman', 'madgwick', 'mahony', 'ahrs', or 'None' (no orientation calculation).
        Default is 'ahrs'.

    Returns:
    -------
    raw_data : dict
        Raw data loaded from the pickle file, containing left and right sensor data.
    gait_evaluation : dict
        Dictionary containing:
        - `gait_dict`: Results of the gait analysis.
        - `IMU_dict`: Results of IMU trajectory analysis.
    """
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Load a DataFrame from a pickle file.")
    parser.add_argument("-fp", "--file_path", type=str, required=True, help="The full path to the pickle file (including the filename).")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0, help="Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output)")
    parser.add_argument(
    "-flt", "--filter_type",
    type=str,
    choices = ['analytical', 'kalman', 'madgwick', 'mahony', 'ahrs','None'],
    default = 'ahrs',
    help = "Determines how the orientation gets calculated: "
         "'analytical' (default), 'kalman', 'madgwick', 'mahony', 'ahrs', or 'None' for no calculation."
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
    gait_analysis.plot_data(raw_data)
    

    
    gait_dict=gait_analysis.gait_analysis()
  
    
    
    if args.filter_type in ['analytical', 'kalman', 'madgwick', 'mahony']:
        
        # Create an instance of IMUDataProcessor
        processor = IMUDataProcessor(raw_data, filter_type=args.filter_type, verbosity=args.verbosity)
        
        # Extract and process data
        processor.extract_data()
        
        
        # Store quaternions
        processor.right_sensor.set_qtype(args.filter_type)
        processor.left_sensor.set_qtype(args.filter_type)
        
        quaternions={}
        #right_quaternions = processor.right_sensor.quat
        #left_quaternions = processor.left_sensor.quat
        #quaternions = {'right': right_quaternions, 'left': left_quaternions}
        
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

    else:
        


        
        # Assuming `data` is a pandas DataFrame with IMU and GPS columns
        analyzer = TrajectoryAnalyzerAHRS(raw_data['right'], sample_period=0.02, verbosity=args.verbosity)
        analyzer.calculate_imu_trajectory()
        IMU_dict=analyzer.plot_trajectory_with_map(output_html_file="trajectory_map.html")
        
       
    
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

    gait_evaluation = {}
    gait_evaluation['gait_dict']=gait_dict
    if args.filter_type in ['ahrs']:
        gait_evaluation['IMU_dict']=IMU_dict
        
    # Call the save_to_pickle method
    data_handler.save_to_pickle(data=gait_evaluation, file_path = 'output_data', filename = 'gait_evaluation.pkl')
        

    
   
    return gait_evaluation

if __name__ == "__main__":
    
    gait_evaluation = main()
    print(gait_evaluation['gait_dict'].keys())
    print(gait_evaluation['IMU_dict'].keys())
