# GDP Growth YoY Analysis for Major Economies

This project analyzes Year-over-Year (YoY) GDP growth rates for the world's major economies using data from the World Bank.

## Major Economies Covered

The analysis covers the following economies (by GDP size):
- **United States (USA)** - World's largest economy
- **China (CHN)** - Second largest economy
- **Japan (JPN)** - Third largest economy
- **Germany (DEU)** - Largest European economy
- **India (IND)** - Fastest growing major economy
- **United Kingdom (GBR)** - Major financial center
- **France (FRA)** - Second largest European economy
- **Brazil (BRA)** - Largest Latin American economy
- **Italy (ITA)** - Third largest Eurozone economy
- **Canada (CAN)** - Major G7 economy

## Data Source

Data is sourced from the World Bank's World Development Indicators (WDI) database using the `wbgapi` Python library.

**Indicator Used:** 
- `NY.GDP.MKTP.KD.ZG` - GDP growth (annual %)

## Project Structure

```
gdp-analysis/
├── README.md           # This documentation file
├── requirements.txt    # Python dependencies
├── gdp_analysis.py     # Main analysis script
└── output/            # Generated visualizations and reports
```

## Installation

```bash
cd gdp-analysis
pip install -r requirements.txt
```

## Usage

Run the analysis:
```bash
python gdp_analysis.py
```

This will:
1. Fetch GDP growth data from the World Bank
2. Calculate YoY growth statistics
3. Generate comparative analysis
4. Create visualizations
5. Output summary statistics

## Key Metrics Analyzed

1. **Annual GDP Growth Rate (%)** - Year-over-Year percentage change
2. **Average Growth Rate** - Mean growth over the analysis period
3. **Growth Volatility** - Standard deviation of growth rates
4. **Peak/Trough Analysis** - Highest and lowest growth periods
5. **Comparative Rankings** - Economy performance comparisons

## Output

The analysis generates the following files in the `output/` directory:

**Visualizations:**
- `gdp_growth_comparison.png` - Line chart comparing GDP growth across economies
- `gdp_growth_heatmap.png` - Heatmap showing growth patterns by year
- `average_growth_comparison.png` - Bar chart ranking economies by average growth
- `growth_volatility_scatter.png` - Scatter plot showing growth vs volatility trade-off

**Data Files:**
- `gdp_statistics.csv` - Summary statistics for each economy
- `gdp_growth_data.csv` - Year-by-year GDP growth data for all economies

**Console Output:**
- Comprehensive analysis report with key insights

## Key Economic Insights

The analysis helps understand:
- How different economies perform relative to each other
- Impact of global events (e.g., 2008 financial crisis, COVID-19)
- Growth patterns and economic cycles
- Emerging vs. developed economy dynamics

## License

This project is for educational and analytical purposes.
