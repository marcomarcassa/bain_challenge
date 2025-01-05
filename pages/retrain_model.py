import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from train_model import train_and_evaluate, get_next_versioned_filename, save_model, save_metrics

def main():
    st.title("Model Training and Evaluation")
    data_source = st.selectbox("Choose data source", ["csv", "db"])

    if data_source == "csv":
        train_path = st.text_input("Enter train CSV file path")
        test_path = st.text_input("Enter test CSV file path")
        db_url = None
        table_name = None
    elif data_source == "db":
        db_url = st.text_input("Enter database connection string")
        table_name = st.text_input("Enter table name")
        train_path = None
        test_path = None

    format = st.selectbox("Choose model format", ["joblib", "pickle"])

    if st.button("Train and Evaluate"):
        try:
            model, metrics = train_and_evaluate(
                data_source=data_source,
                train_path=train_path,
                test_path=test_path,
                db_url=db_url,
                table_name=table_name
            )

            filename = get_next_versioned_filename("models/property_friends")
            save_model(model, filename, format)
            save_metrics(metrics, filename, format)

            st.write(f"Model saved to {filename}.{format}")
            st.write("Evaluation Metrics:")
            st.write(metrics)
        except Exception as e:
            st.error(str(e))

if __name__ == "__main__":
    main()