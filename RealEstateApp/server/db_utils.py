import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join("database", "properties.db")
CSV_PATH = os.path.join("database", "bhp.csv")

def create_database():
    df = pd.read_csv(CSV_PATH)

    # Normalize column names
    df = df.rename(columns={
        'location': 'location',
        'total_sqft': 'sqft',
        'bath': 'bath',
        'bhk': 'bhk',
        'price': 'price'
    })

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create properties table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            sqft REAL,
            bath INTEGER,
            bhk INTEGER,
            price REAL
        )
    ''')
    cursor.execute("DELETE FROM properties")

    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO properties (location, sqft, bath, bhk, price)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['location'], row['sqft'], row['bath'], row['bhk'], row['price']))

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL
        )
    ''')

    # ✅ Create saved_searches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            location TEXT,
            bhk INTEGER,
            bath INTEGER,
            min_sqft REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Add this to create_database() after saved_searches table

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS favorites
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER
                       NOT
                       NULL,
                       property_id
                       INTEGER
                       NOT
                       NULL,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   ),
                       FOREIGN KEY
                   (
                       property_id
                   ) REFERENCES properties
                   (
                       id
                   )
                       )
                   ''')

    conn.commit()
    conn.close()
    print("✅ Database setup complete.")


if __name__ == '__main__':
    create_database()
