import pandas as pd
from sqlalchemy import create_engine
import os

# Get the current directory (config)
current_dir = os.path.dirname(__file__)

# Go up one level to the parent directory (bain_challenge)
parent_dir = os.path.dirname(current_dir)

# Join the parent directory with the provided directory
provided_dir = os.path.join(parent_dir, 'provided')

# Read train and test CSV files
train = pd.read_csv(os.path.join(provided_dir, "train.csv"))
test = pd.read_csv(os.path.join(provided_dir, "test.csv"))


# Database connection URL
DATABASE_URL = "postgresql://postgres:password@localhost:5432/ml_model_db"

# Add the 'is_test' column
train['is_test'] = False
test['is_test'] = True

# Combine train and test datasets
data = pd.concat([train, test])

# Insert data into the database
engine = create_engine(DATABASE_URL)
data.to_sql('property_friends_model_data', engine, if_exists='replace', index=False)
print("Data successfully loaded into the database!")

