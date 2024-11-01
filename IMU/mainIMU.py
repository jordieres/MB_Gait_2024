import argparse
from load_pickle import DataLoader
from gait_analysis import GaitAnalysis


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
    
    
    
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Load a DataFrame from a pickle file.")
    parser.add_argument("-p", "--path", type=str, required=True, help="The directory where the pickle file is located.")
    parser.add_argument("-f", "--filename", type=str, required=True, help="The name of the pickle file.")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0, help="Verbosity level (0 = no output, 1 = minimal output, 2 = detailed output)")

    # Parse arguments
    args = parser.parse_args()

    # Initialize DataLoader with verbosity
    loader = DataLoader(verbosity=args.verbosity)
    
    # Load DataFrame from pickle
    raw_data = loader.load_from_pickle(file_path=args.path, filename=args.filename)
    if args.verbosity > 0:
        print("DataFrame successfully loaded from pickle")
                
                # Print time range if 'time' column exists
        if '_time' in raw_data.columns:
            start_time = raw_data['_time'].iloc[0].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Keep two decimal places
            end_time = raw_data['_time'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]    # Keep two decimal places
            print(f"Time range: {start_time} to {end_time}")
    
    if raw_data is not None:
        if args.verbosity > 0:
            print("Data loaded successfully for further processing.")
    
    
    # Run gait analysis
    # Instantiate GaitAnalysis with data and verbosity level from arguments
    gait_analysis = GaitAnalysis(raw_data, verbosity=args.verbosity)

    
    data_dict = gait_analysis.preprocess_data()
    gait_analysis.plot_data(data_dict)
    
    
    
    return data_dict













if __name__ == "__main__":
    data_dict=main()