import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter1d

class OrientationAnalyzer:
    def __init__(self, mag_x, mag_y, mag_z, verbosity=0):
        """
        Initialize with magnetometer data.
        :param mag_x: Magnetometer X-axis data.
        :param mag_y: Magnetometer Y-axis data.
        :param mag_z: Magnetometer Z-axis data.
        :param verbosity: Verbosity level (0: silent, 1: basic, 2: detailed).
        """
        self.mag_x = mag_x
        self.mag_y = mag_y
        self.mag_z = mag_z
        self.mag_x_smooth = None  # Initialize smoothed data attributes
        self.mag_y_smooth = None
        self.mag_z_smooth = None
        self.verbosity = verbosity

        if self.verbosity >= 1:
            print(f"OrientationAnalyzer initialized with verbosity level {self.verbosity}.")

    def remove_outliers(self, data, threshold=3):
        """
        Remove outliers from the data using Z-score method.
        :param data: Input data array (mag_x, mag_y, mag_z).
        :param threshold: Z-score threshold for identifying outliers.
        :return: Cleaned data with outliers removed.
        """
        if self.verbosity >= 2:
            print("Removing outliers from data using Z-score method.")

        mean = np.mean(data)
        std_dev = np.std(data)
        z_scores = (data - mean) / std_dev
        # Filter out data points with Z-scores beyond the threshold
        cleaned_data = data[np.abs(z_scores) < threshold]

        if self.verbosity >= 2:
            print(f"Outliers removed. Data length reduced from {len(data)} to {len(cleaned_data)}.")

        return cleaned_data

    def clean_data(self):
        """
        Clean magnetometer data by removing outliers from the raw data (mag_x, mag_y, mag_z).
        """
        if self.verbosity >= 1:
            print("Cleaning magnetometer data by removing outliers.")

        self.mag_x = self.remove_outliers(self.mag_x)
        self.mag_y = self.remove_outliers(self.mag_y)
        self.mag_z = self.remove_outliers(self.mag_z)

        if self.verbosity >= 1:
            print("Magnetometer data cleaned.")

    def smooth_data(self, window_size=1000):
        """
        Smooth the magnetometer data using a simple moving average.
        :param window_size: The size of the moving window (number of samples to average).
        :return: Smoothed x, y, z data.
        """
        if self.verbosity >= 1:
            print(f"Smoothing data with window size {window_size}.")

        # Ensure outliers are removed before smoothing
        #self.clean_data()

        # Ensure the lengths of the data are the same after removing outliers
        min_length = min(len(self.mag_x), len(self.mag_y), len(self.mag_z))
        self.mag_x = self.mag_x[:min_length]
        self.mag_y = self.mag_y[:min_length]
        self.mag_z = self.mag_z[:min_length]

        # Smooth the data using moving average
        self.mag_x_smooth = np.convolve(self.mag_x, np.ones(window_size)/window_size, mode='valid')
        self.mag_y_smooth = np.convolve(self.mag_y, np.ones(window_size)/window_size, mode='valid')
        self.mag_z_smooth = np.convolve(self.mag_z, np.ones(window_size)/window_size, mode='valid')

        if self.verbosity >= 1:
            print("Data smoothing complete.")

    def compute_heading(self):
        """
        Compute the heading (yaw angle) from the magnetometer data.
        :return: Heading angles in radians.
        """
        if self.verbosity >= 1:
            print("Computing heading from smoothed magnetometer data.")

        # Ensure that smoothing has been applied before computing the heading
        if self.mag_x_smooth is None or self.mag_y_smooth is None or self.mag_z_smooth is None:
            raise ValueError("Magnetometer data must be smoothed before computing heading.")

        # Normalize the magnetometer readings
        mag_norm = np.sqrt(self.mag_x_smooth**2 + self.mag_y_smooth**2)
        mag_x_normalized = self.mag_x_smooth / mag_norm
        mag_y_normalized = self.mag_y_smooth / mag_norm

        # Compute heading using arctan2
        heading = np.arctan2(mag_y_normalized, mag_x_normalized)

        if self.verbosity >= 2:
            print(f"Heading computed. Heading range: {np.degrees(heading).min()}° to {np.degrees(heading).max()}°.")

        return heading

    def detect_turns(self, heading, threshold=np.radians(15)):
        """
        Detect turns based on changes in heading.
        :param heading: Array of heading angles.
        :param threshold: Minimum change in heading (in radians) to count as a turn.
        :return: Indices where turns are detected.
        """
        if self.verbosity >= 1:
            print(f"Detecting turns with a threshold of {np.degrees(threshold)}°.")

        heading_diff = np.diff(heading)
        turn_indices = np.where(np.abs(heading_diff) > threshold)[0]

        if self.verbosity >= 2:
            print(f"{len(turn_indices)} turns detected.")

        return turn_indices

    def plot_heading(self, heading, turn_indices=None):
        """
        Plot the heading over time, highlighting turns if provided, using Plotly.

        :param heading: Heading angles in radians.
        :param turn_indices: Indices where turns occur.
        """
        if self.verbosity >= 1:
            print("Plotting heading with detected turns using Plotly.")

        time = np.arange(len(heading))  # Assume constant sampling interval
        heading_degrees = np.degrees(heading)

        # Create the base line plot for heading
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=time,
            y=heading_degrees,
            mode='lines',
            name='Heading (degrees)',
            line=dict(color='blue')
        ))

        # Add scatter plot for turn indices if provided
        if turn_indices is not None:
            fig.add_trace(go.Scatter(
                x=turn_indices,
                y=heading_degrees[turn_indices],
                mode='markers',
                name='Detected Turns',
                marker=dict(color='red', size=8, symbol='circle')
            ))

        # Update layout for the plot
        fig.update_layout(
            title="Heading and Turns",
            xaxis=dict(title="Time"),
            yaxis=dict(title="Heading (degrees)"),
            legend=dict(title="Legend"),
            template="plotly_white"
        )

        if self.verbosity >= 1:
            print("Displaying interactive plot.")

        fig.show()
