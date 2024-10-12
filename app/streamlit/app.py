from __future__ import annotations

import json
import os
import time

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000/")
BASE_URL = API_URL + "past-predictions"
ITEMS_PER_PAGE = 10


# Initialize session state
st.session_state.setdefault("current_page", 1)
st.session_state.setdefault("total_pages", 1)


# Helper function to simulate loading state
def add_loading_state():
    with st.spinner("Applying filters..."):
        time.sleep(2)
        st.success("Filters applied!")


def fetch_data(params={}) -> pd.DataFrame:
    """Fetch data from the FastAPI backend."""
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            return pd.DataFrame(data)
        else:
            st.error("Unexpected data format received.")
            return pd.DataFrame()

    else:
        st.error("Error fetching data")
        return pd.DataFrame()  # Return an empty DataFrame instead of None


def display_data(df):
    """Display the DataFrame in Streamlit."""
    if df.empty:
        st.warning("No data found for the applied filters.")
    else:
        df = reorder_columns(df)
        df.columns = [snake_to_title(col) for col in df.columns]
        st.dataframe(df, width=1500)


def validate_csv_columns(df: pd.DataFrame) -> bool | str:
    """Validate required CSV columns."""
    required_columns = {
        "Age",
        "Gender",
        "ChestPainType",
        "RestingBP",
        "Cholesterol",
        "FastingBS",
        "RestingECG",
        "MaxHR",
        "ExerciseAngina",
    }
    missing_cols = required_columns - set(df.columns)
    return (
        True
        if not missing_cols
        else f"Missing required columns: {', '.join(missing_cols)}"
    )


def map_and_rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map and rename DataFrame columns."""
    column_mapping = {
        "Gender": "gender",
        "ChestPainType": "chest_pain_type",
        "RestingECG": "resting_ecg",
        "ExerciseAngina": "exercise_angina",
        "Cholesterol": "cholesterol",
        "RestingBP": "resting_bp",
        "MaxHR": "max_hr",
        "Oldpeak": "old_peak",
        "ST_Slope": "st_slope",
        "FastingBS": "fasting_bs",
        "Age": "age",
        "HeartDisease": "heart_disease",
    }
    desired_order = [
        "age",
        "gender",
        "chest_pain_type",
        "resting_bp",
        "cholesterol",
        "fasting_bs",
        "resting_ecg",
        "max_hr",
        "exercise_angina",
        "old_peak",
        "st_slope",
        "heart_disease",
    ]
    df.rename(columns=column_mapping, inplace=True)
    return df[desired_order]


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Reorder DataFrame columns."""
    column_order = [
        "age",
        "gender",
        "chest_pain_type",
        "resting_bp",
        "cholesterol",
        "fasting_bs",
        "resting_ecg",
        "max_hr",
        "exercise_angina",
        "old_peak",
        "st_slope",
        "heart_disease",
    ]
    if "created_at" in df.columns:
        column_order.append("created_at")
    return df[column_order]


def snake_to_title(snake_str: str) -> str:
    """Convert snake_case string to Title Case."""
    return " ".join(word.title() for word in snake_str.split("_"))


def make_prediction(data: list) -> dict:
    """Send prediction request to the API."""
    response = requests.post(
        API_URL + "predict",
        json=data,  # Automatically handles JSON serialization
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()


def display_prediction_result(result: dict):
    """Display prediction result in Streamlit."""
    if isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True)
    else:
        try:
            result_df = pd.DataFrame(result)
            result_df.columns = [
                snake_to_title(col) for col in result_df.columns
            ]
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.write("Error displaying result:", e)


# Main application
def main():
    st.title("Heart Disease Prediction")
    history, predict = st.tabs(["Prediction History", "Making a Prediction"])
    df = fetch_data()

    with predict:
        option = st.selectbox(
            "Choose Prediction Type", ["Single Prediction", "Bulk Prediction"]
        )

        if option == "Single Prediction":
            with st.expander("Single Prediction Form", expanded=True):
                form_data = {
                    "age": st.number_input(
                        "Age", min_value=0, max_value=120, value=25
                    ),
                    "gender": st.selectbox("Gender", ["M", "F"]),
                    "chest_pain_type": st.selectbox(
                        "Chest Pain Type", ["ATA", "NAP", "ASY", "TA"]
                    ),
                    "resting_bp": st.number_input(
                        "Resting BP", min_value=0, max_value=250, value=120
                    ),
                    "cholesterol": st.number_input(
                        "Cholesterol", min_value=0, max_value=600, value=200
                    ),
                    "fasting_bs": st.number_input(
                        "Fasting Blood Sugar > 120 mg/dl", value=0.0
                    ),
                    "resting_ecg": st.selectbox(
                        "Resting ECG", ["Normal", "ST", "LVH"]
                    ),
                    "st_slope": st.selectbox(
                        "St Slope", ["Flat", "Up", "Down"]
                    ),
                    "max_hr": st.number_input(
                        "Max HR", min_value=50, max_value=220, value=150
                    ),
                    "old_peak": st.number_input("Old Peak", value=1.0),
                    "exercise_angina": st.selectbox(
                        "Exercise Induced Angina", ["Y", "N"]
                    ),
                }

                if st.button("Submit Single Prediction"):
                    data = [
                        form_data
                    ]  # Wrapping in a list for consistent format
                    with st.spinner("Making prediction..."):
                        result = make_prediction(data)
                        st.subheader("Prediction Result")
                        display_prediction_result(result)

        elif option == "Bulk Prediction":
            uploaded_file = st.file_uploader("Upload CSV File", type="csv")

            if uploaded_file is not None and st.button(
                "Submit Bulk Prediction"
            ):
                df = pd.read_csv(uploaded_file)
                if validate_csv_columns(df) is True:
                    df = map_and_rename_columns(df)
                    data = df.to_dict(orient="records")
                    with st.spinner("Making bulk predictions..."):
                        result = make_prediction(data)
                        st.subheader("Prediction Results")
                        display_prediction_result(result)

    with history:
        if df is None or df.empty:
            st.warning(
                "No data available. Please make a prediction to view history."
            )
        else:
            df = reorder_columns(df)
            df.columns = [snake_to_title(col) for col in df.columns]

            # Form for filtering
            with st.form(key="filter_form"):
                column_selection = st.selectbox(
                    "Select Column for Search", options=df.columns
                )
                search_text = st.text_input("Search (any column)", "")

                start_date = st.date_input("Start Date", value=None)
                end_date = st.date_input("End Date", value=None)

                apply_filter = st.form_submit_button("Apply Filter")
                print(apply_filter)

            # Prepare request parameters
            request_params = {
                "search_text": search_text,
                "column": column_selection.replace(" ", "_").lower(),
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "page": st.session_state.current_page,
                "page_size": ITEMS_PER_PAGE,
            }

            # Fetch initial data
            data = fetch_data(request_params)
            if df is None or df.empty:
                st.warning("No data available for the applied filters.")
            else:
                df_filtered = pd.DataFrame(data)
                st.session_state.total_pages = data.get("total_pages", 1)

                display_data(df_filtered)

                # Pagination controls
                col1, col2, col3 = st.columns([2, 6, 2])
                pre_btn_cond = st.session_state.current_page > 1
                with col1:
                    if st.button("Previous") and pre_btn_cond:
                        st.session_state.current_page -= 1
                        request_params["page"] = st.session_state.current_page
                        data = fetch_data(request_params)
                        if df is None or df.empty:
                            df_filtered = pd.DataFrame(data)
                            st.session_state.total_pages = data.get(
                                "total_pages", 1
                            )
                            display_data(df_filtered)

                with col3:
                    if st.button("Next"):
                        st.session_state.current_page += 1
                        request_params["page"] = st.session_state.current_page
                        data = fetch_data(request_params)
                        if df is None or df.empty:
                            df_filtered = pd.DataFrame(data)
                            st.session_state.total_pages = data.get(
                                "total_pages", 1
                            )
                            display_data(df_filtered)


if __name__ == "__main__":
    main()
