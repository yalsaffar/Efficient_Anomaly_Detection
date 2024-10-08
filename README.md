# Efficient Streamed Anomaly Detection
🌟 If you want, you can start by checking out the live demo of the full implementation at this link: [Live Dashboard](https://cobblestone-next-9bql.vercel.app/), and then read through everything! 😊

## Requirements
Before running the project, ensure all requirements are installed. Use the following command to install them:

```bash
pip install -r requirements.txt
```
## 1. Algorithm Selection

### Introduction
The selection of the right algorithm for anomaly detection can be quite a challenge, especially given the ambiguous nature of the data. It’s important to ensure the algorithm is fully optimized and efficient, while keeping things simple by avoiding external libraries and advanced AI models to maintain speed.😅

### Approach
1. **Dataset Identification**: I utilized the Numenta Anomaly Benchmark (NAB), specifically datasets from the `artificialWithAnomaly` and `realKnownCause` categories. These datasets include concept drift and seasonal variations, with ground truth labels for reference. [Source](https://github.com/numenta/NAB) and [Source2](https://github.com/ngobibibnbe/anomaly-detection-in-data-stream/tree/master?tab=readme-ov-file#datasets-and-their-characteristics)

2. **Research on Algorithms**: I researched efficient algorithms that do not require external libraries or models. The implemented algorithms include:
   - [OMLADStreaming](https://www.arxiv.org/abs/2409.09742)
   - [OMLADEWMAStreaming](https://www.arxiv.org/abs/2409.09742)
   - [StreamingHampelFilter](https://medium.com/data-and-beyond/outlier-detection-in-r-hampel-filter-for-time-series-15ca7d166067)
   - [ADWIN](https://www.researchgate.net/figure/Output-of-algorithm-ADWIN-with-slow-gradual-changes_fig2_220907178)
   - [SlidingWindowDensityEstimation](https://www.researchgate.net/figure/Estimation-of-the-data-distribution-in-the-sliding-window-for-two-time-instances-2-d_fig3_321121463)
   - [EWMA](https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/exponentially-weighted-moving-average-ewma/)
   - [RankedSlidingWindowAnomalyDetection](https://www.sciencedirect.com/science/article/pii/S1877050922023328/pdf?md5=75a26ac3731870a82946c964dc17d2a9&pid=1-s2.0-S1877050922023328-main.pdf)
   - MovingZScore

   Note: Each implementation has its own parameters, and hyperparameter tuning was discarded due to:
   - Variations in dataset patterns.
   - The ambiguous nature of the datasetin the task.

3. **Performance Metrics**: Average precision, recall, and F1 score were calculated for each algorithm. The concept of tolerance was applied to increase the detection window, which is crucial for accurately detecting anomalies. [Source](https://github.com/ngobibibnbe/anomaly-detection-in-data-stream/blob/master/summary_of_the_experiments.pdf)

4. **Efficiency Measurement**: Average processing time for each method was calculated for performance assessment.

### Results

| Algorithm                    | Precision | Recall   | F1 Score | Average Time |
|------------------------------|-----------|----------|----------|--------------|
| ADWIN                        | 0.054949  | 0.822629 | 0.098765 | 0.000451     |
| EWMA                        | 0.036809  | 0.018331 | 0.024366 | 0.000003     |
| MovingZScore                | 0.054703  | 0.013978 | 0.020132 | 0.000031     |
| OMLADEWMAStreaming          | 0.048432  | 0.049748 | 0.047863 | 0.000002     |
| OMLADStreaming              | 0.204724  | 0.098451 | 0.119517 | 0.000002     |
| RSWAD                       | 0.080794  | 0.070311 | 0.062563 | 0.000039     |
| SWDE                        | 0.057087  | 0.024431 | 0.028602 | 0.000015     |
| StreamingHampelFilter       | 0.056354  | 0.124949 | 0.074400 | 0.000050     |

### Conclusion
- **ADWIN** achieved the highest recall (0.822629), indicating its effectiveness in identifying a large proportion of actual anomalies, but it has low precision.
- **OMLADStreaming** has the best precision (0.204724), meaning it has the highest ratio of true positives among the detected anomalies.
- **OMLADStreaming** also has the highest F1 score (0.119517), reflecting a better balance between precision and recall compared to other methods.
- All methods maintained low average processing times, suggesting efficient performance.
- The nature of the datasets varies, which may affect the results.
- No hyperparameter tuning was performed due to time constraints, which could lead to suboptimal performance of the algorithms.
- The nature of the actual data is unknown, aside from having drift and seasonality, making this evaluation primarily a demonstration of the methods rather than definitive conclusions on their effectiveness.
- This process serves to illustrate that further examination and analysis are essential for selecting the best anomaly detection algorithm.

All the above is documented in the folder called `"algorithm_selection"`, which includes a data folder and a notebook that walks through the steps🤗.

## 2. Algorithms Implementation

All the mentioned algorithms are implemented in `algorithms.py` as classes. This structure allows for maintaining the state of the data being processed, which is crucial for the streaming nature of the task⏩⏩⏩.

### Data Stream Simulator
The `data_stream_simulator.py` class simulates the streamed data as required by the project. It takes the following parameters into consideration:

```python
class DataStreamSimulator:
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
```

### Visualization
Finally, a notebook called `visualization.ipynb` provides a user-friendly interface to visualize all algorithms in action with the streamed data📺.


## 3. Data Stream Visualizer

In this step, I created an advanced frontend using React and JavaScript, alongside a FastAPI app in the root folder, to develop a fully customizable dashboard for testing different algorithms with different simulated data in the browser.

### Running Locally
To run this locally, follow these steps:
1. Inside the `frontend` folder, run:
   ```bash
   npm install
   npm start
   ```
2. In the main folder, run:
    ```
    uvicorn app:app --reload
    ```
3. Ensure you have Node.js installed.

### Online Access
Alternatively, I created a separate clone of the project using Next.js, which I deployed on Vercel, along with the API deployed on Heroku. You can access the interface at the following link: [ONLINE DEMO](https://cobblestone-next-9bql.vercel.app/) 🥳

## Conclusion

To wrap things up, this project showcases my journey into anomaly detection in data streams! I carefully selected algorithms based on their ability to handle concept drift and seasonal variations, ensuring they fit the unique challenges we face. The implementation relied on Pandas and NumPy, optimized for speed to keep things running smoothly.

By applying a tolerance concept, I was able to enhance the detection window, leading to some interesting results. It's important to remember that there isn’t **one definitive answer** when it comes to choosing the right algorithm; often, it's about the specific case at hand or even a combination of multiple methods in real-world scenarios.

The simple notebook interface is a great way to visualize how everything works, making it user-friendly and accessible. Plus, the React app paired with FastAPI adds a fun layer of customization, allowing users to tailor their experience.

And don’t forget to check out the Next.js and FastAPI implementation, deployed on Vercel and Heroku! It’s a nice and simple way to explore the full capabilities of the project in an interactive environment. I hope you find this approach insightful and engaging!

## Thank You 🙏
Thank you for taking the time to review my application! I truly hope I meet your expectations and look forward to the possibility of working together.🙏


