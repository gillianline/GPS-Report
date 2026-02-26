# Daily GPS Positional Report

A Streamlit App to visualize and analyze athlete GPS performance data. Upload your Excel export and instantly generate team and position-level reports with charts, metrics, and tables.

---

## Features

- Select **Session Intensity**: High, Medium, Low
- Enter a **Practice Label** for reporting
- **Metrics & Visualizations**:
  - Total Player Load
  - High-Speed Distance (HSD)
  - Acceleration / Deceleration Efforts
  - Explosive Work
  - Maximum Velocity (% Max)
- **Position Reports**:
  - Scatter plots (Load vs Top Speed)
  - HSD bar charts
  - Explosive effort breakdown
  - Elite / Grinder lists
  - Roster tables with conditional formatting
- **Team Overview**: Average metrics by position with bar charts

---


### Prerequisites

- Python 3.9+
- Streamlit, Pandas, Plotly, NumPy, OpenPyXL

Install dependencies:

```bash
pip install streamlit pandas plotly numpy openpyxl



## Running the App
- streamlit run app.py
- Upload your Excel GPS export.
- Select session intensity and label.
- Explore Team Overview and individual Position Tabs.
- Metrics and charts update automatically.


## Excel Data Requirements
Columns needed:
- Name
- Position Name
- Total Player Load
- 60-75% Dist
- 82%+ Distance Tempo1 (y)
- 82-90% Dist
- Acceleration B1 Efforts (Gen 2)
- Acceleration B2 Efforts (Gen 2)
- Acceleration B3 Efforts (Gen 2)
- Deceleration B1 Efforts (Gen 2)
- Deceleration B2 Efforts (Gen 2)
- Deceleration B3 Efforts (Gen 2)
- Maximum Velocity (mph)
- Max Vel (% Max)
(Extra columns are ignored. Missing columns are treated as 0.)