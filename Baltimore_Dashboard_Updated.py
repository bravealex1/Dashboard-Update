"""
Baltimore Dashboard - Updated Version with Expanded Data
Integrates 91 indicators (35 health + 56 economic) at tract level

Author: Alex & Yiyang
Date: 2026-02-16
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page config
st.set_page_config(
    page_title="Baltimore City Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: #f7fafc;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the expanded integrated dataset."""
    try:
        df = pd.read_csv("data/integrated/baltimore_integrated_expanded_2022.csv")
        return df
    except:
        st.error("⚠️ Data file not found. Please ensure baltimore_integrated_expanded_2022.csv is in data/integrated/")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🏙️ Baltimore City Health & Economic Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("**Comprehensive tract-level health and economic indicators for Baltimore City**")
    st.markdown("---")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Controls")
    st.sidebar.markdown("---")
    
    # View selection
    view_mode = st.sidebar.radio(
        "Select View",
        ["🗺️ City Overview", "🔍 Neighborhood Explorer", "📈 Indicator Analysis", "ℹ️ About"]
    )
    
    if view_mode == "🗺️ City Overview":
        show_city_overview(df)
    elif view_mode == "🔍 Neighborhood Explorer":
        show_neighborhood_explorer(df)
    elif view_mode == "📈 Indicator Analysis":
        show_indicator_analysis(df)
    else:
        show_about()

def show_city_overview(df):
    """Show city-level overview with key metrics."""
    st.header("🗺️ City Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Census Tracts",
            f"{len(df):,}",
            help="Total number of census tracts in Baltimore City"
        )
    
    with col2:
        avg_poverty = df['poverty_rate'].mean()
        st.metric(
            "Avg Poverty Rate",
            f"{avg_poverty:.1f}%",
            help="Average poverty rate across all tracts"
        )
    
    with col3:
        avg_unemployment = df['unemployment_rate'].mean()
        st.metric(
            "Avg Unemployment",
            f"{avg_unemployment:.1f}%",
            help="Average unemployment rate across all tracts"
        )
    
    with col4:
        median_income = df['median_household_income_econ'].median()
        st.metric(
            "Median Income",
            f"${median_income:,.0f}",
            help="Median household income across all tracts"
        )
    
    st.markdown("---")
    
    # Indicator selection
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Select Indicator")
        
        indicator_categories = {
            "Economic": {
                'poverty_rate': 'Poverty Rate (%)',
                'unemployment_rate': 'Unemployment Rate (%)',
                'median_household_income_econ': 'Median Household Income ($)',
                'gini_index': 'Gini Index (Income Inequality)',
                'snap_participation_rate': 'SNAP Participation Rate (%)',
                'housing_cost_burden_rate': 'Housing Cost Burden Rate (%)',
            },
            "Health": {
                'uninsured_rate': 'Uninsured Rate (%)',
                'disability_rate': 'Disability Rate (%)',
            },
            "Education": {
                'college_degree_rate': 'College Degree Rate (%)',
            }
        }
        
        category = st.selectbox("Category", list(indicator_categories.keys()))
        indicator = st.selectbox("Indicator", list(indicator_categories[category].keys()), 
                                format_func=lambda x: indicator_categories[category][x])
        
        # Statistics
        st.markdown("### Statistics")
        values = df[indicator].dropna()
        st.write(f"**Min:** {values.min():.2f}")
        st.write(f"**Median:** {values.median():.2f}")
        st.write(f"**Max:** {values.max():.2f}")
        st.write(f"**Std Dev:** {values.std():.2f}")
    
    with col2:
        st.subheader(f"Distribution: {indicator_categories[category][indicator]}")
        
        # Create histogram
        fig = px.histogram(
            df,
            x=indicator,
            nbins=30,
            title=f"Distribution of {indicator_categories[category][indicator]}",
            labels={indicator: indicator_categories[category][indicator]},
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Box plot
        fig2 = px.box(
            df,
            y=indicator,
            title=f"Box Plot: {indicator_categories[category][indicator]}",
            labels={indicator: indicator_categories[category][indicator]},
            color_discrete_sequence=['#764ba2']
        )
        fig2.update_layout(
            showlegend=False,
            height=300,
            plot_bgcolor='white'
        )
        st.plotly_chart(fig2, use_container_width=True)

def show_neighborhood_explorer(df):
    """Show neighborhood-level drill-down."""
    st.header("🔍 Neighborhood Explorer")
    
    # Prepare tract selection
    df['tract_str'] = df['tract'].astype(str).str.zfill(6)
    df['tract_display'] = 'Tract ' + df['tract_str']
    
    # Select tract
    selected_tract = st.selectbox(
        "Select Census Tract",
        df['tract_display'].tolist(),
        help="Choose a census tract to view detailed information"
    )
    
    tract_data = df[df['tract_display'] == selected_tract].iloc[0]
    
    st.markdown("---")
    
    # Key indicators
    st.subheader("📊 Key Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        poverty = tract_data['poverty_rate']
        city_avg = df['poverty_rate'].mean()
        delta = poverty - city_avg
        st.metric(
            "Poverty Rate",
            f"{poverty:.1f}%",
            f"{delta:+.1f}% vs city avg",
            delta_color="inverse"
        )
    
    with col2:
        unemployment = tract_data['unemployment_rate']
        city_avg = df['unemployment_rate'].mean()
        delta = unemployment - city_avg
        st.metric(
            "Unemployment Rate",
            f"{unemployment:.1f}%",
            f"{delta:+.1f}% vs city avg",
            delta_color="inverse"
        )
    
    with col3:
        income = tract_data['median_household_income_econ']
        city_avg = df['median_household_income_econ'].median()
        delta = income - city_avg
        st.metric(
            "Median Income",
            f"${income:,.0f}",
            f"${delta:+,.0f} vs city median"
        )
    
    with col4:
        gini = tract_data['gini_index']
        city_avg = df['gini_index'].mean()
        delta = gini - city_avg
        st.metric(
            "Gini Index",
            f"{gini:.3f}",
            f"{delta:+.3f} vs city avg",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Detailed metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Housing & Economic")
        
        metrics = [
            ('housing_cost_burden_rate', 'Housing Cost Burden', '%'),
            ('snap_participation_rate', 'SNAP Participation', '%'),
            ('public_assistance_rate', 'Public Assistance', '%'),
            ('home_ownership_rate', 'Home Ownership', '%'),
            ('vacancy_rate', 'Vacancy Rate', '%'),
        ]
        
        for key, label, unit in metrics:
            if key in tract_data.index and pd.notna(tract_data[key]):
                value = tract_data[key]
                city_avg = df[key].mean()
                diff_pct = ((value - city_avg) / city_avg * 100) if city_avg != 0 else 0
                
                st.write(f"**{label}:** {value:.1f}{unit}")
                st.progress(min(value / 100, 1.0) if unit == '%' else 0.5)
                st.caption(f"{diff_pct:+.1f}% vs city average")
                st.markdown("")
    
    with col2:
        st.subheader("🏥 Health & Education")
        
        metrics = [
            ('uninsured_rate', 'Uninsured Rate', '%'),
            ('disability_rate', 'Disability Rate', '%'),
            ('college_degree_rate', 'College Degree Rate', '%'),
            ('long_commute_rate', 'Long Commute Rate (60+ min)', '%'),
        ]
        
        for key, label, unit in metrics:
            if key in tract_data.index and pd.notna(tract_data[key]):
                value = tract_data[key]
                city_avg = df[key].mean()
                diff_pct = ((value - city_avg) / city_avg * 100) if city_avg != 0 else 0
                
                st.write(f"**{label}:** {value:.1f}{unit}")
                st.progress(min(value / 100, 1.0) if unit == '%' else 0.5)
                st.caption(f"{diff_pct:+.1f}% vs city average")
                st.markdown("")
    
    # Comparison radar chart
    st.markdown("---")
    st.subheader("📈 Neighborhood vs City Average")
    
    comparison_indicators = [
        'poverty_rate',
        'unemployment_rate',
        'snap_participation_rate',
        'housing_cost_burden_rate',
        'uninsured_rate',
        'college_degree_rate'
    ]
    
    tract_values = []
    city_values = []
    labels = []
    
    for ind in comparison_indicators:
        if ind in tract_data.index and pd.notna(tract_data[ind]):
            tract_val = tract_data[ind]
            city_val = df[ind].mean()
            
            # Normalize to percentage of city average
            normalized = (tract_val / city_val * 100) if city_val != 0 else 100
            
            tract_values.append(normalized)
            city_values.append(100)
            labels.append(ind.replace('_', ' ').title())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=tract_values,
        theta=labels,
        fill='toself',
        name=selected_tract,
        line_color='#667eea'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=city_values,
        theta=labels,
        fill='toself',
        name='City Average (100%)',
        line_color='#764ba2',
        line_dash='dash'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 150])),
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_indicator_analysis(df):
    """Show indicator analysis and correlations."""
    st.header("📈 Indicator Analysis")
    
    st.markdown("### Correlation Analysis")
    
    # Select indicators
    col1, col2 = st.columns(2)
    
    with col1:
        indicators_x = {
            'poverty_rate': 'Poverty Rate',
            'unemployment_rate': 'Unemployment Rate',
            'median_household_income_econ': 'Median Income',
            'gini_index': 'Gini Index',
            'snap_participation_rate': 'SNAP Participation',
        }
        x_var = st.selectbox("X-axis", list(indicators_x.keys()), 
                            format_func=lambda x: indicators_x[x])
    
    with col2:
        indicators_y = {
            'uninsured_rate': 'Uninsured Rate',
            'disability_rate': 'Disability Rate',
            'college_degree_rate': 'College Degree Rate',
            'housing_cost_burden_rate': 'Housing Cost Burden',
            'vacancy_rate': 'Vacancy Rate',
        }
        y_var = st.selectbox("Y-axis", list(indicators_y.keys()), 
                            format_func=lambda x: indicators_y[x])
    
    # Scatter plot
    fig = px.scatter(
        df,
        x=x_var,
        y=y_var,
        title=f"{indicators_x[x_var]} vs {indicators_y[y_var]}",
        labels={
            x_var: indicators_x[x_var],
            y_var: indicators_y[y_var]
        },
        trendline="ols",
        color_discrete_sequence=['#667eea']
    )
    
    fig.update_layout(
        height=600,
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation coefficient
    corr = df[[x_var, y_var]].corr().iloc[0, 1]
    st.metric("Correlation Coefficient", f"{corr:.3f}")
    
    if abs(corr) > 0.7:
        st.success("🔵 Strong correlation")
    elif abs(corr) > 0.4:
        st.info("🟡 Moderate correlation")
    else:
        st.warning("⚪ Weak correlation")

def show_about():
    """Show about page."""
    st.header("ℹ️ About This Dashboard")
    
    st.markdown("""
    ### Baltimore City Health & Economic Dashboard
    
    This dashboard provides comprehensive tract-level health and economic indicators for Baltimore City.
    
    **Data Coverage:**
    - 📍 **199 census tracts** in Baltimore City
    - 📊 **91 indicators** (35 health + 56 economic)
    - 📅 **Data year:** 2022 (ACS 5-year estimates)
    
    **Data Sources:**
    - U.S. Census Bureau - American Community Survey (ACS)
    - City Health Dashboard (NYU Langone Health)
    
    **Key Features:**
    - ✅ Tract-level precision (1,000-8,000 residents per tract)
    - ✅ Integrated health and economic data
    - ✅ Interactive visualizations
    - ✅ Neighborhood drill-down capability
    
    **Indicators Include:**
    - **Economic:** Poverty, unemployment, income, housing costs, SNAP participation, Gini index
    - **Health:** Insurance coverage, disability rates
    - **Education:** College degree attainment
    - **Housing:** Homeownership, vacancy, cost burden
    - **Transportation:** Commute patterns
    
    **Project Team:**
    - Alex
    - Yiyang
    - Adler (Project Lead)
    
    **Last Updated:** February 16, 2026
    
    ---
    
    ### How to Use
    
    1. **City Overview:** View city-wide distributions and statistics
    2. **Neighborhood Explorer:** Drill down into specific census tracts
    3. **Indicator Analysis:** Explore correlations between indicators
    
    ### Data Quality
    
    - **Completeness:** 95.6% of data cells have valid values
    - **Validation:** Cross-checked with Baltimore City Open Data
    - **Methodology:** Follows NYU City Health Dashboard standards
    
    ### Citation
    
    If you use this dashboard or data, please cite:
    
    > Alex, Yiyang, & Adler. (2026). Baltimore City Health & Economic Dashboard: 
    > Integrating Tract-Level Health and Economic Indicators. Baltimore, MD.
    
    ---
    
    **GitHub:** [Repository Link]  
    **Contact:** [Email]
    """)

if __name__ == "__main__":
    main()
