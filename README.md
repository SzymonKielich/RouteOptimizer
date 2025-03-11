# Public Transport Route Optimization

This project finds the fastest or least transfer-intensive routes between public transport stops using **Dijkstra** and **A*** algorithms. It uses Wrocław's public transport data (March 1, 2023) and supports multiple distance heuristics.

---

## Files

- **`reader.py`**: Reads and processes transport data from `connection_graph.csv`.
- **`algorithms.py`**: Implements Dijkstra and A* with heuristics (Haversine, Manhattan, Euclidean, Cosine, Chebyshev).
- **`constants.py`**: Contains constants like column names and average transport speed.
- **`main.py`**: Runs the algorithms on predefined stops and outputs results.

---

## How It Works

1. **Data Reading**: Reads and processes transport data, handling edge cases like midnight time wrapping.
2. **Algorithms**:
   - **Dijkstra**: Finds the shortest path based on travel time.
   - **A***: Uses heuristics to estimate remaining distance, optimizing for time or transfers.
3. **Heuristics**: Includes Haversine, Manhattan, Euclidean, Cosine, and Chebyshev distances.
4. **Execution**: Runs algorithms on predefined stops, outputting travel time, transfers, and computation time.
