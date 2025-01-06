import pandas as pd

def remove_invalid_rows(data: pd.DataFrame) -> pd.DataFrame:
    """Processes the data to filter out invalid or unusable rows."""
    # Remove rows with zero or negative values in key columns (e.g., price, area)
    data = data[(data['price'] > 0) & (data['net_usable_area'] > 0) & (data['net_area'] > 0)]
    
    return data

def feature_engineering(data: pd.DataFrame) -> pd.DataFrame:
    """Performs feature engineering on the dataset."""
    
    # Create derived features
    if 'price' in data.columns and 'net_usable_area' in data.columns:
        data['price_per_sq_meter'] = data['price'] / data['net_usable_area']
    
    
    return data
