import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NIFTY Model Dashboard",
    page_icon="📈",
    layout="wide"
)



SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    dict(st.secrets["gcp_service_account"]),
    scopes=SCOPES
)

gc = gspread.authorize(credentials)



GOOGLE_SHEET_ID = "1EP2UEufBvnUtf8LxDpmjuT4lDQFVEGp2apLwFdtfod4"
GOOGLE_SHEET_TAB = "Predictions"


spreadsheet = gc.open_by_key(
    GOOGLE_SHEET_ID
)

sheet = spreadsheet.worksheet(
    GOOGLE_SHEET_TAB
)

records = sheet.get_all_records()

df = pd.DataFrame(records)


if df.empty:
    st.warning("No prediction data available.")
    st.stop()


df["datetime"] = pd.to_datetime(
    df["datetime"],
    errors="coerce"
)


df = df.dropna(
    subset=["datetime"]
)


df = df.sort_values(
    "datetime",
    ascending=False
)


# Convert probabilities to numeric

df["up_prob"] = pd.to_numeric(
    df["up_prob"],
    errors="coerce"
)

df["down_prob"] = pd.to_numeric(
    df["down_prob"],
    errors="coerce"
)




st.title(
    "📈 NIFTY Intraday Model Dashboard"
)

st.caption(
    "Morning & Afternoon Model Predictions"
)


latest = df.iloc[0]




col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Symbol",
        latest["symbol"]
    )


with col2:

    st.metric(
        "Session",
        latest["session"]
    )


with col3:

    st.metric(
        "Datetime",
        latest["datetime"].strftime(
            "%d %b %Y %H:%M"
        )
    )


# ============================================================
# LATEST PREDICTION
# ============================================================

st.subheader(
    "Latest Prediction"
)


c1, c2 = st.columns(2)


with c1:

    if pd.isna(latest["up_prob"]):

        up_value = "N/A"

    else:

        up_value = f"{latest['up_prob']:.2%}"


    st.metric(
        "UP Probability",
        up_value
    )


with c2:

    if pd.isna(latest["down_prob"]):

        down_value = "N/A"

    else:

        down_value = f"{latest['down_prob']:.2%}"


    st.metric(
        "DOWN Probability",
        down_value
    )


# ============================================================
# PREDICTIONS
# ============================================================

p1, p2 = st.columns(2)


with p1:

    up_pred = latest["up_pred"]

    if pd.isna(up_pred) or up_pred == "":
        up_prediction = "N/A"

    elif int(float(up_pred)) == 1:
        up_prediction = "UP"

    else:
        up_prediction = "NO"


    st.metric(
        "UP Prediction",
        up_prediction
    )


with p2:

    down_pred = latest["down_pred"]

    if pd.isna(down_pred) or down_pred == "":
        down_prediction = "N/A"

    elif int(float(down_pred)) == 1:
        down_prediction = "DOWN"

    else:
        down_prediction = "NO"


    st.metric(
        "DOWN Prediction",
        down_prediction
    )


# ============================================================
# MODEL VERSION
# ============================================================

st.caption(
    f"Model Version: {latest['model_version']}"
)


# ============================================================
# PREDICTION HISTORY
# ============================================================

st.subheader(
    "Prediction History"
)


history_df = df.copy()


history_df["datetime"] = history_df[
    "datetime"
].dt.strftime(
    "%d %b %Y %H:%M"
)


st.dataframe(
    history_df,
    use_container_width=True,
    hide_index=True
)
