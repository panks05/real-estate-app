import pandas as pd
import sqlite3
import pickle
import json
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

DB_PATH = os.path.join("database", "properties.db")
MODEL_PATH = os.path.join("artifacts", "model.pkl")
COLUMNS_PATH = os.path.join("artifacts", "columns.json")

def train_model():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT location, sqft, bath, bhk, price FROM properties", conn)
    conn.close()

    X = df.drop("price", axis=1)
    y = df["price"]

    # Define categorical and numeric features
    categorical_features = ["location"]
    numeric_features = ["sqft", "bath", "bhk"]

    # Column Transformer
    column_transformer = ColumnTransformer([
        ('location_encoder', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ], remainder='passthrough')

    # Pipeline
    model = Pipeline([
        ('transformer', column_transformer),
        ('regressor', LinearRegression())
    ])

    model.fit(X, y)

    # Save model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)

    # Save column metadata
    columns_info = {
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "all_columns": list(X.columns)
    }

    with open(COLUMNS_PATH, 'w') as f:
        json.dump(columns_info, f)

    print("✅ Model training complete.")
    print("📦 Model saved to:", MODEL_PATH)

if __name__ == "__main__":
    train_model()
