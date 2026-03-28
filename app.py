import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import folium
import streamlit as st
from sqlalchemy import create_engine
from urllib.parse import quote_plus

st.set_page_config(
    page_title="Loan Portfolio Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

MYSQL_USER = os.getenv("MYSQL_USER", "Sumit_Kumar_Garg")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "SuMKgT#02")
MYSQL_HOST = os.getenv("MYSQL_HOST", "192.168.93.20")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "dwh")
SQL_QUERY = os.getenv(
    "SQL_QUERY",
    "select * from `loan-portfolio-mapping-data-2 (1)`;",
)

DATA_URL = os.getenv("DATABASE_URL")
if not DATA_URL:
    password = quote_plus(MYSQL_PASSWORD)
    DATA_URL = (
        f"mysql+pymysql://{MYSQL_USER}:{password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

DATA_FILE = os.getenv("DATA_FILE", "Loan_portfolio.csv")
DATA_PATH = Path(__file__).parent / DATA_FILE

@st.cache_data(ttl=600)
def load_data_from_csv(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def build_database_url(user: str, password: str, host: str, port: str, db_name: str) -> str:
    return f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:{port}/{db_name}"


def test_db_connection(database_url: str) -> tuple[bool, str]:
    try:
        engine = create_engine(
            database_url,
            connect_args={"connect_timeout": 5},
            pool_pre_ping=True,
        )
        with engine.connect() as connection:
            pass
        return True, "Connection succeeded."
    except Exception as exc:
        return False, str(exc)


@st.cache_data(ttl=600)
def load_data_from_sql(database_url: str, query: str) -> pd.DataFrame:
    engine = create_engine(
        database_url,
        connect_args={"connect_timeout": 10},
        pool_pre_ping=True,
    )
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)


def create_map(df: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=[22.5, 78.9], zoom_start=5, control_scale=True)

    def risk_color(dpd: float) -> str:
        if pd.isna(dpd):
            return "gray"
        if dpd == 0:
            return "green"
        if dpd <= 30:
            return "yellow"
        if dpd <= 60:
            return "orange"
        if dpd <= 90:
            return "red"
        return "darkred"

    def circle_radius(asset_value: float) -> float:
        if pd.isna(asset_value):
            return 4
        if asset_value <= 1_000_000:
            return 4
        if asset_value <= 2_000_000:
            return 6
        if asset_value <= 3_000_000:
            return 8
        return 10

    default_color = "blue"
    for _, row in df.iterrows():
        lat, lon = row.get("Latitude"), row.get("Longitude")
        if pd.isna(lat) or pd.isna(lon):
            continue

        folium.CircleMarker(
            location=[lat, lon],
            radius=circle_radius(row.get("Asset_Colleteral_Value", 0)),
            color=default_color,
            fill=True,
            fill_color=risk_color(row.get("DPD", 0)),
            fill_opacity=0.7,
            popup=(
                f"Branch: {row.get('Branch', 'NA')}<br>"
                f"Status: {row.get('Status', 'NA')}<br>"
                f"DPD: {row.get('DPD', 'NA')}<br>"
                f"Asset Value: {row.get('Asset_Colleteral_Value', 'NA')}"
            ),
        ).add_to(m)

    legend_html = '''
    <div style="position: fixed; bottom: 10px; left: 10px; width: 220px; height: 140px;
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                padding: 10px;">
      <b>DPD Risk Level</b><br>
      <span style="color:green;">●</span> 0 DPD<br>
      <span style="color:yellow;">●</span> 1–30 DPD<br>
      <span style="color:orange;">●</span> 31–60 DPD<br>
      <span style="color:red;">●</span> 61–90 DPD<br>
      <span style="color:darkred;">●</span> 90+ DPD
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


def main():
    st.title("Loan Portfolio Map Dashboard")
    st.markdown(
        "This dashboard loads loan portfolio data, renders a branch risk map, and auto-refreshes every 10 minutes. "
        "Share the deployed link with your team for office reporting."
    )

    refresh_script = "<script>setTimeout(()=>window.location.reload(), 600000);</script>"
    st.components.v1.html(refresh_script, height=0)

    with st.sidebar.expander("Database connection"):
        host = st.text_input("MySQL host", value=MYSQL_HOST)
        port = st.text_input("MySQL port", value=MYSQL_PORT)
        user = st.text_input("MySQL user", value=MYSQL_USER)
        password = st.text_input("MySQL password", value=MYSQL_PASSWORD, type="password")
        database = st.text_input("MySQL database", value=MYSQL_DB)
        query = st.text_area("SQL query", value=SQL_QUERY, height=120)
        connection_url = build_database_url(user, password, host, port, database)

        if st.button("Test connection"):
            ok, message = test_db_connection(connection_url)
            if ok:
                st.success(message)
            else:
                st.error(message)

    try:
        df = load_data_from_sql(connection_url, query)
        st.sidebar.success("Loaded data from SQL source.")
    except Exception as exc:
        st.sidebar.error("SQL load failed. Check the SQL settings above.")
        st.sidebar.exception(exc)
        st.warning(
            "Unable to connect to the SQL server from this host. "
            "If this is a local test machine, you can place `Loan_portfolio.csv` in the app folder or upload a CSV file now."
        )
        if DATA_PATH.exists():
            df = load_data_from_csv(DATA_PATH)
            st.info(f"Loaded fallback CSV from {DATA_PATH}.")
        else:
            uploaded_file = st.file_uploader("Upload loan portfolio CSV", type=["csv"])
            if uploaded_file is None:
                st.stop()
            df = pd.read_csv(uploaded_file)

    SQL_QUERY = query
    DATA_URL = connection_url

    df.columns = df.columns.str.strip()

    df.columns = df.columns.str.strip()

    with st.sidebar:
        st.header("Filters")
        st.caption("Data will load from SQL using DATABASE_URL and SQL_QUERY.")

        state_filter = st.multiselect(
            "Select State", options=sorted(df["State"].dropna().unique()),
            default=sorted(df["State"].dropna().unique())
        )
        area_filter = st.multiselect(
            "Select Area", options=sorted(df["Area"].dropna().unique()),
            default=sorted(df["Area"].dropna().unique())
        )
        branch_filter = st.multiselect(
            "Select Branch", options=sorted(df["Branch"].dropna().unique()),
            default=sorted(df["Branch"].dropna().unique())
        )
        status_filter = st.multiselect(
            "Select Status", options=sorted(df["Status"].dropna().unique()),
            default=sorted(df["Status"].dropna().unique())
        )

        dpd_min, dpd_max = int(df["DPD"].min()), int(df["DPD"].max())
        dpd_range = st.slider(
            "Select DPD Range", min_value=dpd_min, max_value=dpd_max,
            value=(dpd_min, dpd_max)
        )

        asset_min = int(df["Asset_Colleteral_Value"].min())
        asset_max = int(df["Asset_Colleteral_Value"].max())
        asset_range = st.slider(
            "Select Asset Collateral Value", min_value=asset_min, max_value=asset_max,
            value=(asset_min, asset_max)
        )

    filtered_df = df[
        df["State"].isin(state_filter)
        & df["Area"].isin(area_filter)
        & df["Branch"].isin(branch_filter)
        & df["Status"].isin(status_filter)
        & df["DPD"].between(dpd_range[0], dpd_range[1], inclusive="both")
        & df["Asset_Colleteral_Value"].between(asset_range[0], asset_range[1], inclusive="both")
    ]

    st.markdown(
        f"**Records loaded:** {len(df):,} &nbsp;&nbsp;|&nbsp;&nbsp; **Records shown:** {len(filtered_df):,}"
    )
    st.markdown(f"**Last refresh:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (auto-refresh every 10 min)")

    if filtered_df.empty:
        st.warning("No records match the selected filters.")
        st.stop()

    folium_map = create_map(filtered_df)
    map_html = folium_map._repr_html_()
    st.components.v1.html(map_html, height=700)

    with st.expander("Download filtered data"):
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="filtered_loan_portfolio.csv")


if __name__ == "__main__":
    main()
