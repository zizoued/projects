"""
GDP Growth Year-over-Year Analysis for Major World Economies

This script analyzes GDP growth rates for the world's major economies
using data from the World Bank's World Development Indicators database.

Author: Data Analysis Project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import wbgapi as wb
import os
from datetime import datetime

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Major economies by GDP (ISO 3166-1 alpha-3 codes)
MAJOR_ECONOMIES = {
    'USA': 'United States',
    'CHN': 'China',
    'JPN': 'Japan',
    'DEU': 'Germany',
    'IND': 'India',
    'GBR': 'United Kingdom',
    'FRA': 'France',
    'BRA': 'Brazil',
    'ITA': 'Italy',
    'CAN': 'Canada'
}

# World Bank indicator for GDP growth (annual %)
GDP_GROWTH_INDICATOR = 'NY.GDP.MKTP.KD.ZG'

# Analysis period
START_YEAR = 2000
END_YEAR = 2023


def fetch_gdp_data():
    """
    Fetch GDP growth data from World Bank API.
    
    Returns:
        pd.DataFrame: DataFrame with GDP growth data for major economies
    """
    print("Fetching GDP growth data from World Bank...")
    
    try:
        # Fetch data using World Bank API
        data = wb.data.DataFrame(
            GDP_GROWTH_INDICATOR,
            economy=list(MAJOR_ECONOMIES.keys()),
            time=range(START_YEAR, END_YEAR + 1)
        )
        
        # Transpose and clean data
        df = data.T
        df.index = df.index.astype(str).str.replace('YR', '').astype(int)
        df.index.name = 'Year'
        
        # Rename columns to country names
        df.columns = [MAJOR_ECONOMIES.get(col, col) for col in df.columns]
        
        print(f"Successfully fetched data for {len(df.columns)} economies, {len(df)} years")
        return df
        
    except Exception as e:
        print(f"Error fetching data from World Bank: {e}")
        print("Using sample data for demonstration...")
        return create_sample_data()


def create_sample_data():
    """
    Create sample GDP growth data for demonstration purposes.
    Based on actual historical patterns from major economies.
    
    Returns:
        pd.DataFrame: Sample GDP growth data
    """
    np.random.seed(42)
    years = range(START_YEAR, END_YEAR + 1)
    
    # Base growth patterns for each economy (approximated from real data)
    base_patterns = {
        'United States': {'mean': 2.3, 'std': 2.0, 'crisis_impact': -3.5},
        'China': {'mean': 8.5, 'std': 2.5, 'crisis_impact': -1.5},
        'Japan': {'mean': 1.0, 'std': 2.0, 'crisis_impact': -4.0},
        'Germany': {'mean': 1.5, 'std': 2.5, 'crisis_impact': -4.5},
        'India': {'mean': 6.5, 'std': 2.5, 'crisis_impact': -2.0},
        'United Kingdom': {'mean': 2.0, 'std': 2.0, 'crisis_impact': -4.0},
        'France': {'mean': 1.5, 'std': 2.0, 'crisis_impact': -3.0},
        'Brazil': {'mean': 2.5, 'std': 3.0, 'crisis_impact': -4.0},
        'Italy': {'mean': 0.5, 'std': 2.0, 'crisis_impact': -5.0},
        'Canada': {'mean': 2.2, 'std': 2.0, 'crisis_impact': -3.0}
    }
    
    data = {}
    for country, params in base_patterns.items():
        growth_rates = []
        for year in years:
            # Base growth with random variation
            rate = params['mean'] + np.random.normal(0, params['std'] * 0.5)
            
            # Add crisis impacts
            if year == 2008:  # Global Financial Crisis beginning
                rate = rate + params['crisis_impact'] * 0.3
            elif year == 2009:  # GFC peak impact
                rate = params['crisis_impact']
            elif year == 2020:  # COVID-19 pandemic
                rate = params['crisis_impact'] * 1.5
            elif year == 2021:  # Recovery bounce
                rate = params['mean'] * 2 + np.random.normal(0, 1)
            elif year == 2022:  # Post-pandemic normalization
                rate = params['mean'] * 1.2 + np.random.normal(0, 0.5)
                
            growth_rates.append(round(rate, 2))
        
        data[country] = growth_rates
    
    df = pd.DataFrame(data, index=list(years))
    df.index.name = 'Year'
    return df


def calculate_statistics(df):
    """
    Calculate summary statistics for GDP growth data.
    
    Args:
        df: DataFrame with GDP growth data
        
    Returns:
        pd.DataFrame: Summary statistics for each economy
    """
    stats = pd.DataFrame({
        'Average Growth (%)': df.mean().round(2),
        'Median Growth (%)': df.median().round(2),
        'Std Deviation': df.std().round(2),
        'Max Growth (%)': df.max().round(2),
        'Min Growth (%)': df.min().round(2),
        'Best Year': df.idxmax(),
        'Worst Year': df.idxmin(),
        'Positive Years': (df > 0).sum(),
        'Negative Years': (df < 0).sum()
    })
    
    return stats.sort_values('Average Growth (%)', ascending=False)


def analyze_correlations(df):
    """
    Analyze correlations between economies' growth rates.
    
    Args:
        df: DataFrame with GDP growth data
        
    Returns:
        pd.DataFrame: Correlation matrix
    """
    return df.corr().round(3)


def plot_gdp_growth_comparison(df):
    """
    Create line chart comparing GDP growth across economies.
    
    Args:
        df: DataFrame with GDP growth data
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Color palette for distinguishing economies
    colors = plt.cm.tab10(np.linspace(0, 1, len(df.columns)))
    
    for i, country in enumerate(df.columns):
        ax.plot(df.index, df[country], label=country, 
                linewidth=2, marker='o', markersize=4, color=colors[i])
    
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.axvspan(2008, 2009.5, alpha=0.2, color='red', label='2008-09 Crisis')
    ax.axvspan(2020, 2020.5, alpha=0.2, color='orange', label='COVID-19')
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('GDP Growth Rate (%)', fontsize=12)
    ax.set_title('GDP Growth Year-over-Year Comparison\nMajor World Economies (2000-2023)', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(df.index.min() - 0.5, df.index.max() + 0.5)
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'gdp_growth_comparison.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def plot_gdp_heatmap(df):
    """
    Create heatmap of GDP growth patterns.
    
    Args:
        df: DataFrame with GDP growth data
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create heatmap
    sns.heatmap(df.T, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                ax=ax, cbar_kws={'label': 'GDP Growth (%)'})
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Economy', fontsize=12)
    ax.set_title('GDP Growth Heatmap by Economy and Year\n(Green = Growth, Red = Contraction)', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'gdp_growth_heatmap.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def plot_average_growth_bar(stats):
    """
    Create bar chart of average GDP growth.
    
    Args:
        stats: DataFrame with summary statistics
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['green' if x > 0 else 'red' for x in stats['Average Growth (%)']]
    bars = ax.barh(stats.index, stats['Average Growth (%)'], color=colors, alpha=0.7)
    
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.set_xlabel('Average GDP Growth (%)', fontsize=12)
    ax.set_ylabel('Economy', fontsize=12)
    ax.set_title(f'Average Annual GDP Growth Rate ({START_YEAR}-{END_YEAR})', 
                 fontsize=14, fontweight='bold')
    
    # Add value labels
    for bar, value in zip(bars, stats['Average Growth (%)']):
        ax.annotate(f'{value:.1f}%', 
                   xy=(value, bar.get_y() + bar.get_height()/2),
                   xytext=(5 if value >= 0 else -30, 0), 
                   textcoords='offset points',
                   ha='left' if value >= 0 else 'right', va='center', fontsize=10)
    
    ax.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'average_growth_comparison.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def plot_volatility_scatter(stats):
    """
    Create scatter plot of growth vs volatility.
    
    Args:
        stats: DataFrame with summary statistics
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    x = stats['Average Growth (%)']
    y = stats['Std Deviation']
    
    scatter = ax.scatter(x, y, s=200, c=x, cmap='RdYlGn', alpha=0.7, edgecolor='black')
    
    # Add country labels
    for i, country in enumerate(stats.index):
        ax.annotate(country, (x.iloc[i], y.iloc[i]), 
                   textcoords='offset points', xytext=(0, 10),
                   ha='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Average GDP Growth (%)', fontsize=12)
    ax.set_ylabel('Growth Volatility (Std Dev)', fontsize=12)
    ax.set_title('Growth Performance vs Volatility Trade-off\nMajor World Economies', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.colorbar(scatter, label='Average Growth (%)')
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'growth_volatility_scatter.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def print_analysis_report(df, stats, correlations):
    """
    Print comprehensive analysis report to console.
    
    Args:
        df: DataFrame with GDP growth data
        stats: DataFrame with summary statistics
        correlations: Correlation matrix
    """
    print("\n" + "="*80)
    print("GDP GROWTH YEAR-OVER-YEAR ANALYSIS REPORT")
    print(f"Major World Economies ({START_YEAR}-{END_YEAR})")
    print("="*80)
    
    print("\n📊 SUMMARY STATISTICS")
    print("-"*80)
    print(stats.to_string())
    
    print("\n\n🏆 KEY FINDINGS")
    print("-"*80)
    
    # Top performers
    top_growers = stats.nlargest(3, 'Average Growth (%)')
    print("\n1. HIGHEST AVERAGE GROWTH:")
    for i, (country, row) in enumerate(top_growers.iterrows(), 1):
        print(f"   {i}. {country}: {row['Average Growth (%)']}% average annual growth")
    
    # Most volatile
    most_volatile = stats.nlargest(3, 'Std Deviation')
    print("\n2. MOST VOLATILE ECONOMIES:")
    for i, (country, row) in enumerate(most_volatile.iterrows(), 1):
        print(f"   {i}. {country}: {row['Std Deviation']} std deviation")
    
    # Crisis impact analysis
    print("\n3. CRISIS IMPACT ANALYSIS:")
    if 2009 in df.index:
        print(f"   2009 (Global Financial Crisis):")
        crisis_2009 = df.loc[2009].sort_values()
        for country in crisis_2009.index[:3]:
            print(f"      - {country}: {crisis_2009[country]:.1f}%")
    
    if 2020 in df.index:
        print(f"\n   2020 (COVID-19 Pandemic):")
        crisis_2020 = df.loc[2020].sort_values()
        for country in crisis_2020.index[:3]:
            print(f"      - {country}: {crisis_2020[country]:.1f}%")
    
    # Correlation insights
    print("\n4. CORRELATION INSIGHTS:")
    print("   Economies with highest correlation (move together):")
    corr_pairs = []
    for i, c1 in enumerate(correlations.columns):
        for c2 in correlations.columns[i+1:]:
            corr_pairs.append((c1, c2, correlations.loc[c1, c2]))
    corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    for c1, c2, corr in corr_pairs[:5]:
        print(f"      - {c1} & {c2}: {corr:.3f}")
    
    print("\n\n📈 YEAR-BY-YEAR DATA")
    print("-"*80)
    print(df.round(2).to_string())
    
    print("\n" + "="*80)
    print("Analysis complete. Visualizations saved to output/ directory.")
    print("="*80 + "\n")


def main():
    """Main function to run the GDP growth analysis."""
    print("="*80)
    print("GDP GROWTH YEAR-OVER-YEAR ANALYSIS")
    print("Analyzing major world economies")
    print("="*80 + "\n")
    
    # Step 1: Fetch data
    df = fetch_gdp_data()
    
    # Step 2: Calculate statistics
    print("\nCalculating summary statistics...")
    stats = calculate_statistics(df)
    
    # Step 3: Analyze correlations
    print("Analyzing inter-economy correlations...")
    correlations = analyze_correlations(df)
    
    # Step 4: Generate visualizations
    print("\nGenerating visualizations...")
    plot_gdp_growth_comparison(df)
    plot_gdp_heatmap(df)
    plot_average_growth_bar(stats)
    plot_volatility_scatter(stats)
    
    # Step 5: Save data to CSV
    csv_path = os.path.join(OUTPUT_DIR, 'gdp_statistics.csv')
    stats.to_csv(csv_path)
    print(f"Saved: {csv_path}")
    
    data_csv_path = os.path.join(OUTPUT_DIR, 'gdp_growth_data.csv')
    df.to_csv(data_csv_path)
    print(f"Saved: {data_csv_path}")
    
    # Step 6: Print analysis report
    print_analysis_report(df, stats, correlations)
    
    return df, stats, correlations


if __name__ == "__main__":
    main()
