# 🏏 IPL Auction: Moneyball Squad Optimizer

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SciPy](https://img.shields.io/badge/SciPy-Optimization-8CAAE6?style=flat&logo=scipy&logoColor=white)]()

**Live Application:** [https://ipl-value-engineering-pvwrfqsz5wnp9b8yzufddb.streamlit.app/]

An interactive, data-driven Resource Allocation and Operations Research dashboard designed for sports franchise management. This engine moves beyond basic exploratory data analysis (EDA) by implementing **Integer Linear Programming (ILP)** to solve a complex Knapsack optimization problem: building the highest-impact 11-player squad under strict budgetary and role constraints.

## 🚀 Core Features & Architecture

* **Integer Linear Programming (0/1 Knapsack):** Utilizes `scipy.optimize.milp` to calculate mathematically optimal squad compositions based on total purse limits and minimum role requirements (Batters, Bowlers, All-Rounders, Wicketkeepers).
* **Value Engineering (The Moneyball Approach):** Calculates a proprietary `Value_Score` (On-Field Impact / Cost) to identify heavily undervalued assets in the auction pool.
* **Interactive Financial Visualizations:** Deploys `plotly.express` to map Price vs. On-Field Impact, visually isolating high-ROI players in the top-left statistical quadrant.
* **Session State Management:** Built with advanced Streamlit session state handling to ensure optimization results persist seamlessly during cross-tab filtering and individual player searches.

## 🛠️ Tech Stack

* **Language:** Python
* **Optimization & Math:** SciPy (`milp`), NumPy
* **Data Engineering:** Pandas
* **Frontend UI & Viz:** Streamlit, Plotly Express

## ⚙️ Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/MAverick107wq/ipl-value-engineering.git](https://github.com/MAverick107wq/ipl-value-engineering.git)
   cd ipl-value-engineering
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```
   
      
