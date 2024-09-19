from __future__ import annotations

import json
import time

import pandas as pd
import requests
import streamlit as st


# Helper function to simulate loading state
def add_loading_state():
    with st.spinner("Applying filters..."):
        time.sleep(1)


def fetch_data_from_api():
    try:
        response = requests.get("http://localhost:8000/past-predictions")
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def validate_csv_columns(df):
    # Update the required columns to match the camel case format
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

    # Check if all required columns are present in the DataFrame
    if required_columns.issubset(df.columns):
        return True
    else:
        missing_cols = required_columns - set(df.columns)
        return f"Missing required columns: {', '.join(missing_cols)}"


def map_and_rename_columns(df):
    # Define the mapping of old column names to new column names
    column_mapping = {
        "Age": "age",
        "Gender": "gender",
        "ChestPainType": "chest_pain_type",
        "RestingBP": "resting_bp",
        "Cholesterol": "cholesterol",
        "FastingBS": "fasting_bs",
        "RestingECG": "resting_ecg",
        "MaxHR": "max_hr",
        "ST_Slope": "st_slope",
        "ExerciseAngina": "exercise_angina",
        "Oldpeak": "old_peak",
    }
    # Rename the columns
    df.rename(columns=column_mapping, inplace=True)
    df = df[list(column_mapping.values())]

    # Return the modified DataFrame
    return df


def snake_to_title(snake_str):
    components = snake_str.split("_")
    return " ".join(x.title() for x in components)


# Function to make predictions
def make_prediction(data):
    # Example API URL (replace with your actual endpoint)
    api_url = "http://localhost:8000/predict"

    # Convert the data to JSON
    json_data = json.dumps(data)
    # Send the request to the API
    print(json_data)
    response = requests.post(
        api_url, data=json_data, headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to get prediction from API"}


# Main application
def main():
    st.title("Heart Disease Prediction")
    history, predict = st.tabs(["Prediction History", "Making a Prediction"])
    df = fetch_data_from_api()
    df.columns = [snake_to_title(col) for col in df.columns]
    with predict:
        # Option Selection (above the table)
        option = st.selectbox(
            "Choose Prediction Type", ["Single Prediction", "Bulk Prediction"]
        )
        # Option-specific content
        if option == "Single Prediction":
            with st.expander("Single Prediction Form", expanded=True):
                age = st.number_input(
                    "Age", min_value=0, max_value=120, value=25
                )
                gender = st.selectbox("Gender", ["M", "F"])
                chest_pain = st.selectbox(
                    "Chest Pain Type", ["ATA", "NAP", "ASY", "TA"]
                )
                resting_bp = st.number_input(
                    "Resting BP", min_value=0, max_value=250, value=120
                )
                cholesterol = st.number_input(
                    "Cholesterol", min_value=0, max_value=600, value=200
                )
                fasting_bs = st.selectbox(
                    "Fasting Blood Sugar > 120 mg/dl", ["Y", "N"]
                )
                resting_ecg = st.selectbox(
                    "Resting ECG", ["Normal", "ST", "LVH"]
                )
                st_slope = st.selectbox("St Slope", ["Flat", "Up", "Down"])
                max_hr = st.number_input(
                    "Max HR", min_value=50, max_value=220, value=150
                )
                old_peak = st.number_input("Old Peak", value=0)
                exercise_angina = st.selectbox(
                    "Exercise Induced Angina", ["Y", "N"]
                )
                if st.button("Submit Single Prediction"):
                    data = [
                        {
                            "age": age,
                            "gender": gender,
                            "chest_pain_type": chest_pain,
                            "resting_bp": resting_bp,
                            "cholesterol": cholesterol,
                            "fasting_bs": fasting_bs,
                            "resting_ecg": resting_ecg,
                            "max_hr": max_hr,
                            "st_slope": st_slope,
                            "old_peak": old_peak,
                            "exercise_angina": exercise_angina,
                        }
                    ]

                    # Call the API with the single prediction data
                    result = make_prediction(data)

                    st.write("Prediction Result:", result)

        elif option == "Bulk Prediction":
            option = "Bulk Prediction"
            # File uploader for CSV files
            uploaded_file = st.file_uploader("Upload CSV File", type="csv")

            if uploaded_file is not None:
                if st.button("Submit Bulk Prediction"):
                    df = pd.read_csv(uploaded_file)

                    # Validate the CSV file structure
                    if validate_csv_columns(df):
                        # Convert the DataFrame to JSON format
                        df = map_and_rename_columns(df)
                        data = df.to_dict(orient="records")

                        # Make the bulk prediction API call
                        result = make_prediction(data)

                        # Display the result in a DataTable
                        st.subheader("Prediction Results")
                        st.write("Prediction Result:", result)
                        # if isinstance(result, pd.DataFrame):
                        #     st.dataframe(df)
                        # else:
                        #     result_df = pd.DataFrame(result)
                        #     st.dataframe(result_df)
                    else:
                        st.error(
                            "CSV file does not contain the required columns"
                        )
    with history:
        # Filter and Search Section
        with st.form(key="filter_form"):
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=None)
            with col2:
                end_date = st.date_input("End Date", value=None)

            search_text = st.text_input("Search (any column)", "")

            apply_filter = st.form_submit_button("Apply Filter")
            if apply_filter:
                add_loading_state()

                # Make a request to the FastAPI endpoint for filtering
                response = requests.post(
                    "http://localhost:8000/filter",
                    json={
                        "search_text": search_text,
                        "start_date": start_date.isoformat()
                        if start_date
                        else None,
                        "end_date": end_date.isoformat() if end_date else None,
                    },
                )
                df_filtered = pd.DataFrame(response.json())

                # Start filtering by search input
                if search_text:
                    df_filtered = df[
                        df.apply(
                            lambda row: row.astype(str)
                            .str.contains(search_text, case=False)
                            .any(),
                            axis=1,
                        )
                    ]
                else:
                    df_filtered = df.copy()  # No search applied, show all

                # Date filtering logic: You can implement

                # your own logic for date-based
                if start_date and end_date:
                    st.write(
                        f"Showing results for dates between {start_date} and {end_date}"
                    )
                else:
                    st.write("No date filtering applied")

                # Pagination setup
                items_per_page = 10
                total_pages = len(df_filtered) // items_per_page + (
                    1 if len(df_filtered) % items_per_page > 0 else 0
                )

                # Select current page
                if "current_page" not in st.session_state:
                    st.session_state.current_page = 1

                # Paginate dataframe
                start_idx = (
                    st.session_state.current_page - 1
                ) * items_per_page
                end_idx = start_idx + items_per_page
                df_paginated = df_filtered[start_idx:end_idx]

                st.write(df_paginated)

            else:
                df_filtered = df.copy()  # No filtering applied initially

        # Pagination setup
        items_per_page = 10
        total_pages = len(df_filtered) // items_per_page + (
            1 if len(df_filtered) % items_per_page > 0 else 0
        )

        # Select current page
        if "current_page" not in st.session_state:
            st.session_state.current_page = 1

        # Paginate dataframe
        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        df_paginated = df_filtered[start_idx:end_idx]

        # Show the DataTable with full page width
        st.dataframe(df_paginated, width=1500)

        # Update page on button click
        col1, col2, col3 = st.columns(
            [2, 6, 2]
        )  # Adjusted column widths for button width
        with col1:
            if st.button("Previous"):
                if st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
        with col3:
            if st.button("Next"):
                if st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1

        st.write(f"Page {st.session_state.current_page} of {total_pages}")


# Run the app
if __name__ == "__main__":
    main()
