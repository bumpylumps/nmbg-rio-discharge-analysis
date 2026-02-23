# Rio Grande Hydrologic Monitoring Pipeline
### Water Data Team Data Integration Task

This project provides a robust data pipeline for retrieving, cleaning, and analyzing real-time river discharge (or stream flow) data for the **Rio Grande** at **San Marcial, NM (USGS Site 08358400)** in the last 30 days.

---

## Selecting the Data
I started out gathering data on water discharge on the Rio from the **EPA Water Quality Portal (WQP)** by targetting sites around Albuquerque. But after consistently getting empty datasets from the WQP API, I pivoted to using the **USGS National Water Information System (NWIS)** API and was able to successfully retrieve accurate data sets. 

* **Selected Site:** Rio Grande Floodway at San Marcial, NM (USGS Site 08358400).
* **Data Retrieved:**  "Discharge" (stream flow) measured in cubic feet per second (cfs)
* **Timeframe:** The last 30 days from now

---

## Getting Started

### Prereq
* Python 3.x
* A virtual environment is recommended (like `venv`)

### Installation & Execution
1.  **Clone the repo** at ([https://github.com/bumpylumps/nmbg-rio-discharge-analysis](https://github.com/bumpylumps/nmbg-rio-discharge-analysis))
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the script**:
    ```bash
    python3 water_summary.py
    ```
    *Note: No `.env` files or API keys are required for the USGS API endpoint*

### Output
On success, the script runs through three actions:
1.  **CLI Dashboard:** Prints a formatted summary of min, max, and average flow directly to the terminal.
2.  **`rio_grande_data.csv`**: Exports a cleaned dataset with human-readable headers
3.  **`water_summary.json`**: Exports a structured JSON object for frontend consumption

---

## Technical Implementations
* **Data Integrity:** I implemented a "Coerce and Drop" pattern to handle USGS-specific RDB metadata, making sure that non-numeric flags in the dataset don't cause a panic (i.e. no chars like`20d`, `14n`) or corrupt calculations
* **Dynamic Parsing:** I utilized list comprehension and vectorized string operations to handle unpredictable column prefixes from USGS
* **Reliability:** Finally, I implemented a sort operation to ensure that the pipeline sorts the data by "latest time" before serving the "latest" reading to make sure that the "latest" field is accurate even if the API serves the data out of order

---

## Possible Improvements (Given More Time)
With more time, I would upgrade this tool from a script into a full-scale monitoring application with:

1.  **Interaction for Users:** I would develop a D3.js or Chart.js front end to consume the exported JSON object. The JSON could be used to render interactive time-series graphs of river trends.
2.  **Parameter Expansion:** I would also update the script to accept user-defined parameters for other metrics, such as:
    * **Gage Height** (River depth)
    * **Water Temperature**
3.  **Flexible Querying:** I’d move away from the script's hardcoded variables and implement a way for users to input their own date ranges and query for other metrics through forms on the aforementioned D3/Chart.js front end. This would allow users to use the project as a tool for research rather than serve a static snapshot of one metric in a fixed time range.
---