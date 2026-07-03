# IPL Value Engineering Dashboard 🏏📊

An interactive, data-driven sports analytics web application engineered to analyze Indian Premier League (IPL) auction dynamics, evaluate player ROI, and uncover hidden talent using financial performance metrics.

## 📌 Project Overview
Traditional sports statistics often fail to account for the financial context of player acquisitions. This project implements **Value Engineering principles** to assess whether franchises are overpaying for talent or identifying high-efficiency assets. By analyzing data across multiple variables, the pipeline exposes "Hidden Gems"—players delivering high on-field output relative to their auction valuation.

## 🛠️ Tech Stack & Architecture
* **Language:** Python 3.x
* **Core Data Engine:** Pandas, NumPy
* **Visualization Vector:** Plotly Express (Dynamic Scatter Plots)
* **Web Framework:** Streamlit (Responsive Cloud UI Architecture)
* **Testing Environment:** Google Colab / Localtunnel Pipeline

## ⚙️ Analytical Framework & Metrics
The pipeline computes specific data vectors to evaluate efficiency:
* **Cost Per Run (CPR):** Total Sold Price divided by Total Runs Scored.
* **Cost Per Wicket (CPW):** Total Sold Price divided by Total Wickets Taken.
* **Contribution Per Crore:** Normalized on-field performance metrics mapped against team spend parameters.
* **The Hidden Gems Quadrant:** A spatial layout mapping high performance (X-axis) against low cost (Y-axis) to identify undervalued players.

## 📂 Repository Structure
* `app.py`: The production-ready Streamlit web application code containing data transformation and caching logic.
* `cleaned_ipl_metrics_2024.csv`: The cleaned data file containing structural sports metrics.
* `IPL_Value_Engineering_EDA.ipynb`: Jupyter Notebook documenting the exploratory data analysis and initial validation tests.

## 🚀 How to Run Locally
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/ipl-value-engineering-dashboard.git](https://github.com/YOUR_USERNAME/ipl-value-engineering-dashboard.git)
