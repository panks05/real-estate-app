# 🏠 Real Estate Price Prediction Web App

This is a Flask-based web application for predicting real estate prices in Bengaluru. It includes a user-friendly UI for users and an admin dashboard for managing properties, visualizing data, and monitoring model performance.

## 🚀 Features

### 🔒 User Portal
- Signup/Login with session management
- Home price estimator based on BHK, bath, sqft, and location
- Save searches and favorite listings
- Filter and sort property listings
- Export filtered results to CSV

### 🛠️ Admin Dashboard
- View and manage all property listings
- Add, edit, and delete properties
- Dynamic filters with AJAX (location, BHK, bath)
- Pagination support
- Model performance metrics (R² scores for Linear Regression, Lasso, Decision Tree)
- Visualizations (price distributions, top locations)
- Retrain model on new data (coming soon)

## 📦 Tech Stack

- **Backend**: Flask, SQLite, pandas, scikit-learn
- **Frontend**: Bootstrap 5, Chart.js, AJAX (jQuery)
- **Model**: Linear Regression (default), with support for Lasso & Decision Tree

## 🏗️ Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/real-estate-app.git
   cd real-estate-app
   ```

2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run database setup:

   ```bash
   python server/db_utils.py
   ```

4. Start the Flask server:

   ```bash
   python server/app.py
   ```

5. Visit `http://127.0.0.1:5000` to use the app.

## 🧪 Admin Credentials

- **Username**: admin
- **Password**: admin123

## 📁 File Structure

```
real-estate-app/
│
├── server/
│   ├── app.py               # Main Flask app
│   ├── db_utils.py          # Initializes SQLite DB
│   ├── model_utils.py       # Model training and metrics
│
├── templates/
│   ├── admin.html
│   ├── admin_table.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   └── ... more pages
│
├── static/
│   └── export.csv
│
├── artifacts/
│   ├── model.pkl
│   └── columns.json
│
├── database/
│   ├── properties.db
│   └── bhp.csv
│
├── requirements.txt
└── README.md
```

---

Made with ❤️ for price prediction in Indian real estate.