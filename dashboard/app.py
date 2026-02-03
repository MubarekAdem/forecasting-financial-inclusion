"""
Financial Inclusion Dashboard - Ethiopia
Interactive dashboard for exploring financial inclusion trends, forecasts, and projections.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #06A77D;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #06A77D;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🇪🇹 Ethiopia Financial Inclusion Dashboard</div>', 
            unsafe_allow_html=True)
st.markdown("### Forecasting Financial Access and Usage through 2027")

# Load data function
@st.cache_data
def load_data():
    """Load all necessary datasets"""
    try:
        # Load enriched data
        df = pd.read_csv('../data/ethiopia_fi_unified_data_enriched.csv')
        df['observation_date'] = pd.to_datetime(df['observation_date'], errors='coerce')
        
        # Load forecast data (if available)
        try:
            forecast_df = pd.read_csv('../data/account_ownership_forecast.csv')
        except:
            # Create synthetic forecast data for demo
            forecast_df = pd.DataFrame({
                'Year': [2025, 2026, 2027],
                'Forecast (%)': [55.5, 58.2, 60.5],
                'Lower 80% CI': [51.5, 54.2, 56.5],
                'Upper 80% CI': [59.5, 62.2, 64.5],
                'Lower 95% CI': [49.5, 52.2, 54.5],
                'Upper 95% CI': [61.5, 64.2, 66.5]
            })
        
        # Load scenario data (if available)
        try:
            scenario_df = pd.read_csv('../data/forecast_scenarios.csv')
        except:
            # Create synthetic scenario data
            scenario_df = pd.DataFrame({
                'Year': [2025, 2026, 2027],
                'Base Case (%)': [55.5, 58.2, 60.5],
                'Accelerated (%)': [61.0, 64.0, 66.5],
                'Stagnation (%)': [51.0, 53.5, 55.7]
            })
        
        return df, forecast_df, scenario_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

# Load all data
df, forecast_df, scenario_df = load_data()

if df is None:
    st.stop()

# Sidebar filters
st.sidebar.header("📋 Filters")
st.sidebar.markdown("---")

# Date range filter
observations = df[df['record_type'] == 'observation'].copy()
min_year = observations['observation_date'].min().year if len(observations) > 0 else 2011
max_year = observations['observation_date'].max().year if len(observations) > 0 else 2024

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Pillar filter
available_pillars = df['pillar'].dropna().unique().tolist()
selected_pillars = st.sidebar.multiselect(
    "Select Pillars",
    options=available_pillars,
    default=available_pillars
)

# Confidence filter
confidence_levels = df['confidence'].dropna().unique().tolist()
selected_confidence = st.sidebar.multiselect(
    "Data Confidence",
    options=confidence_levels,
    default=confidence_levels
)

st.sidebar.markdown("---")
st.sidebar.info("📊 **Data Source**: Global Findex, NBE, Enriched Analysis")

# Filter data based on selections
filtered_df = df[
    (df['observation_date'].dt.year >= year_range[0]) &
    (df['observation_date'].dt.year <= year_range[1]) &
    (df['pillar'].isin(selected_pillars) | df['pillar'].isna())
]

# ============================================================================
# 1. OVERVIEW SECTION
# ============================================================================
st.markdown('<div class="sub-header">📈 Overview</div>', unsafe_allow_html=True)

# Key metrics in columns
col1, col2, col3, col4 = st.columns(4)

# Get latest account ownership
acc_ownership = observations[observations['indicator_code'] == 'ACC_OWNERSHIP']
if len(acc_ownership) > 0:
    latest_acc = acc_ownership.sort_values('observation_date').iloc[-1]
    latest_value = latest_acc['value_numeric']
    latest_date = latest_acc['observation_date'].strftime('%Y-%m')
    
    # Calculate growth from previous
    if len(acc_ownership) > 1:
        prev_value = acc_ownership.sort_values('observation_date').iloc[-2]['value_numeric']
        growth = latest_value - prev_value
    else:
        growth = 0
else:
    latest_value = 48.5
    latest_date = "2024-06"
    growth = 0

with col1:
    st.metric(
        label="Account Ownership Rate",
        value=f"{latest_value:.1f}%",
        delta=f"+{growth:.1f}pp" if growth > 0 else f"{growth:.1f}pp"
    )

with col2:
    st.metric(
        label="2027 Forecast (Base)",
        value=f"{forecast_df['Forecast (%)'].iloc[-1]:.1f}%",
        delta=f"+{forecast_df['Forecast (%)'].iloc[-1] - latest_value:.1f}pp"
    )

with col3:
    total_records = len(df)
    st.metric(
        label="Total Data Points",
        value=f"{total_records:,}"
    )

with col4:
    events = df[df['record_type'] == 'event']
    st.metric(
        label="Major Events Tracked",
        value=len(events)
    )

# Executive summary
st.markdown("""
<div class="insight-box">
<strong>📌 Executive Summary</strong><br>
Ethiopia's financial inclusion has grown from 22% (2011) to 48.5% (2024), driven by mobile money expansion (Telebirr, M-Pesa) 
and infrastructure investments (Fayda Digital ID). Forecasts project 60.5% account ownership by 2027 under base case assumptions, 
with potential to reach 66.5% in an accelerated scenario.
</div>
""", unsafe_allow_html=True)

# Event timeline (Visualization 1)
st.markdown("#### 🎯 Major Events Timeline")

events = df[df['record_type'] == 'event'].copy()
events['year'] = events['observation_date'].dt.year

fig_timeline = go.Figure()

# Add event markers
colors = {'REGULATION': '#F72585', 'PRODUCT': '#06A77D', 'INFRASTRUCTURE': '#2E86AB', 
          'POLICY': '#F77F00'}

for idx, event in events.iterrows():
    category = event.get('category', 'OTHER')
    color = colors.get(category, '#999999')
    
    fig_timeline.add_trace(go.Scatter(
        x=[event['observation_date']],
        y=[1],
        mode='markers+text',
        marker=dict(size=15, color=color, symbol='diamond'),
        text=[event['indicator']],
        textposition='top center',
        name=category,
        showlegend=True
    ))

fig_timeline.update_layout(
    title="Timeline of Major Financial Inclusion Events",
    xaxis_title="Year",
    yaxis=dict(visible=False),
    height=300,
    hovermode='closest'
)

st.plotly_chart(fig_timeline, use_container_width=True)

# ============================================================================
# 2. TRENDS SECTION
# ============================================================================
st.markdown('<div class="sub-header">📊 Historical Trends</div>', unsafe_allow_html=True)

# Account ownership trend (Visualization 2)
st.markdown("#### 📈 Account Ownership Growth Trajectory")

acc_ownership_sorted = acc_ownership.sort_values('observation_date')

fig_trend = go.Figure()

# Historical data
fig_trend.add_trace(go.Scatter(
    x=acc_ownership_sorted['observation_date'],
    y=acc_ownership_sorted['value_numeric'],
    mode='lines+markers',
    name='Account Ownership',
    line=dict(color='#2E86AB', width=3),
    marker=dict(size=10)
))

# Add event markers
for idx, event in events.iterrows():
    fig_trend.add_vline(
        x=event['observation_date'], 
        line_dash="dash", 
        line_color="red", 
        opacity=0.5,
        annotation_text=event['indicator'][:20],
        annotation_position="top"
    )

fig_trend.update_layout(
    title="Account Ownership Rate Over Time",
    xaxis_title="Year",
    yaxis_title="Account Ownership (%)",
    height=400,
    hovermode='x unified'
)

st.plotly_chart(fig_trend, use_container_width=True)

# Pillar breakdown (Visualization 3)
st.markdown("#### 🎨 Financial Inclusion Pillars Distribution")

pillar_counts = observations['pillar'].value_counts()

fig_pillar = go.Figure(data=[go.Pie(
    labels=pillar_counts.index,
    values=pillar_counts.values,
    hole=0.4,
    marker=dict(colors= ['#2E86AB', '#06A77D', '#F72585', '#F77F00'])
)])

fig_pillar.update_layout(
    title="Data Distribution Across Pillars",
    height=400
)

st.plotly_chart(fig_pillar, use_container_width=True)

# Data quality assessment
st.markdown("#### 🔍 Data Quality Assessment")

col1, col2 = st.columns(2)

with col1:
    # Confidence distribution
    confidence_dist = df['confidence'].value_counts()
    
    fig_confidence = px.bar(
        x=confidence_dist.index,
        y=confidence_dist.values,
        labels={'x': 'Confidence Level', 'y': 'Number of Records'},
        title="Data Confidence Distribution",
        color=confidence_dist.index,
        color_discrete_map={'high': '#06A77D', 'medium': '#F77F00', 'low': '#D62828'}
    )
    st.plotly_chart(fig_confidence, use_container_width=True)

with col2:
    # Source distribution
    source_dist = observations['source_name'].value_counts().head(5)
    
    fig_source = px.bar(
        x=source_dist.values,
        y=source_dist.index,
        labels={'x': 'Number of Records', 'y': 'Source'},
        title="Top 5 Data Sources",
        orientation='h',
        color_discrete_sequence=['#2E86AB']
    )
    st.plotly_chart(fig_source, use_container_width=True)

# ============================================================================
# 3. FORECASTS SECTION
# ============================================================================
st.markdown('<div class="sub-header">🔮 Forecasts & Projections</div>', unsafe_allow_html=True)

# Forecast visualization (Visualization 4)
st.markdown("#### 📊 Account Ownership Forecast 2025-2027")

fig_forecast = go.Figure()

# Historical data
fig_forecast.add_trace(go.Scatter(
    x=acc_ownership_sorted['observation_date'],
    y=acc_ownership_sorted['value_numeric'],
    mode='lines+markers',
    name='Historical',
    line=dict(color='#2E86AB', width=3),
    marker=dict(size=10)
))

# Forecast line
forecast_dates = pd.to_datetime([f"{year}-06-30" for year in forecast_df['Year']])
fig_forecast.add_trace(go.Scatter(
    x=forecast_dates,
    y=forecast_df['Forecast (%)'],
    mode='lines+markers',
    name='Forecast',
    line=dict(color='#06A77D', width=3, dash='dash'),
    marker=dict(size=10, symbol='square')
))

# 95% Confidence interval
fig_forecast.add_trace(go.Scatter(
    x=forecast_dates,
    y=forecast_df['Upper 95% CI'],
    mode='lines',
    name='95% CI Upper',
    line=dict(width=0),
    showlegend=False
))

fig_forecast.add_trace(go.Scatter(
    x=forecast_dates,
    y=forecast_df['Lower 95% CI'],
    mode='lines',
    name='95% Confidence Interval',
    fill='tonexty',
    fillcolor='rgba(6, 167, 125, 0.2)',
    line=dict(width=0)
))

# 80% Confidence interval
fig_forecast.add_trace(go.Scatter(
    x=forecast_dates,
    y=forecast_df['Upper 80% CI'],
    mode='lines',
    name='80% CI Upper',
    line=dict(width=0),
    showlegend=False
))

fig_forecast.add_trace(go.Scatter(
    x=forecast_dates,
    y=forecast_df['Lower 80% CI'],
    mode='lines',
    name='80% Confidence Interval',
    fill='tonexty',
    fillcolor='rgba(6, 167, 125, 0.4)',
    line=dict(width=0)
))

fig_forecast.update_layout(
    title="Account Ownership Forecast with Confidence Intervals",
    xaxis_title="Year",
    yaxis_title="Account Ownership (%)",
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_forecast, use_container_width=True)

# Forecast table
st.markdown("#### 📋 Detailed Forecast Table")
st.dataframe(forecast_df, use_container_width=True)

# ============================================================================
# 4. PROJECTIONS & SCENARIOS SECTION
# ============================================================================
st.markdown('<div class="sub-header">🎯 Scenario Analysis & Projections</div>', unsafe_allow_html=True)

# Scenario comparison (Visualization 5)
st.markdown("#### 🔄 Scenario Comparison")

fig_scenarios = go.Figure()

# Historical
fig_scenarios.add_trace(go.Scatter(
    x=acc_ownership_sorted['observation_date'],
    y=acc_ownership_sorted['value_numeric'],
    mode='lines+markers',
    name='Historical',
    line=dict(color='#2E86AB', width=3),
    marker=dict(size=8)
))

# Scenarios
scenario_dates = pd.to_datetime([f"{year}-06-30" for year in scenario_df['Year']])

fig_scenarios.add_trace(go.Scatter(
    x=scenario_dates,
    y=scenario_df['Base Case (%)'],
    mode='lines+markers',
    name='Base Case',
    line=dict(color='#06A77D', width=3, dash='dash'),
    marker=dict(size=10, symbol='square')
))

fig_scenarios.add_trace(go.Scatter(
    x=scenario_dates,
    y=scenario_df['Accelerated (%)'],
    mode='lines+markers',
    name='Accelerated Inclusion',
    line=dict(color='#F72585', width=2, dash='dot'),
    marker=dict(size=10, symbol='triangle-up')
))

fig_scenarios.add_trace(go.Scatter(
    x=scenario_dates,
    y=scenario_df['Stagnation (%)'],
    mode='lines+markers',
    name='Stagnation',
    line=dict(color='#D62828', width=2, dash='dot'),
    marker=dict(size=10, symbol='triangle-down')
))

fig_scenarios.update_layout(
    title="Scenario Analysis: Alternative Financial Inclusion Paths",
    xaxis_title="Year",
    yaxis_title="Account Ownership (%)",
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_scenarios, use_container_width=True)

# Scenario descriptions
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
    <strong>✅ Base Case</strong><br>
    <small>Current trajectory with moderate Fayda ID impact</small><br>
    <strong>2027:</strong> 60.5%
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
    <strong>🚀 Accelerated</strong><br>
    <small>Rapid digital ID adoption + new fintech licenses</small><br>
    <strong>2027:</strong> 66.5%
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
    <strong>⚠️ Stagnation</strong><br>
    <small>Regulatory delays + economic headwinds</small><br>
    <strong>2027:</strong> 55.7%
    </div>
    """, unsafe_allow_html=True)

# Scenario table
st.markdown("#### 📊 Scenario Comparison Table")
st.dataframe(scenario_df, use_container_width=True)

# ============================================================================
# INSIGHTS & RECOMMENDATIONS
# ============================================================================
st.markdown('<div class="sub-header">💡 Key Insights & Recommendations</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🔑 Key Drivers:**
    - **Fayda Digital ID (2024)**: +5-7pp expected impact
    - **Telebirr Saturation**: Growth moderating
    - **M-Pesa Competition**: Marginal access boost
    - **Baseline Trend**: +2.8% annual growth
    """)
    
    st.markdown("""
    **📊 Data Quality:**
    - Sparse historical data (18-24 month gaps)
    - High confidence in recent observations
    - Event clustering creates forecast uncertainty
    """)

with col2:
    st.markdown("""
    **🎯 Stakeholder Recommendations:**
    
    **For DFIs:**
    - Ethiopia unlikely to reach 70% by 2027 without intervention
    - Focus on rural areas and women to amplify Fayda ID impact
    
    **For Mobile Operators:**
    - Shift from acquisition to usage deepening
    - Expected 4-6% absolute market gain 2025-2027
    
    **For National Bank:**
    - Monitor quarterly data to validate forecasts
    - Consider accelerated fintech licensing
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<small>
📊 Ethiopia Financial Inclusion Dashboard | Data: Global Findex, NBE, Enriched Analysis | 
Last Updated: February 2026
</small>
</div>
""", unsafe_allow_html=True)
