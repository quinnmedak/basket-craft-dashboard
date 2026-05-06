# Streamlit + Snowflake Dashboard — Design Spec

**Date:** 2026-05-06  
**Project:** basket-craft-dashboard

---

## Overview

A minimal Streamlit dashboard that connects to the `BASKET_CRAFT_PIPELINE` Snowflake database, runs a connection smoke test, and displays the result. Foundation for future data views.

---

## Environment

- Python 3.14 with a `.venv` virtual environment in the project root
- Dependencies tracked in `requirements.txt`
- `.venv` is already gitignored

**`requirements.txt`:**
```
streamlit
snowflake-connector-python
python-dotenv
```

---

## Credentials

Loaded from `.env` at runtime via `python-dotenv`. Never hardcoded.

| Variable | Purpose |
|---|---|
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier |
| `SNOWFLAKE_USER` | Login username |
| `SNOWFLAKE_PASSWORD` | Login password |
| `SNOWFLAKE_DATABASE` | Target database (`BASKET_CRAFT_PIPELINE`) |
| `SNOWFLAKE_WAREHOUSE` | Compute warehouse (`COMPUTE_WH`) |

`.env` is already gitignored.

---

## `app.py` Structure

1. Load `.env` with `python-dotenv`
2. Display page title: `"Basket Craft Dashboard"`
3. Open a cached Snowflake connection (`@st.cache_resource`) — created once per session
4. Run a cached smoke-test query (`@st.cache_data(ttl=600)`):
   ```sql
   SELECT CURRENT_DATABASE(), CURRENT_USER(), CURRENT_WAREHOUSE()
   ```
5. Display result in `st.dataframe`

---

## Caching Strategy

| Layer | Decorator | Scope |
|---|---|---|
| Connection object | `@st.cache_resource` | Shared across all users/sessions |
| Query result | `@st.cache_data(ttl=600)` | Re-fetched every 10 minutes |

---

## Error Handling

Wrap the connection and query in a `try/except`; surface errors via `st.error()` so the app fails gracefully rather than crashing.

---

## Out of Scope

- Authentication beyond env-var credentials
- Any specific dimension table queries (added later once schema is confirmed)
- Deployment / secrets management beyond `.env`
