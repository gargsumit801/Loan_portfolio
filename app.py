import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import folium
import streamlit as st

st.set_page_config(
    page_title="Loan Portfolio Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_CSV_PATH = os.getenv(
    "CSV_PATH",
    r"C:\Users\UHF5350\Downloads\Loan_portfolio.csv",
)

LOCAL_CSV_PATH = Path(__file__).parent / "Loan_portfolio.csv"
CSV_PATH = Path(DEFAULT_CSV_PATH)
if not CSV_PATH.exists() and LOCAL_CSV_PATH.exists():
    CSV_PATH = LOCAL_CSV_PATH


@st.cache_data(ttl=600)
def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    return df


def format_currency(value: float) -> str:
    return f"₹{value:,.0f}"


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


def create_map(df: pd.DataFrame) -> folium.Map:
    fallback_location = [22.5, 78.9]
    m = folium.Map(location=fallback_location, zoom_start=5, control_scale=True)

    for _, row in df.iterrows():
        lat, lon = row.get("Latitude"), row.get("Longitude")
        if pd.isna(lat) or pd.isna(lon):
            continue

        folium.CircleMarker(
            location=[lat, lon],
            radius=circle_radius(row.get("Asset_Colleteral_Value", 0)),
            color="black",
            fill=True,
            fill_color=risk_color(row.get("DPD", 0)),
            fill_opacity=0.7,
            popup=(
                f"<b>Branch:</b> {row.get('Branch', 'NA')}<br>"
                f"<b>Status:</b> {row.get('Status', 'NA')}<br>"
                f"<b>DPD:</b> {row.get('DPD', 'NA')}<br>"
                f"<b>Asset Value:</b> {row.get('Asset_Colleteral_Value', 'NA')}"
            ),
        ).add_to(m)

    legend_html = '''
    <div style="position: fixed; bottom: 10px; left: 10px; width: 220px; height: 150px;
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


def build_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    state_filter = st.sidebar.multiselect(
        "Select State",
        options=sorted(df["State"].dropna().unique()),
        default=sorted(df["State"].dropna().unique()),
    )
    area_filter = st.sidebar.multiselect(
        "Select Area",
        options=sorted(df["Area"].dropna().unique()),
        default=sorted(df["Area"].dropna().unique()),
    )
    branch_filter = st.sidebar.multiselect(
        "Select Branch",
        options=sorted(df["Branch"].dropna().unique()),
        default=sorted(df["Branch"].dropna().unique()),
    )
    status_filter = st.sidebar.multiselect(
        "Select Status",
        options=sorted(df["Status"].dropna().unique()),
        default=sorted(df["Status"].dropna().unique()),
    )

    dpd_min, dpd_max = int(df["DPD"].min()), int(df["DPD"].max())
    dpd_range = st.sidebar.slider(
        "DPD Range", min_value=dpd_min, max_value=dpd_max, value=(dpd_min, dpd_max)
    )

    asset_min = int(df["Asset_Colleteral_Value"].min())
    asset_max = int(df["Asset_Colleteral_Value"].max())
    asset_range = st.sidebar.slider(
        "Asset Collateral Value",
        min_value=asset_min,
        max_value=asset_max,
        value=(asset_min, asset_max),
    )

    filtered_df = df[
        df["State"].isin(state_filter)
        & df["Area"].isin(area_filter)
        & df["Branch"].isin(branch_filter)
        & df["Status"].isin(status_filter)
        & df["DPD"].between(dpd_range[0], dpd_range[1], inclusive="both")
        & df["Asset_Colleteral_Value"].between(asset_range[0], asset_range[1], inclusive="both")
    ]
    return filtered_df


def render_metrics(df: pd.DataFrame) -> None:
    total_loans = len(df)
    total_value = df["Asset_Colleteral_Value"].sum()
    avg_dpd = df["DPD"].mean()
    open_accounts = df[df["Status"] == "A"].shape[0] if "A" in df["Status"].unique() else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", f"{total_loans:,}")
    col2.metric("Total Asset Value", format_currency(total_value))
    col3.metric("Average DPD", f"{avg_dpd:.1f}")
    col4.metric("Open Accounts", f"{open_accounts:,}")


def render_charts(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Status Distribution")
        status_counts = df["Status"].value_counts().rename_axis("Status").reset_index(name="Count")
        st.bar_chart(status_counts.set_index("Status"))

    with col2:
        st.subheader("DPD Distribution")
        dpd_counts = df["DPD"].value_counts().sort_index()
        st.line_chart(dpd_counts)

    st.subheader("Asset Collateral by State")
    asset_by_state = df.groupby("State")["Asset_Colleteral_Value"].sum().sort_values(ascending=False)
    st.bar_chart(asset_by_state)


def main():
    st.title("Loan Portfolio Dashboard")
    st.markdown(
        "### Office-ready loan portfolio overview with filters, performance KPIs, and branch risk mapping."
    )
    st.markdown(
        "Use the sidebar filters to narrow the dataset and update the dashboard automatically."
    )

    st.sidebar.markdown("## Data source")
    st.sidebar.write(f"CSV file path: `{CSV_PATH}`")

    if CSV_PATH.exists():
        df = load_data(CSV_PATH)
    else:
        st.warning(
            "CSV file not found at the configured path. Upload a CSV file or set the `CSV_PATH` environment variable."
        )
        uploaded_file = st.file_uploader("Upload Loan Portfolio CSV", type=["csv"])
        if uploaded_file is None:
            st.stop()
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()

    filtered_df = build_filters(df)

    st.markdown("---")
    st.subheader("Portfolio Summary")
    render_metrics(filtered_df)
    st.markdown("---")

    render_charts(filtered_df)

    st.markdown("---")
    st.subheader("Branch Location Risk Map")
    folium_map = create_map(filtered_df)
    st.components.v1.html(folium_map._repr_html_(), height=650)

    st.markdown("---")
    st.subheader("Filtered Loan Portfolio Data")
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

    with st.expander("Download filtered data"):
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="filtered_loan_portfolio_filtered.csv")

    st.markdown(
        f"---\nLast refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
