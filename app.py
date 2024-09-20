from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from algorithm_implementation.data_stream_simulator import DataStreamSimulator
# Import the anomaly detection algorithms
from algorithm_implementation.algorithms import (
    EWMA, StreamingHampelFilter, ADWIN, 
    SlidingWindowDensityEstimation, 
    RankedSlidingWindowAnomalyDetection, 
    OMLADEWMAStreaming, MovingZScore
)
import asyncio
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
current_stream_task = None
stop_event = asyncio.Event()

class StreamParams(BaseModel):
    amplitude: float = 1.0
    period: int = 50
    seasonality_amplitude: float = 0.5
    seasonality_period: int = 500
    noise_level: float = 0.1
    stream_length: int = 10000
    anomaly_chance: float = 0.01
    drift_rate: float = 0.0001
    algorithm: str
    algorithm_params: dict

async def data_stream(simulator: DataStreamSimulator, algorithm: str, algorithm_params: dict):
    # Initialize the anomaly detectors based on the selected algorithm
    if algorithm == "EWMA":
        detector = EWMA(alpha=algorithm_params['alpha'], threshold=algorithm_params['threshold'])
    elif algorithm == "StreamingHampelFilter":
        detector = StreamingHampelFilter(window_size=algorithm_params['window_size'], n_sigmas=algorithm_params['n_sigmas'])
    elif algorithm == "ADWIN":
        detector = ADWIN(delta=algorithm_params['delta'])
    elif algorithm == "SlidingWindowDensityEstimation":
        detector = SlidingWindowDensityEstimation(window_size=algorithm_params['window_size'], 
                                                  bandwidth=algorithm_params['bandwidth'], 
                                                  density_threshold=algorithm_params['density_threshold'])
    elif algorithm == "RankedSlidingWindowAnomalyDetection":
        detector = RankedSlidingWindowAnomalyDetection(window_size=algorithm_params['window_size'], 
                                                       rank_threshold=algorithm_params['rank_threshold'])
    elif algorithm == "OMLADEWMAStreaming":
        detector = OMLADEWMAStreaming(threshold=algorithm_params['threshold'], alpha=algorithm_params['alpha'])
    elif algorithm == "MovingZScore":
        detector = MovingZScore(window_size=algorithm_params['window_size'], threshold=algorithm_params['threshold'])
    
    try:
        while not stop_event.is_set():
            for timestamp, point in simulator.stream_data():
                if stop_event.is_set():
                    break  # Exit if stop event is set
                anomaly = detector.update(point)  # Check for anomalies
                data = {"timestamp": timestamp, "value": point, "anomaly": anomaly}
                yield json.dumps(data).encode('utf-8') + b"\n"
                await asyncio.sleep(0.1)
    finally:
        stop_event.clear()  # Clear the event when finished

@app.post("/start_stream")
async def start_stream(params: StreamParams):
    global stop_event
    stop_event.clear()  # Clear any previous stop event

    simulator = DataStreamSimulator(
        amplitude=params.amplitude,
        period=params.period,
        seasonality_amplitude=params.seasonality_amplitude,
        seasonality_period=params.seasonality_period,
        noise_level=params.noise_level,
        stream_length=params.stream_length,
        anomaly_chance=params.anomaly_chance,
        drift_rate=params.drift_rate
    )

    return StreamingResponse(data_stream(simulator, params.algorithm, params.algorithm_params), media_type="application/json")

@app.post("/stop_stream")
async def stop_stream():
    global stop_event
    stop_event.set()  # Set the stop event
    return {"message": "Streaming stopped and ready for new requests."}
