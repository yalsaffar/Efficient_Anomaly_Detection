import React, { useState } from 'react';
import { Chart as ChartJS, LineElement, PointElement, LinearScale, Title, Tooltip, Legend, CategoryScale } from 'chart.js';
import { Line } from 'react-chartjs-2';
import './App.css';

// Register necessary components
ChartJS.register(LineElement, PointElement, LinearScale, Title, Tooltip, Legend, CategoryScale);

function App() {
  const [params, setParams] = useState({
    amplitude: 1,
    period: 50,
    seasonality_amplitude: 0.5,
    seasonality_period: 500,
    noise_level: 0.1,
    stream_length: 10000,
    anomaly_chance: 0.01,
    drift_rate: 0.0001,
  });

  const [algorithm, setAlgorithm] = useState("EWMA");
  const [algorithmParams, setAlgorithmParams] = useState({
    alpha: 0.3,
    threshold: 3,
    window_size: 7,
    n_sigmas: 3,
    delta: 0.001,
    bandwidth: 1.0,
    density_threshold: 0.01,
    rank_threshold: 0.95,
  });

  const [dataPoints, setDataPoints] = useState([]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setParams({ ...params, [name]: parseFloat(value) });
  };

  const handleAlgorithmChange = (e) => {
    const selectedAlgorithm = e.target.value;
    setAlgorithm(selectedAlgorithm);
    
    // Reset algorithm parameters based on selected algorithm
    switch (selectedAlgorithm) {
      case "EWMA":
        setAlgorithmParams({ alpha: 0.3, threshold: 3 });
        break;
      case "StreamingHampelFilter":
        setAlgorithmParams({ window_size: 7, n_sigmas: 3 });
        break;
      case "ADWIN":
        setAlgorithmParams({ delta: 0.001 });
        break;
      case "SlidingWindowDensityEstimation":
        setAlgorithmParams({ window_size: 50, bandwidth: 1.0, density_threshold: 0.01 });
        break;
      case "RankedSlidingWindowAnomalyDetection":
        setAlgorithmParams({ window_size: 50, rank_threshold: 0.95 });
        break;
      case "OMLADEWMAStreaming":
        setAlgorithmParams({ threshold: 3, alpha: 0.3 });
        break;
      case "MovingZScore":
        setAlgorithmParams({ window_size: 20, threshold: 3 });
        break;
      default:
        setAlgorithmParams({});
        break;
    }
  };
  

  const handleAlgorithmParamChange = (e) => {
    const { name, value } = e.target;
    setAlgorithmParams({ ...algorithmParams, [name]: parseFloat(value) });
  };
  const [streaming, setStreaming] = useState(false); // State to track if streaming is active

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStreaming(true); // Set streaming to true when starting

    const response = await fetch('http://127.0.0.1:8000/start_stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...params,
        algorithm,
        algorithm_params: algorithmParams,
      }),
    });
    

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    // Clear previous data points
    setDataPoints([]);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const point = JSON.parse(decoder.decode(value));
      setDataPoints((prev) => [...prev, point]);
    }
  };

  // Prepare chart data
  const chartData = {
    labels: dataPoints.map((point) => point.timestamp),
    datasets: [
      {
        label: 'Data Stream',
        data: dataPoints.map((point) => point.value),
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
      {
        label: 'Anomalies',
        data: dataPoints
          .filter(point => point.anomaly === 1)
          .map(point => ({ x: point.timestamp, y: point.value })),
        backgroundColor: 'rgba(255,0,0,1)',
        pointRadius: 5,
        pointBackgroundColor: 'rgba(255,0,0,1)',
        fill: false,
      },
    ],
  };
  const handleStopStreaming = async () => {
    const response = await fetch('http://127.0.0.1:8000/stop_stream', {
      method: 'POST',
    });

    const data = await response.json();
    console.log(data.message);
    setStreaming(false); // Set streaming to false when stopping
  };
  return (
    <div className="container">
      <h1>Data Stream Visualizer</h1>
      <form onSubmit={handleSubmit}>
        {/* Dropdown for selecting anomaly detection algorithm */}
        <div className="section" >
        <h2>Indicator Selection</h2>
          <label>
            Select Algorithm:
            <select value={algorithm} onChange={handleAlgorithmChange}>
              <option value="EWMA">EWMA</option>
              <option value="StreamingHampelFilter">Streaming Hampel Filter</option>
              <option value="ADWIN">ADWIN</option>
              <option value="SlidingWindowDensityEstimation">Sliding Window Density Estimation</option>
              <option value="RankedSlidingWindowAnomalyDetection">Ranked Sliding Window Anomaly Detection</option>
              <option value="OMLADEWMAStreaming">OMLADEWMA Streaming</option>
              <option value="MovingZScore">Moving Z-Score</option>
            </select>
          </label>
        </div>

        {/* Dynamic inputs for algorithm parameters */}
        {algorithm === "EWMA" && (
          <>
            <label>
              Alpha:
              <input type="number" name="alpha" value={algorithmParams.alpha} onChange={handleAlgorithmParamChange} step={0.01} />
            </label>
            <label>
              Threshold:
              <input type="number" name="threshold" value={algorithmParams.threshold} onChange={handleAlgorithmParamChange} step={0.1} />
            </label>
          </>
        )}
        {algorithm === "StreamingHampelFilter" && (
          <>
            <label>
              Window Size:
              <input type="number" name="window_size" value={algorithmParams.window_size} onChange={handleAlgorithmParamChange} />
            </label>
            <label>
              N Sigmas:
              <input type="number" name="n_sigmas" value={algorithmParams.n_sigmas} onChange={handleAlgorithmParamChange} />
            </label>
          </>
        )}
        {algorithm === "ADWIN" && (
          <label>
            Delta:
            <input type="number" name="delta" value={algorithmParams.delta} onChange={handleAlgorithmParamChange} step={0.001} />
          </label>
        )}
        {algorithm === "SlidingWindowDensityEstimation" && (
          <>
            <label>
              Window Size:
              <input type="number" name="window_size" value={algorithmParams.window_size} onChange={handleAlgorithmParamChange} />
            </label>
            <label>
              Bandwidth:
              <input type="number" name="bandwidth" value={algorithmParams.bandwidth} onChange={handleAlgorithmParamChange} step={0.1} />
            </label>
            <label>
              Density Threshold:
              <input type="number" name="density_threshold" value={algorithmParams.density_threshold} onChange={handleAlgorithmParamChange} step={0.01} />
            </label>
          </>
        )}
        {algorithm === "RankedSlidingWindowAnomalyDetection" && (
          <label>
            Rank Threshold:
            <input type="number" name="rank_threshold" value={algorithmParams.rank_threshold} onChange={handleAlgorithmParamChange} step={0.01} />
          </label>
        )}
        {algorithm === "OMLADEWMAStreaming" && (
          <>
            <label>
              Threshold:
              <input type="number" name="threshold" value={algorithmParams.threshold} onChange={handleAlgorithmParamChange} step={0.1} />
            </label>
            <label>
              Alpha:
              <input type="number" name="alpha" value={algorithmParams.alpha} onChange={handleAlgorithmParamChange} step={0.01} />
            </label>
          </>
        )}
        {algorithm === "MovingZScore" && (
          <>
            <label>
              Window Size:
              <input type="number" name="window_size" value={algorithmParams.window_size} onChange={handleAlgorithmParamChange} />
            </label>
            <label>
              Threshold:
              <input type="number" name="threshold" value={algorithmParams.threshold} onChange={handleAlgorithmParamChange} step={0.1} />
            </label>
          </>
        )}

        {/* Data simulation fields */}
        <div className="section">
        <h2>Data Simulation Parameters</h2>
        {Object.keys(params).map((key) => (
          <div key={key}>
            <label>
              {key}:
              <input
                type="number"
                name={key}
                value={params[key]}
                onChange={handleChange}
                step={0.01}
                required
              />
            </label>
          </div>
        ))}
        </div>
        <button type="submit">Start Stream</button>
        <button type="button" onClick={handleStopStreaming} disabled={!streaming}>Stop Stream</button>

      </form>
      <Line data={chartData} />
    </div>
  );
}

export default App;
