# Forecasting Financial Inclusion in Ethiopia

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project analyzes and forecasts financial inclusion metrics for Ethiopia through 2027, leveraging unified datasets from Global Findex, National Bank of Ethiopia, and other sources. The project includes event impact modeling, time series forecasting, and an interactive dashboard.

## 📊 Project Overview

**Objective**: Generate robust forecasts for Ethiopian financial inclusion metrics (Access & Usage) incorporating the impacts of major events like Telebirr launch, M-Pesa entry, and Fayda Digital ID rollout.

**Key Features**:
- ✅ Comprehensive data enrichment with event tracking
- ✅ Exploratory data analysis with 5+ key insights
- ✅ Event impact modeling with structural break analysis
- ✅ Multi-model forecasting (ARIMA, Exponential Smoothing, Linear Regression)
- ✅ Scenario analysis (Base, Accelerated, Stagnation)
- ✅ Interactive Streamlit dashboard with 5+ visualizations
- ✅ Uncertainty quantification (80% and 95% confidence intervals)

## 🗂️ Project Structure

```
forecasting-financial-inclusion/
├── data/                                    # Raw and processed datasets
│   ├── ethiopia_fi_unified_data.xlsx       # Original unified dataset
│   ├── ethiopia_fi_unified_data_enriched.csv  # Enriched with new events
│   ├── reference_codes.xlsx                # Indicator reference codes
│   ├── account_ownership_forecast.csv      # Forecast output
│   └── forecast_scenarios.csv              # Scenario analysis output
├── src/                                    # Source code modules
│   ├── data_loader.py                      # Data loading and event utilities
│   ├── enrichment.py                       # Data enrichment logic
│   └── forecasting_utils.py               # Forecasting helper functions
├── notebooks/                              # Analysis notebooks
│   ├── eda.ipynb                          # Exploratory Data Analysis (Task 2)
│   ├── event_impact_modeling.ipynb        # Event impact analysis (Task 3)
│   └── forecasting.ipynb                  # Forecasting models (Task 4)
├── dashboard/                              # Interactive dashboard
│   ├── app.py                             # Main Streamlit application
│   ├── config.py                          # Dashboard configuration
│   └── utils.py                           # Dashboard utilities
├── tests/                                  # Unit tests
├── .github/workflows/                      # CI/CD pipelines
├── requirements.txt                        # Python dependencies
├── README.md                              # This file
└── INTERIM_REPORT.md                      # Detailed interim report

```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/msultan001/forecasting-financial-inclusion.git
   cd forecasting-financial-inclusion
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📋 Tasks Overview

### Task 1: Data Exploration and Enrichment ✅
**Branch**: `task-1`

- Loaded and analyzed unified dataset schema
- Enriched data with 3 new records:
  - National Digital ID (Fayda) launch event (EVT_2024_001)
  - 2024 account ownership estimate (OBS_2024_001)
  - Impact link between digital ID and access (IMP_2024_001)
- Documented all enrichments in `data_enrichment_log.md`

**Key Files**:
- `src/enrichment.py`
- `src/data_loader.py`
- `data/ethiopia_fi_unified_data_enriched.csv`

### Task 2: Exploratory Data Analysis (EDA) ✅
**Branch**: `task-2`

- Comprehensive EDA with 6+ key insights
- Event timeline visualization
- Data quality assessment
- Cross-pillar analysis
- Identified growth deceleration and event clustering patterns

**Key Files**:
- `notebooks/eda.ipynb`

**Insights**:
1. Account ownership growth deceleration (4.3% → 2.8% annual)
2. Event clustering in 2021-2024 period
3. Significant data sparsity (18-24 month gaps)
4. ACCESS pillar has most data; USAGE underrepresented
5. Infrastructure events precede access upticks
6. 68% of observations rated "high" confidence

### Task 3: Event Impact Modeling ✅
**Branch**: `task-3`

- Created event-indicator association matrix
- Implemented interrupted time series analysis
- Quantified impacts of major events:
  - **Telebirr**: +8-12pp boost to account ownership
  - **Conflict**: -3-5pp vs. trend
  - **Fayda ID**: +5-7pp expected (prospective)
- Historical validation of event impacts

**Key Files**:
- `notebooks/event_impact_modeling.ipynb`
- Enhanced `src/data_loader.py` with event analysis functions

**Outputs**:
- Event-indicator association heatmap
- Interrupted time series visualization
- Event impact summary table

### Task 4: Forecasting ✅
**Branch**: `task-4`

- Multiple forecasting models:
  - ARIMA with exogenous variables
  - Exponential Smoothing with damped trend
  - Linear regression with event adjustments
  - Ensemble forecast (weighted average)
- Scenario analysis (Base, Accelerated, Stagnation)
- Uncertainty quantification (80% and 95% CI)

**Key Files**:
- `notebooks/forecasting.ipynb`
- `src/forecasting_utils.py`

**Forecast Results (Base Case)**:
- **2025**: 55.5% (Range: 49.5-61.5%)
- **2026**: 58.2% (Range: 52.2-64.2%)
- **2027**: 60.5% (Range: 54.5-66.5%)

**Scenarios**:
- **Accelerated**: 66.5% by 2027 (+10% above base)
- **Stagnation**: 55.7% by 2027 (-8% below base)

### Task 5: Dashboard Development ✅
**Branch**: `task-5`

Interactive Streamlit dashboard with four main sections:

1. **Overview**: KPIs, executive summary, event timeline
2. **Trends**: Historical analysis, pillar distribution, data quality
3. **Forecasts**: Point forecasts with confidence intervals
4. **Projections**: Scenario analysis and recommendations

**Features**:
- 5+ interactive Plotly visualizations
- Sidebar filters (year range, pillar, confidence)
- Responsive design
- Downloadable data tables

## 🎨 Running the Dashboard

1. **Navigate to project root**
   ```bash
   cd forecasting-financial-inclusion
   ```

2. **Activate virtual environment** (if not already activated)
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Run the Streamlit dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

4. **Access the dashboard**
   - The dashboard will automatically open in your default browser
   - If not, navigate to: `http://localhost:8501`

5. **Interact with the dashboard**
   - Use sidebar filters to customize views
   - Hover over charts for detailed information
   - Explore different scenarios in the Projections section

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔄 Git Workflow

This project follows a task-based branching strategy:

```bash
# Branches
main          # Production-ready code
task-1        # Data exploration and enrichment
task-2        # EDA
task-3        # Event impact modeling
task-4        # Forecasting
task-5        # Dashboard development

# Commit message format
feat (task-X): "descriptive message"
fix (task-X): "bug fix description"
docs: "documentation update"
```

## 📊 Data Sources

- **Global Findex Database**: World Bank's comprehensive financial inclusion survey
- **National Bank of Ethiopia (NBE)**: Regulatory data and estimates
- **Fayda National ID**: Digital identity program information
- **Telebirr & M-Pesa**: Mobile money operator data

## 🔑 Key Findings

1. **Growth Trajectory**: Ethiopia's account ownership grew from 22% (2011) to 48.5% (2024)
2. **Major Drivers**: Telebirr launch (+8-12pp), Fayda ID rollout (expected +5-7pp)
3. **Forecast**: Base case projects 60.5% by 2027, with uncertainty range of 54.5-66.5%
4. **Policy Implication**: Ethiopia unlikely to reach 70% target by 2027 without accelerated interventions

## 📝 Documentation

- **`INTERIM_REPORT.md`**: Comprehensive report on Tasks 1 & 2 with stakeholder analysis
- **`data_enrichment_log.md`**: Detailed log of all data enrichment activities
- **Notebooks**: Each notebook contains markdown explanations and interpretations

## 🛠️ Technologies Used

- **Python 3.8+**
- **Data Analysis**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Forecasting**: statsmodels, scikit-learn, Prophet
- **Dashboard**: Streamlit
- **Version Control**: Git, GitHub
- **CI/CD**: GitHub Actions


