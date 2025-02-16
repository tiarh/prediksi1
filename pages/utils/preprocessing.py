import pandas as pd
import numpy as np

def preprocess_data(df, lag):
    # Pastikan kolom 'Date' dalam format datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

    # Inisialisasi dataframe baru untuk fitur dan target
    feature_columns = []
    target_columns = []
    data = {}

    for step in range(lag):
        for col in ['Price', 'temperature_celsius', 'dewpoint_Celsius', 'precipitation', 'mean_pressure']:
            data[f"{col}_lag{step + 1}"] = df[col].shift(step + 1)
            feature_columns.append(f"{col}_lag{step + 1}")

    # Target untuk prediksi
    for i in range(1, 8):  # Misal prediksi t+1 hingga t+7
        data[f"Price_t+{i}"] = df['Price'].shift(-i)
        target_columns.append(f"Price_t+{i}")

    # Membuat dataframe baru
    transformed_df = pd.DataFrame(data)

    # Drop rows dengan nilai NaN karena efek lagging
    transformed_df.dropna(inplace=True)

    return transformed_df
