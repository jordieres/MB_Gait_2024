# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:06:27 2024

@author: marbo
"""

import argparse
from config import Config
from data_fetcher import DataFetcher
from data_processor import DataProcessor
from map_generator import MapGenerator



# Custom verbose handler for argparse
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
    Main function to fetch data, process it, and generate movement maps. This function parses
    command-line arguments, fetches data from an API, processes the data, and generates a movement
    map using Plotly. It also handles verbosity levels.
    
    The following steps are performed:
    1. Command-line arguments are parsed.
    2. Data is fetched using the DataFetcher class.
    3. The fetched data is processed using the DataProcessor class.
    4. A map visualizing the movements is generated using MapGenerator.
    5. Output information is printed using the Output class.
    """
    

    # Load config
    config = Config()
    
    # Parse command-line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--from", type=str, required=True, help="Date for starting the analysis. Format YYYY-MM-DD.")
    ap.add_argument("-u", "--until", type=str, required=True, help="Date for ending the analysis. Format YYYY-MM-DD.")
    ap.add_argument("-v", "--verbose", nargs='?', action=VAction, dest='verbose', help="Option for methods verbosity.")
    ap.add_argument("-q", "--qtok", type=str, required=True, help="Enter the qtok value (e.g., 'MGM-202406-79').")
    ap.add_argument("-p", "--pie", type=str, choices=["Right", "Left"], required=True, help="Enter the foot ('Right' or 'Left').")
    ap.add_argument("-o", "--output", type=int, choices=range(0, 3), default=2, help="Choose a number from 0 to 2 (default is 2)")
    ap.add_argument("-t", "--time-spacing", type=int, default=120, help="Time spacing in seconds for segmenting movements (default is 120).")
    args = vars(ap.parse_args())
    
    verbosity_level = int(args['verbose']) if args['verbose'] else 0
    
    if verbosity_level > 0:
        print(f"Starting data processing with verbosity level {verbosity_level}")
        
    if verbosity_level > 1:
        print(f"Loaded configuration: {config}\n")
        
        
    # Create DataFetcher and fetch the data
    data_fetcher = DataFetcher(
        qtok=args['qtok'],
        pie=args['pie'],
        start_date=f"{args['from']}T00:00:00Z",
        end_date=f"{args['until']}T23:59:59Z",
        token=config.token,
        org=config.org,
        url=config.url,
        verbose = verbosity_level
    )
   
    raw_data = data_fetcher.fetch_data()
    
    # Process the data with the provided time_spacing argument
    data_processor = DataProcessor(raw_data, verbosity_level)
    
    movements_df = data_processor.process_data(time_spacing=args['time_spacing'])
    
    
    # Generate maps
    map_generator = MapGenerator(movements_df, verbosity_level)
    
    map_generator.generate_plotly_map(args['qtok'], args['from'], args['until'])
   
    # Save movements_df to a pickle file
    data_fetcher.save_to_pickle(movements_df, output_dir='output_data', filename='movements.pkl')

   
   
    
    if verbosity_level > 0:
        print("\nProgram execution completed.")

if __name__ == '__main__':
    main()
