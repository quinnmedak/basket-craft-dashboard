import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import snowflake.connector

load_dotenv()

st.title("Basket Craft Dashboard")


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    )


@st.cache_data(ttl=600)
def get_headline_metrics():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        WITH monthly AS (
            SELECT
                DATE_TRUNC('month', TO_TIMESTAMP_NTZ(CREATED_AT, 9)) AS order_month,
                COUNT(*)                    AS total_orders,
                SUM(PRICE_USD)              AS total_revenue,
                AVG(PRICE_USD)              AS avg_order_value,
                SUM(ITEMS_PURCHASED::INT)   AS total_items_sold
            FROM BASKET_CRAFT.RAW.ORDERS
            GROUP BY 1
        ),
        with_lag AS (
            SELECT
                order_month,
                total_revenue,
                total_orders,
                avg_order_value,
                total_items_sold,
                LAG(total_revenue)    OVER (ORDER BY order_month) AS prior_revenue,
                LAG(total_orders)     OVER (ORDER BY order_month) AS prior_orders,
                LAG(avg_order_value)  OVER (ORDER BY order_month) AS prior_aov,
                LAG(total_items_sold) OVER (ORDER BY order_month) AS prior_items
            FROM monthly
        )
        SELECT *
        FROM with_lag
        ORDER BY order_month DESC
        LIMIT 1
    """)
    return cur.fetchone()


@st.cache_data(ttl=3600)
def get_order_date_range():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            MIN(TO_TIMESTAMP_NTZ(CREATED_AT, 9))::DATE,
            MAX(TO_TIMESTAMP_NTZ(CREATED_AT, 9))::DATE
        FROM BASKET_CRAFT.RAW.ORDERS
    """)
    return cur.fetchone()


@st.cache_data(ttl=600)
def get_revenue_trend(start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            DATE_TRUNC('month', TO_TIMESTAMP_NTZ(CREATED_AT, 9))::DATE AS order_month,
            SUM(PRICE_USD) AS total_revenue
        FROM BASKET_CRAFT.RAW.ORDERS
        WHERE TO_TIMESTAMP_NTZ(CREATED_AT, 9)::DATE BETWEEN %s AND %s
        GROUP BY 1
        ORDER BY 1
    """, (start_date, end_date))
    rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["Month", "Revenue"])


def delta_pct(current, prior):
    if prior and prior != 0:
        return f"{((current - prior) / prior * 100):+.1f}%"
    return None


try:
    # --- Headline metrics ---
    row = get_headline_metrics()
    if row:
        month_label, revenue, orders, aov, items, p_revenue, p_orders, p_aov, p_items = row
        st.subheader(f"Headline Metrics — {month_label.strftime('%B %Y')}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue",    f"${revenue:,.2f}", delta_pct(revenue, p_revenue))
        c2.metric("Total Orders",     f"{orders:,}",      delta_pct(orders,  p_orders))
        c3.metric("Avg Order Value",  f"${aov:,.2f}",     delta_pct(aov,     p_aov))
        c4.metric("Total Items Sold", f"{items:,}",       delta_pct(items,   p_items))

    st.divider()

    # --- Revenue trend ---
    st.subheader("Revenue Trend")

    min_date, max_date = get_order_date_range()
    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = date_range
        df = get_revenue_trend(start, end)
        if not df.empty:
            st.line_chart(df.set_index("Month")["Revenue"], y_label="Revenue ($)")
        else:
            st.info("No orders in the selected range.")

except Exception as e:
    st.error(f"Failed to load data: {e}")
