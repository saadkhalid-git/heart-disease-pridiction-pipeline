from __future__ import annotations

import time

import pandas as pd
import streamlit as st

import requests

# Sample DataFrame based on the provided image
data = {
    "Id": [
        "PT1000",
        "PT1001",
        "PT1002",
        "PT1003",
        "PT1004",
        "PT1005",
        "PT1006",
        "PT1007",
        "PT1008",
        "PT1009",
        "PT1010",
    ],
    "Age": [42, 54, 60, 54, 55, 59, 47, 49, 67, 63, 43],
    "Gender": ["M", "M", "M", "M", "M", "M", "M", "M", "F", "M", "M"],
    "ChestPainType": [
        "ASY",
        "NAP",
        "ASY",
        "ATA",
        "ASY",
        "ASY",
        "NAP",
        "ASY",
        "NAP",
        "ASY",
        "ATA",
    ],
    "RestingBP": [120, 140, 141, 124, 160, 140, 108, 130, 152, 170, 142],
    "Cholesterol": [198, 239, 316, 266, 292, 264, 243, 206, 277, 177, 207],
    "FastingBS": [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
    "RestingECG": [
        "Normal",
        "Normal",
        "ST",
        "LVH",
        "Normal",
        "LVH",
        "Normal",
        "Normal",
        "Normal",
        "Normal",
        "Normal",
    ],
    "MaxHR": [155, 160, 122, 109, 143, 119, 152, 170, 172, 84, 138],
    "ExerciseAngina": ["N", "N", "Y", "Y", "N", "Y", "N", "N", "N", "Y", "N"],
}
df = pd.DataFrame(data)


# Helper function to add a loading state
def add_loading_state():
    with st.spinner("Applying filters..."):
        time.sleep(2)


# Main application
def main():

    predict, history = st.tabs(["Making a Prediction", "Prediction History"])

    with predict:
        # Prediction Form Section
        st.header("Make a Prediction")
        with st.form(key="prediction_form"):
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
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
                "Fasting Blood Sugar > 120 mg/dl", ["Yes", "No"]
            )
            resting_ecg = st.selectbox("Resting ECG", ["Normal", "ST", "LVH"])
            max_hr = st.number_input(
                "Max HR", min_value=50, max_value=220, value=150
            )
            exercise_angina = st.selectbox(
                "Exercise Induced Angina", ["Yes", "No"]
            )

            submit_prediction = st.form_submit_button("Submit Prediction")

            if submit_prediction:
                st.success("Prediction submitted successfully!")
                # You can add your prediction logic here
                response = requests.post(
                    "http://localhost:8000/predict",
                    json={
                        "age": age,
                        "gender": gender,
                        "chest_pain": chest_pain,
                        "resting_bp": resting_bp,
                        "cholesterol": cholesterol,
                        "fasting_bs": fasting_bs,
                        "resting_ecg": resting_ecg,
                        "max_hr": max_hr,
                        "exercise_angina": exercise_angina,
                    },
                )
                prediction = response.json().get("prediction")
                st.success(f"Prediction: {prediction:'No prediction available'}")
       
        # File Upload Section for Multiple Predictions
        st.header("Upload CSV for Multiple Predictions")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file is not None:
            df_uploaded = pd.read_csv(uploaded_file)
            st.write("Uploaded Data:")
            st.write(df_uploaded)

            if st.button("Submit for Predictions"):
                predictions = []
                for _, row in df_uploaded.iterrows():
                    response = requests.post(
                        "http://localhost:8000/predict",
                        json=row.to_dict(),
                    )
                    prediction = response.json().get("prediction")
                    predictions.append(prediction)

                df_uploaded["Prediction"] = predictions
                st.write("Predictions:")
                st.write(df_uploaded)
    
    with history:
        st.title("Heart Disease Prediction")

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
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                    },
                )
                # df_filtered = pd.DataFrame(response.json())

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
                start_idx = (st.session_state.current_page - 1) * items_per_page
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
        st.write(f"Page {st.session_state.current_page} of {total_pages}")
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



# Run the app
if __name__ == "__main__":
    main()