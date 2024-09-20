import pandas as pd
import numpy as np

class OMLADEWMAStreaming:
    def __init__(self, threshold=3, alpha=0.3):
        """
        Streaming anomaly detection using EWMA for mean and standard deviation.
        
        Parameters:
        threshold (float): Z-score threshold to classify anomalies.
        alpha (float): Smoothing factor for EWMA. A higher value gives more weight to recent observations.
        """
        self.threshold = threshold
        self.alpha = alpha
        self.ewma_mean = None  # EWMA for mean
        self.ewma_var = None   # EWMA for variance
        self.std = None        # EWMA for standard deviation
        self.anomalies = []    # To store anomaly detection results

    def update_ewma(self, new_value):
        """
        Update the EWMA mean and variance with a new value.
        
        Parameters:
        new_value (float): The new value from the time series.
        """
        if self.ewma_mean is None:
            # Initialize EWMA mean and variance with the first value
            self.ewma_mean = new_value
            self.ewma_var = 0
            self.std = 0
        else:
            # Update EWMA mean
            self.ewma_mean = self.alpha * new_value + (1 - self.alpha) * self.ewma_mean

            # Update EWMA variance (mean square error)
            self.ewma_var = self.alpha * (new_value - self.ewma_mean)**2 + (1 - self.alpha) * self.ewma_var

            # Calculate EWMA standard deviation
            self.std = np.sqrt(self.ewma_var)

    def update(self, new_value):
        """
        Detect whether a new value is an anomaly based on the EWMA Z-score.
        
        Parameters:
        new_value (float): The new value from the time series.

        Returns:
        int: 1 if the value is an anomaly, 0 otherwise.
        """
        if self.std is None or self.std == 0:
            # Not enough data to calculate standard deviation, can't detect anomalies
            self.update_ewma(new_value)
            self.anomalies.append(0)
            return 0

        # Calculate Z-score based on EWMA mean and standard deviation
        z_score = (new_value - self.ewma_mean) / self.std
        
        # Check if the Z-score exceeds the threshold
        if abs(z_score) > self.threshold:
            anomaly = 1
        else:
            anomaly = 0

        # Update EWMA stats after checking for an anomaly
        self.update_ewma(new_value)

        # Append result to anomaly list
        self.anomalies.append(anomaly)
        
        return anomaly
    
class StreamingHampelFilter:
    def __init__(self, window_size=7, n_sigmas=3):
        """
        Streaming Hampel Filter for anomaly detection.
        
        Parameters:
        window_size (int): The size of the sliding window (number of points to include on each side).
        n_sigmas (int): The number of median absolute deviations to use for the threshold.
        """
        self.window_size = window_size
        self.n_sigmas = n_sigmas
        self.window = []  # Sliding window to hold the recent data points

    def update(self, new_value):
        """
        Update the Hampel filter with a new value and detect if it's an anomaly.
        
        Parameters:
        new_value (float): New value from the data stream.
        
        Returns:
        int: 1 if the value is an anomaly, 0 otherwise.
        """
        # Append the new value to the sliding window
        self.window.append(new_value)

        # Ensure the window size is maintained
        if len(self.window) > 2 * self.window_size + 1:
            self.window.pop(0)

        # If the window is not full yet, return 0 (no anomaly)
        if len(self.window) < 2 * self.window_size + 1:
            return 0

        # Calculate the median and MAD (Median Absolute Deviation) of the window
        median = np.median(self.window)
        mad = np.median(np.abs(self.window - median))

        # Define the threshold based on the MAD
        threshold = self.n_sigmas * mad

        # Check if the current value is an anomaly
        if np.abs(new_value - median) > threshold:
            return 1  # Anomaly detected
        else:
            return 0  # No anomaly detected

class ADWIN:
    def __init__(self, delta=0.001):
        """
        ADWIN algorithm for adaptive windowing and change detection in data streams.

        Parameters:
        delta (float): Confidence level. Lower values make the algorithm more sensitive to changes.
        """
        self.delta = delta
        self.window = []
        self.width = 0  # Size of the window
        self.total = 0  # Sum of the elements in the window
        self.total_squared = 0  # Sum of squares of the elements in the window

    def _variance(self, mean):
        """
        Calculate variance of the window.
        
        Parameters:
        mean (float): The mean of the window.

        Returns:
        float: Variance of the window.
        """
        if self.width == 0:
            return 0
        return (self.total_squared / self.width) - mean**2

    def _cut_point(self, mean, mean_left, var_left, mean_right, var_right, n_left, n_right):
        """
        Compute whether there is a significant difference between the two sub-windows.

        Parameters:
        mean (float): Mean of the entire window.
        mean_left (float): Mean of the left sub-window.
        mean_right (float): Mean of the right sub-window.
        var_left (float): Variance of the left sub-window.
        var_right (float): Variance of the right sub-window.
        n_left (int): Number of points in the left sub-window.
        n_right (int): Number of points in the right sub-window.

        Returns:
        bool: True if change is detected, False otherwise.
        """
        diff = abs(mean_left - mean_right)
        epsilon = np.sqrt(
            (1 / (2 * n_left)) * var_left +
            (1 / (2 * n_right)) * var_right
        ) + np.sqrt(self.delta / (2 * n_left)) + np.sqrt(self.delta / (2 * n_right))

        return diff > epsilon

    def update(self, value):
        """
        Update the window with a new value and check for change points.

        Parameters:
        value (float): New value from the data stream.

        Returns:
        bool: True if a change is detected, False otherwise.
        """
        # Add new value to the window
        self.window.append(value)
        self.width += 1
        self.total += value
        self.total_squared += value ** 2

        mean = self.total / self.width
        change_detected = False

        for i in range(1, self.width):
            left_window = self.window[:i]
            right_window = self.window[i:]

            # Calculate statistics for the left and right sub-windows
            n_left, n_right = len(left_window), len(right_window)
            mean_left = np.mean(left_window)
            mean_right = np.mean(right_window)
            var_left = np.var(left_window)
            var_right = np.var(right_window)

            # Check if a change occurred
            if self._cut_point(mean, mean_left, var_left, mean_right, var_right, n_left, n_right):
                # Change detected, shrink the window
                self.window = self.window[i:]
                self.width = len(self.window)
                self.total = np.sum(self.window)
                self.total_squared = np.sum(np.square(self.window))
                change_detected = True
                break

        return change_detected

class SlidingWindowDensityEstimation:
    def __init__(self, window_size=50, bandwidth=1.0, density_threshold=0.01):
        """
        Sliding Window Density Estimation for anomaly detection.
        
        Parameters:
        window_size (int): Size of the sliding window to hold recent data points.
        bandwidth (float): Bandwidth parameter for the Gaussian kernel.
        density_threshold (float): Probability density threshold below which the point is considered an anomaly.
        """
        self.window_size = window_size
        self.bandwidth = bandwidth
        self.density_threshold = density_threshold
        self.window = []

    def gaussian_kernel(self, distance):
        """
        Gaussian kernel function.
        
        Parameters:
        distance (float): Distance between points.

        Returns:
        float: The Gaussian kernel value.
        """
        return (1 / (np.sqrt(2 * np.pi) * self.bandwidth)) * np.exp(-0.5 * (distance / self.bandwidth) ** 2)

    def kernel_density_estimate(self, value):
        """
        Estimate the density of the value using a Gaussian kernel based on the sliding window.

        Parameters:
        value (float): The new value for which to estimate the density.

        Returns:
        float: The estimated density.
        """
        distances = np.abs(np.array(self.window) - value)
        kernel_values = self.gaussian_kernel(distances)
        density = np.sum(kernel_values) / (len(self.window) * self.bandwidth)
        return density

    def update(self, value):
        """
        Update the sliding window with a new value and detect anomalies using kernel density estimation.

        Parameters:
        value (float): New value from the data stream.

        Returns:
        int: 1 if the value is an anomaly, 0 otherwise.
        """
        # Add the new value to the sliding window
        self.window.append(value)

        # If the window exceeds the window_size, remove the oldest value
        if len(self.window) > self.window_size:
            self.window.pop(0)

        # If there are fewer points than needed for density estimation, return 0 (non-anomalous)
        if len(self.window) < 2:
            return 0

        # Estimate the density of the new value
        density = self.kernel_density_estimate(value)

        # Detect anomaly based on the density threshold
        if density < self.density_threshold:
            return 1  # Anomaly detected
        else:
            return 0  # No anomaly detected

class EWMA:
    def __init__(self, alpha=0.3, threshold=3):
        """
        Exponential Weighted Moving Average (EWMA) for anomaly detection.
        
        Parameters:
        alpha (float): Smoothing factor for the EWMA, ranges between 0 and 1.
        threshold (float): Z-score threshold for detecting anomalies.
        """
        self.alpha = alpha
        self.threshold = threshold
        self.ewma_value = None
        self.ewma_std = None
        self.n = 0  # Keeps track of the number of points processed
        self.mean = 0
        self.m2 = 0  # To track the variance

    def update(self, value):
        """
        Update the EWMA with a new value and detect anomalies.
        
        Parameters:
        value (float): New value from the data stream.
        
        Returns:
        int: 1 if the value is an anomaly, 0 otherwise.
        """
        if self.ewma_value is None:
            self.ewma_value = value
            self.ewma_std = 0
            return 0

        # Update EWMA
        self.ewma_value = self.alpha * value + (1 - self.alpha) * self.ewma_value

        # Update the variance using Welford's online algorithm
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        delta2 = value - self.mean
        self.m2 += delta * delta2
        variance = self.m2 / (self.n - 1) if self.n > 1 else 0
        self.ewma_std = np.sqrt(variance)

        # Calculate the Z-score
        z_score = (value - self.ewma_value) / self.ewma_std if self.ewma_std > 0 else 0

        # Detect anomaly
        return 1 if np.abs(z_score) > self.threshold else 0

class RankedSlidingWindowAnomalyDetection:
    def __init__(self, window_size=50, rank_threshold=0.95):
        """
        Ranked Sliding Window Anomaly Detection (RSWAD).
        
        Parameters:
        window_size (int): Size of the sliding window to hold recent data points.
        rank_threshold (float): Rank threshold for detecting anomalies (e.g., 0.95 means the top 5% ranked points are anomalies).
        """
        self.window_size = window_size
        self.rank_threshold = rank_threshold
        self.window = []

    def update(self, value):
        """
        Update the sliding window with a new value and detect anomalies using rank-based detection.
        
        Parameters:
        value (float): New value from the data stream.
        
        Returns:
        int: 1 if the value is an anomaly, 0 otherwise.
        """
        self.window.append(value)

        if len(self.window) > self.window_size:
            self.window.pop(0)

        if len(self.window) < self.window_size:
            return 0

        # Calculate median and deviations
        median = np.median(self.window)
        deviations = np.abs(np.array(self.window) - median)

        # Rank the deviations
        ranked_deviations = np.argsort(deviations)

        # Rank the current value's deviation
        current_deviation = np.abs(value - median)
        current_rank = np.searchsorted(deviations[ranked_deviations], current_deviation)

        # Calculate the normalized rank
        normalized_rank = current_rank / len(self.window)

        # Detect anomaly
        return 1 if normalized_rank > self.rank_threshold else 0

class MovingZScore:
    def __init__(self, window_size=20, threshold=3):
        """
        Moving Z-Score for anomaly detection.
        
        Parameters:
        window_size (int): Size of the sliding window to hold recent data points.
        threshold (float): Z-score threshold for detecting anomalies.
        """
        self.window_size = window_size
        self.threshold = threshold
        self.window = []

    def update(self, value):
        """
        Update the sliding window with a new value and detect anomalies using Z-Score.
        
        Parameters:
        value (float): New value from the data stream.
        
        Returns:
        int: 1 if the value is an anomaly, 0 otherwise.
        """
        # Add the new value to the sliding window
        self.window.append(value)

        # If the window exceeds the window_size, remove the oldest value
        if len(self.window) > self.window_size:
            self.window.pop(0)

        # If there are fewer points than the window size, return 0 (no anomaly detected)
        if len(self.window) < self.window_size:
            return 0

        # Calculate mean and standard deviation of the window
        mean = np.mean(self.window)
        std = np.std(self.window)

        # If the standard deviation is 0, treat the point as non-anomalous
        if std == 0:
            return 0

        # Calculate the Z-score of the new value
        z_score = (value - mean) / std

        # Detect anomaly based on the Z-score threshold
        if abs(z_score) > self.threshold:
            return 1  # Anomaly detected
        else:
            return 0  # No anomaly detected
        


