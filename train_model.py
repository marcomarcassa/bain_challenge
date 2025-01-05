import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, mean_absolute_error
from sklearn.model_selection import train_test_split
from category_encoders import TargetEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sqlalchemy import create_engine
import argparse
import joblib
import pickle
import os
import json
from datetime import datetime

def load_data_from_csv(train_path: str, test_path: str) -> (pd.DataFrame, pd.DataFrame):
    """Loads the train and test data into pandas DataFrames from CSV files"""
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    return train, test

def load_data_from_db(db_url: str, table_name: str, test_size: float = 0.2, random_state: int = 42) -> (pd.DataFrame, pd.DataFrame):
    """Loads data from a database and splits it into train and test sets using scikit-learn."""
    engine = create_engine(db_url)
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql(query, engine)
    
    # Use train_test_split
    train, test = train_test_split(data, test_size=test_size, random_state=random_state)
    
    return train, test


def create_pipeline(categorical_cols: list, model_params: dict) -> Pipeline:
    """Creates and returns a preprocessing and modeling pipeline"""
    categorical_transformer = TargetEncoder()
    preprocessor = ColumnTransformer(
        transformers=[
            ('categorical', categorical_transformer, categorical_cols)
        ]
    )
    steps = [
        ('preprocessor', preprocessor),
        ('model', GradientBoostingRegressor(**model_params))
    ]
    return Pipeline(steps)

def get_metrics(predictions, target):
    """Returns evaluation metrics as a dictionary"""
    return {
        "RMSE": np.sqrt(mean_squared_error(target, predictions)),
        "MAPE": mean_absolute_percentage_error(target, predictions),
        "MAE": mean_absolute_error(target, predictions),
        "timestamp": datetime.now().isoformat()
    }

def print_metrics(metrics):
    """Prints evaluation metrics"""
    print("RMSE: ", metrics["RMSE"])
    print("MAPE: ", metrics["MAPE"])
    print("MAE : ", metrics["MAE"])

def get_next_versioned_filename(base_path: str) -> str:
    """Returns the next versioned filename regardless of extension"""
    version = 1
    while any(os.path.exists(f"{base_path}_v{version}.{ext}") for ext in ['joblib', 'pkl']):
        version += 1
    return f"{base_path}_v{version}"

def train_and_evaluate(data_source: str, train_path: str = None, test_path: str = None, db_url: str = None, table_name: str = None):
    """Trains the model and evaluates its performance, using either CSV files or a database"""
    if data_source == 'csv':
        if not train_path or not test_path:
            raise ValueError("For CSV data source, both train_path and test_path must be provided.")
        train, test = load_data_from_csv(train_path, test_path)
    elif data_source == 'db':
        if not db_url or not table_name:
            raise ValueError("For DB data source, both db_url and table_name must be provided.")
        train, test = load_data_from_db(db_url, table_name)
    else:
        raise ValueError("Invalid data source. Choose either 'csv' or 'db'.")

    train_cols = [col for col in train.columns if col not in ['id', 'price', 'is_test']]
    target = "price"
    categorical_cols = ["type", "sector"]

    model_params = {
        "learning_rate": 0.01,
        "n_estimators": 100,
        "max_depth": 3
    }
    print(train.head())
    print(test.head())
    
    pipeline = create_pipeline(categorical_cols, model_params)
    pipeline.fit(train[train_cols], train[target])

    test_predictions = pipeline.predict(test[train_cols])
    test_target = test[target].values

    metrics = get_metrics(test_predictions, test_target)
    print_metrics(metrics)

    return pipeline, metrics

def save_model(model, filename: str, format: str = 'joblib'):
    """Saves the trained model to a file"""
    if format.lower() == 'joblib':
        joblib.dump(model, f"{filename}.joblib")
    elif format.lower() == 'pickle':
        with open(f"{filename}.pkl", 'wb') as f:
            pickle.dump(model, f)
    else:
        raise ValueError("Invalid format. Supported formats are 'joblib' and 'pickle'.")

def save_metrics(metrics, filename: str, ext):
    """Saves the metrics to a JSON file"""
    metrics_filename = "models/model_metrics.json"
    
    if ext == "pickle": 
        ext = "pkl"

    if os.path.exists(metrics_filename):
        with open(metrics_filename, 'r') as f:
            all_metrics = json.load(f)
    else:
        all_metrics = {}

    all_metrics[f"{filename}.{ext}"] = metrics

    with open(metrics_filename, 'w') as f:
        json.dump(all_metrics, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train and evaluate a model')
    parser.add_argument('--data_source', type=str, required=True, choices=['csv', 'db'], help='Data source: "csv" or "db"')
    parser.add_argument('--train', type=str, help='Path to the training CSV file (if using CSV)')
    parser.add_argument('--test', type=str, help='Path to the testing CSV file (if using CSV)')
    parser.add_argument('--db_url', type=str, help='Database connection string (if using DB)')
    parser.add_argument('--table_name', type=str, help='Name of the table in the database (if using DB)')
    parser.add_argument('--format', type=str, default='joblib', help='Format to save the model (joblib or pickle)')
    args = parser.parse_args()

    model, metrics = train_and_evaluate(
        data_source=args.data_source,
        train_path=args.train,
        test_path=args.test,
        db_url=args.db_url,
        table_name=args.table_name
    )

    filename = get_next_versioned_filename("models/property_friends")
    save_model(model, filename, args.format)
    save_metrics(metrics, filename, args.format)

    ext = 'pkl' if args.format == "pickle" else 'joblib'
    print(f"Model saved to {filename}.{ext}")
