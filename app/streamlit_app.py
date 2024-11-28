# standard library imports
import os
from typing import Tuple

# third party imports
import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.graph_objects import Figure

# local imports


# Set page config
st.set_page_config(
    page_title="Steam Time Series", page_icon="📈", initial_sidebar_state="collapsed"
)

# Add page title
st.markdown(
    """
        <style>
            .appview-container .main .block-container {{
                padding-top: {padding_top}rem;
                padding-bottom: {padding_bottom}rem;
                }}

        </style>""".format(
        padding_top=1, padding_bottom=1
    ),
    unsafe_allow_html=True,
)
st.title("🎮 Steam Time Series 📈")

# Create the tabs
spacing = "\u2001\u2001\u2001"
tab1, tab2, tab3 = st.tabs(
    [
        f"{spacing} Home {spacing}",
        f"{spacing} Bandwidth Usage {spacing}",
        f"{spacing} About {spacing}",
    ]
)


# Get timestamp of last modification of file
def get_timestamp(file_path: str) -> float:
    ts = os.path.getmtime(file_path)

    return ts


# Smart data loading with caching
@st.cache_data
def load_data(file_path: str, timestamp: float, **kwargs) -> pd.DataFrame:
    data = pd.read_csv(file_path, **kwargs)

    return data


# Functions to plot data
@st.cache_data
def plot_bandwidth_usage_stacked_area(
    data: pd.DataFrame, timestamp: float
) -> Tuple[Figure, pd.Timestamp]:
    latest_data = data["Timestamp"].max()
    data_melted = data.melt(
        id_vars=["Timestamp"],
        value_vars=data.columns.to_list()[1:],
        var_name="Region",
        value_name="Bandwidth",
    )
    fig = (
        px.area(
            data_frame=data_melted,
            x="Timestamp",
            y="Bandwidth",
            color="Region",
            line_group="Region",
            labels={"Timestamp": "Date", "Bandwidth": "Bandwidth (Gbps)"},
            color_discrete_sequence=px.colors.sequential.Plasma_r,
        )
        .update_xaxes(
            range=[latest_data - pd.Timedelta(days=7), latest_data],
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=48, label="48h", step="hour", stepmode="backward"),
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=14, label="2w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(label="All", step="all"),
                    ]
                )
            ),
            rangeslider_thickness=0.075,
        )
        .update_yaxes(fixedrange=False)
        .update_layout(xaxis_title=None)
    )

    return fig, latest_data


# Load data
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BANDWIDTHS_PATH = os.path.join(DATA_DIR, "bandwidths.csv")

bandwidths_update_ts = get_timestamp(file_path=BANDWIDTHS_PATH)
bandwidths_df = load_data(
    file_path=BANDWIDTHS_PATH, timestamp=bandwidths_update_ts, parse_dates=["Timestamp"]
)

# Populate tabs with content
with tab1:
    st.markdown(
        """
        <style>
        a[href] {
            text-decoration: none;
            color: #66c0f4;
        }
        div.plotly-notifier {
            visibility: hidden;
        }
        </style>

        Welcome to Steam Forecasts!

        Steam has some cool stats about [download bandwidth usage](https://store.steampowered.com/stats/content).
        However, they only display the past 48 hours, respectively, with no way to easily access historical data. 
        While sites like [SteamDB](https://steamdb.info/) do a great job collecting and persisting other kinds of 
        data from Steam such as player counts over time, the data I'm interested in is not available there.

        This project aims to fill that gap and more by fetching, storing, and visualizing historical data
        as well as providing forecasts for future bandwidth usage and (maybe) support requests.
        Not only is this an interesting time series forecasting problem, but it also has the potential
        to provide valuable and practical insights to Steam users and developers.

        [![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/ehan03/Steam-Statistics-Forecasts) 
        """,
        unsafe_allow_html=True,
    )
    st.caption("Note: All times displayed are in UTC.")
with tab2:
    # Create plots
    bandwidths_stacked, bandwidths_latest = plot_bandwidth_usage_stacked_area(
        data=bandwidths_df, timestamp=bandwidths_update_ts
    )

    st.subheader("48-Hour Forecast")
    st.write("Coming soon 🚧👷‍♂️🚧")

    st.divider()

    st.subheader("Historical Download Bandwidth Usage")
    st.caption(f"Latest data: {bandwidths_latest.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    st.plotly_chart(bandwidths_stacked)
with tab3:
    st.markdown(
        """
        This project is a work in progress. 
        
        I'm still in the process of waiting for more data to accumulate
        so that I can start prototyping some forecasting models. I'll update this section with my
        methodology once I have something to show.
        """
    )
