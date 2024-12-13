

# Movement Data Analyzer

## Introduction

The Movement Data Analyzer is a Python program designed to fetch, process, and visualize movement data based on specified input parameters. The program interacts with an external API to retrieve data, processes it to calculate movement-related statistics (such as speed, distance, and duration), and generates interactive visualizations using Plotly.

The program is ideal for anyone who needs to analyze movement data over a specific date range and location, with support for customizable verbosity levels and detailed visual feedback.

## Setup & Installation

### Configuration

Before running the program, ensure that the configuration file (`config.toml`) is correctly set up. This file contains the necessary configuration for API interaction and other settings.

## Usage

### Command-Line Arguments

The program accepts the following command-line arguments:

- `-f` or `--from`: **Required**. Start date/time in the format `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`.
- `-u` or `--until`: **Required**. End date/time in the format `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`.
- `-v` or `--verbose`: **Optional**. Set the verbosity level for method output. The higher the value, the more detailed the output.
- `-q` or `--qtok`: **Required**. Unique identifier for the dataset (e.g., `'MGM-202406-79'`).
- `-p` or `--pie`: **Required**. Indicates which foot the data pertains to. Must be either `Right` or `Left`.
- `-o` or `--output`: **Optional**. Defines the output level (0, 1, or 2). Default is 2.
- `-t` or `--time-spacing`: **Optional**. Defines the time spacing in seconds for segmenting movements. Default is 120 seconds.

### Example Usage

#### From the Command Line

To run the program from the command line:

```bash
python mainExtGPS.py -f 2024-06-16 -u 2024-06-17 -v 2 -q MGM-202406-79 -p Right -o 2 -t 120
```

#### From Spyder IDE

If you're using Spyder IDE, use the following code to run the script:

```python
runfile('path/mainExtGPS.py', wdir='C:/Users/marbo/Documents', args='-f 2024-06-16 -u 2024-06-17 -v 2 -q MGM-202406-79 -p Right')
```

### Main Script

The main function (`mainExtGPS.py`) processes the following steps:

1. **Argument Parsing**: The script begins by parsing command-line arguments using `argparse`.
2. **Data Fetching**: It fetches data from the specified API based on the provided parameters.
3. **Data Processing**: The raw data is processed to calculate relevant metrics such as distance, speed, and duration.
4. **Map Visualization**: The program generates an interactive map using Plotly, with movement routes and tooltips showing relevant data.

### Verbosity Levels

The `verbose` argument controls the output verbosity of the methods:

- **Level 0**: Minimal output (errors and essential information only).
- **Level 1**: Standard output, including important steps and results.
- **Level 2**: Detailed output, including all processing steps and intermediate results.

### Output Levels

The `output` argument controls the level of output detail:

- **0**: Basic output.
- **1**: Standard output with essential details.
- **2**: Full output with all data points and calculations (default).

### Time Spacing

The `time-spacing` argument controls how the data is segmented into movements. By default, it is set to 120 seconds, but you can adjust it as needed.

## Comments

This program provides a comprehensive set of features for analyzing movement data. The interactive maps generated using Plotly allow for detailed visualizations of movement trajectories, helping users better understand patterns over time and location. The ability to control verbosity and output levels ensures flexibility for different use cases, whether you need high-level summaries or detailed logs.
```

