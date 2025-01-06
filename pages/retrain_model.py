import streamlit as st
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from streamlit_utils import show_sidebar_pages
show_sidebar_pages()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from train_model import train_and_evaluate, get_next_versioned_filename, save_model, save_metrics

def main():
    st.title("Model Training and Evaluation")
    data_source = st.selectbox("Choose data source", ["CSV Files", "Postgres Database"], help="Choose the source of the training and test data")

    if data_source == "CSV Files":
        csv_dir = "provided"
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        
        if not csv_files:
            st.error(f"No CSV files found in directory '{csv_dir}'")
            return
        
        train_file = st.selectbox("Choose training CSV file", csv_files, index=1, help="CSV files present in the directory called 'provided'")
        test_file = st.selectbox("Choose test CSV file", csv_files, index=0, help="CSV files present in the directory called 'provided'")
        
        train_path = os.path.join(csv_dir, train_file)
        test_path = os.path.join(csv_dir, test_file)
        db_url = None
        table_name = None
        data_source="csv"

    elif data_source == "Postgres Database":
        db_url = st.text_input("Enter database connection string", value="postgresql://postgres:password@localhost:5432/ml_model_db", help="For this demo, the default option is: postgresql://postgres:password@localhost:5432/ml_model_db")
        table_name = st.text_input("Enter table name", value="public.property_friends_model_data" , help="For this demo, the default option is: public.property_friends_model_data")
        train_path = None
        test_path = None
        checkbox_best_practice = st.checkbox("Use best practice data processing", help="Change the way data is processed to follow best practices, such as random splitting, data cleaning, outliers removal, etc.")
        if checkbox_best_practice:
            data_source="db_best_practice"
        else:
            data_source="db"

    format = st.selectbox("Choose model format", ["joblib", "pickle"], help="does not affect the demo, but can be useful if model is exported for use in other applications")

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
            st.divider()
            st.write("Model saved to: ")
            st.write(f"{filename}.{format}")
            st.write("Evaluation Metrics:")
            st.write(metrics)
        except Exception as e:
            st.error(str(e))

if __name__ == "__main__":
    main()