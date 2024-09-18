from __future__ import annotations

import time

import pandas as pd
import requests
import streamlit as st


# Helper function to simulate loading state
def add_loading_state():
    with st.spinner("Applying filters..."):
        time.sleep(1)


# Function to fetch data from the API
def fetch_data_from_api():
    try:
        response = requests.get(
            "http://localhost:8000/past-predictions"
        )  # Replace with your API URL
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return pd.DataFrame(data)
    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


# Main application
def main():
    st.title("Heart Disease Prediction")

    # Fetch data from API
    df = fetch_data_from_api()

    if df.empty:
        st.warning("No data available.")
        return

    # Initialize df_filtered
    df_filtered = df.copy()

    # Filter and Search Section
    with st.form(key="filter_form"):
        search_text = st.text_input("Search (any column)", "")
        apply_filter = st.form_submit_button("Apply Filter")

        if apply_filter:
            add_loading_state()

            if search_text:
                df_filtered = df[
                    df.apply(
                        lambda row: row.astype(str)
                        .str.contains(search_text, case=False)
                        .any(),
                        axis=1,
                    )
                ]

    # Pagination setup
    items_per_page = 10
    total_pages = (len(df_filtered) + items_per_page - 1) // items_per_page

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    df_paginated = df_filtered[start_idx:end_idx]

    # Display DataTable
    st.write(f"Page {st.session_state.current_page} of {total_pages}")
    st.dataframe(df_paginated)

    # Pagination buttons
    col1, col2, col3 = st.columns([2, 6, 2])
    with col1:
        if st.button("Previous") and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
    with col3:
        if st.button("Next") and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1

    # Prediction Form Section
    st.header("Make a Prediction")
    # with st.form(key="prediction_form"):
    #     age = st.number_input("Age", min_value=0, max_value=120, value=25)
    #     gender = st.selectbox("Gender", ["M", "F"])
    #     chest_pain = st.selectbox(
    #         "Chest Pain Type", ["ATA", "NAP", "ASY", "TA"]
    #     )
    #     resting_bp = st.number_input(
    #         "Resting BP", min_value=0, max_value=250, value=120
    #     )
    #     cholesterol = st.number_input(
    #         "Cholesterol", min_value=0, max_value=600, value=200
    #     )
    #     fasting_bs = st.selectbox(
    #         "Fasting Blood Sugar > 120 mg/dl", ["Yes", "No"]
    #     )
    #     resting_ecg = st.selectbox("Resting ECG", ["Normal", "ST", "LVH"])
    #     max_hr = st.number_input(
    #         "Max HR", min_value=50, max_value=220, value=150
    #     )
    #     exercise_angina = st.selectbox(
    #         "Exercise Induced Angina", ["Yes", "No"]
    #     )

    #     submit_prediction = st.form_submit_button("Submit Prediction")
    # if submit_prediction:
    st.success("Prediction submitted successfully!")


if __name__ == "__main__":
    main()
