# Basket Craft Merchandising

**Live app:** https://basket-craft.streamlit.app/

A Streamlit dashboard connected to the Basket Craft Snowflake data warehouse. Built for the merchandising team to monitor sales performance and identify bundle opportunities.

## Features

- **Headline Metrics** — Total revenue, orders, average order value, and items sold for the most recent month, each with month-over-month change
- **Revenue Trend** — Monthly revenue line chart filterable by date range
- **Top Products by Revenue** — Bar chart of product revenue within the selected date range
- **Bundle Finder** — Pick a product and see which other products appear most often in the same orders, with CSV export

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.streamlit/secrets.toml` with your Snowflake credentials:

```toml
SNOWFLAKE_ACCOUNT = "..."
SNOWFLAKE_USER = "..."
SNOWFLAKE_PASSWORD = "..."
SNOWFLAKE_DATABASE = "BASKET_CRAFT"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
```

Then run:

```bash
streamlit run app.py
```
