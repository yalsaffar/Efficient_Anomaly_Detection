import numpy as np

class DataStreamSimulator:
    def __init__(self, amplitude=1, period=50, seasonality_amplitude=0.5, seasonality_period=500, noise_level=0.1, stream_length=10000, anomaly_chance=0.01, drift_rate=0.0001):
        """
        Initializes the data stream simulator with regular patterns, seasonality, noise, and optional anomalies.
        :param amplitude: Amplitude of the primary signal.
        :param period: Period of the primary signal (regular pattern).
        :param seasonality_amplitude: Amplitude of the seasonal signal.
        :param seasonality_period: Period of the seasonal signal.
        :param noise_level: Level of random noise to add to the signal.
        :param stream_length: Total length of the data stream.
        :param anomaly_chance: Probability of generating an anomaly at each time step.
        :param drift_rate: Rate at which the signal characteristics drift over time.
        """
        self.amplitude = amplitude
        self.period = period
        self.seasonality_amplitude = seasonality_amplitude
        self.seasonality_period = seasonality_period
        self.noise_level = noise_level
        self.stream_length = stream_length
        self.anomaly_chance = anomaly_chance
        self.drift_rate = drift_rate

    def generate_point(self, t):
        """
        Generates a single data point with the combination of regular, seasonal, noise components, and optional anomalies.
        :param t: Time step (or index in the stream).
        :return: Simulated data point at time step t.
        """
        # Apply drift over time to simulate changing conditions
        self.amplitude += self.drift_rate
        self.seasonality_amplitude += self.drift_rate
        
        # Regular pattern (e.g., sine wave)
        regular_component = self.amplitude * np.sin(2 * np.pi * t / self.period)
        
        # Seasonal component (e.g., longer-period sine wave)
        seasonal_component = self.seasonality_amplitude * np.sin(2 * np.pi * t / self.seasonality_period)
        
        # Random noise
        noise_component = self.noise_level * np.random.normal()
        
        # Combine components to generate the signal
        signal = regular_component + seasonal_component + noise_component
        
        # Introduce occasional anomalies
        if np.random.rand() < self.anomaly_chance:
            signal += np.random.uniform(5, 10)  # Add a random spike for anomalies
            
        return signal

    def stream_data(self):
        """
        Continuously generates a data stream and yields the data points with timestamps.
        """
        for t in range(self.stream_length):
            yield t, self.generate_point(t)

