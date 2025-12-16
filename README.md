# Quant Trading Analytics Dashboard

## Overview
This is a high-performance, real-time trading analytics system designed for statistical arbitrage and pair trading strategies. Built with a production-first mindset, it ingests live market data from Binance Futures, processes quantitative signal metrics in near real-time, and surfaces actionable insights via a low-latency dashboard.

The system focuses on correctness, numerical stability, and explainability, providing traders and quantitative researchers with distinct signals for mean-reversion opportunities. It features a clean separation of concerns: robust data ingestion, a centralized analytics engine, a rule-based alerting system, and a responsive React frontend.

## Architecture Overview
The system follows a modular, event-driven architecture optimized for low latency and high throughput without unnecessary complexity.

*   **Ingestion Layer**: Asynchronous WebSocket client (Binance Futures) handling high-frequency tick data.
*   **Data Processing**: In-memory optimized rolling buffers (Deques) for uniform O(1) time complexity on updates.
*   **Analytics Engine**: Computes statistical metrics (Spread, Z-Score, Correlation) on every tick.
*   **API Layer**: FastAPI server exposing standardized REST endpoints.
*   **Frontend**: React-based dashboard for visualization and configuration.

[Architecture Diagram]

<img width="2655" height="887" alt="Quant analytics Architechture Diagram" src="https://github.com/user-attachments/assets/15baed38-9074-46d5-b5e7-e5cdc91bcf8e" />


## Data Ingestion
The system connects directly to the **Binance Futures WebSocket** stream to subscribe to real-time distinct trade events:
*   **Streams**: `btcusdt@trade`, `ethusdt@trade`.
*   **Normalization**: Raw payloads are parsed into structured tick data containing accurate ingestion timestamps (high-precision epoch), price, and quantity.
*   **Resilience**: Implements automatic connection monitoring and exponential backoff strategies for reconnection, ensuring stream continuity.
*   **Storage**: Data is maintained in volatile memory for valid "live" window analysis. Persistence was intentionally scoped out to prioritize real-time processing speed and minimize I/O latency for this specific assignment.

## Sampling & Timeframes
*   **Internal Resolution**: The core engine processes data at the tick level, aggregating updates into rolling windows.
*   **Window Size**: analytics are computed over a moving window of the most recent 50 data points, providing a reactive "live" view of market dynamics.
*   **Scope**: While the architecture supports multi-timeframe resampling (1s, 1m, 5m), this release focuses on the immediate high-frequency domain. A UI timeframe selector was intentionally scoped out to ensure maximum stability of the real-time indicators.

## Core Analytics Implemented

| Metric | Description | Usage |
| :--- | :--- | :--- |
| **Price Stats** | Rolling price history for BTC and ETH | Base asset monitoring and synchronization |
| **Hedge Ratio** | Fixed or Dynamic Ratio (Current: 25.0) | Normalizes the pair for spread calculation |
| **Spread** | `Price(BTC) - Ratio * Price(ETH)` | Identifies absolute price deviations between the pair |
| **Z-Score** | Standardized Score `(Spread - Mean) / StdDev` | Primary signal for mean-reversion entry/exit |
| **Rolling Correlation** | Pearson correlation coefficient | Regime filter to validate pair relationship stability |
| **Stationarity** | Threshold-based check | Verifies if the spread is mean-reverting (tradable) |

## Alert Engine
A robust alert state machine runs downstream of the analytics engine:
*   **Entry Signals**: Triggered when Z-Score magnitude exceeds the configured `Entry Threshold` (default: 2.0).
*   **Exit Signals**: Triggered when Z-Score reverts within the `Exit Threshold` (default: 0.5).
*   **Filters**: Alerts are suppressed if the Rolling Correlation is below the configured minimum (default: 0.7), preventing false signals during market decoupling.
*   **State Management**: Dedupes alerting to prevent signal spam, mirroring real-world execution system constraints.

## API Layer
The backend exposes a documented, type-safe REST API powered by **FastAPI**:

*   `GET /health`: System readiness and heartbeat check.
*   `GET /analytics/latest`: Low-latency endpoint for the most recent signal snapshot.
*   `GET /analytics/stats`: Full time-series history for tabular display.
*   `GET /analytics/stats/csv`: Streams real-time analytics data as a downloadable CSV file.
*   `GET /config` & `POST /config`: Runtime configuration management.

The API is fully decoupled from the frontend, allowing for independent scaling or integration with other execution algorithms.

## Frontend Dashboard
The user interface is a professional, Dark Mode trader dashboard built with **React** and **Recharts**.

*   **Real-time Visualization**: Dynamic line charts for Z-Score, Spread, and Correlation with millisecond-precision timestamps.
*   **Status Indicators**: Visual cues for Stationarity (Yes/No) and Active Signal (Long/Short/None).
*   **Data Export**: Integrated "Download CSV" functionality for offline quant research.
*   **Operational Awareness**: Displays 'Warm-up' status during initial data collection and connection health.
*   **UX**: Designed for density and clarity—no marketing fluff, just data.

## Configuration Management
Traders can adjust risk parameters on the fly without restarting the kernel:
*   **Z-Score Entry/Exit Thresholds**: Tweak sensitivity to volatility.
*   **Minimum Correlation**: Adjust regime filter stringency.
*   **Persistence**: Settings are stored in server memory and apply immediately to the next tick processed by the analytics engine.

## Design Decisions & Trade-offs
*   **In-Memory Architecture**: Chosen over a Time-Series Database (e.g., InfluxDB/KDB+) to strictly meet the assignment timeline and minimize deployment complexity while offering nanosecond-level access speeds.
*   **REST Polling vs. WebSockets**: While the backend ingests via WebSockets, the frontend uses optimized polling. This simplifies state management and separates the ingestion loop from the presentation layer, increasing system stability.
*   **Fixed Hedge Ratio**: A fixed ratio was used for this MVP to prove the pipeline's stability. In a production version, this would be computed dynamically via OLS or Kalman Filter.

## How This Helps Traders & Researchers
1.  **Noise Reduction**: The correlation filter automatically hides signals when the pair relationship breaks down, protecting capital.
2.  **Visual Confirmation**: Overlaying Z-Score with threshold lines provides instant visual confirmation of potential trade setups.
3.  **Data Portability**: The CSV export allows researchers to pull "live" data snapshots instantly to validate hypothesis in Python/Pandas.

## How to Run the Project

### Backend
```bash
# From root directory
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
# From frontend directory
cd frontend
npm install
npm start
```
The dashboard will launch at `http://localhost:3000`.

## Future Extensions
*   **Dynamic Hedge Ratio**: Implement online OLS or Kalman Filtering for adaptive ratios.
*   **Timeframe Selection**: Support for 1m, 5m, and 1h aggregate bars.
*   **Backtesting Module**: Replay historical data against current config parameters.
*   **Execution Connector**: Hook alerts directly into an OMS (Order Management System).
*   **Persistence**: Integrate TimescaleDB for long-term data storage.

## AI Usage Transparency
This project was developed using modern AI-assisted development tools available in the market to improve development speed and accuracy with prompt engineering techniques.

### How AI Tools Were Used
AI tools were used mainly to:
*   Clearly understand the problem statement and requirements
*   Plan the overall system flow
*   Identify and fix errors, edge cases, and stability issues
*   Improve numerical calculations such as rolling windows, correlation, and warm-up handling

### Development Approach
The project was built in clear phases, using AI tools as a support system:
*   **Planning Phase**: Helped break down the problem and define the data flow.
*   **Backend Development**: Assisted in building WebSocket ingestion, analytics logic, and APIs.
*   **Frontend Development**: Helped connect live data, charts, tables, and settings smoothly.
*   **Testing & Fixing**: Helped detect runtime issues, unstable values, and startup behavior problems.

AI tools were used only to speed up development and improve correctness. This approach helped build the system faster, cleaner, and more reliable, while maintaining full understanding and control over the entire application.

## Results 
## Dashboard
<img width="2559" height="1140" alt="Screenshot 2025-12-16 143149" src="https://github.com/user-attachments/assets/b425ce0c-b57b-4220-91c9-bca5884d4298" />

## Analytics
<img width="2139" height="839" alt="image" src="https://github.com/user-attachments/assets/3ea74d6e-089d-4c22-9aa8-ce98934fbccc" />

<img width="2559" height="746" alt="Screenshot 2025-12-16 143214" src="https://github.com/user-attachments/assets/d77ffad1-7731-4856-bfae-d8034b86bdbd" />
<img width="2559" height="732" alt="Screenshot 2025-12-16 143225" src="https://github.com/user-attachments/assets/460117c1-0f76-44e2-8208-5f79d0ac8d4c" />
<img width="2558" height="1003" alt="Screenshot 2025-12-16 143242" src="https://github.com/user-attachments/assets/0d09923f-8a39-4cb1-966b-76bfc0f17173" />

# Settings
<img width="2559" height="1326" alt="Screenshot 2025-12-16 143251" src="https://github.com/user-attachments/assets/99e9ed7f-5f07-4275-b145-b4278dda83b1" />

## Conclusion
This project represents a solid, production-grade foundation for a statistical arbitrage system. By prioritizing numerical stability, clean architecture, and type safety, it delivers a reliable tool for monitoring and analyzing live market inefficiencies. The modular design ensures it is readily extensible for complex production trading environments.
