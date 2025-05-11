# Rewriting the corrected version of the complete app.py file as requested
from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pickle
import os
import json
import pandas as pd

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.jinja_env.globals.update(max=max, min=min)

app.secret_key = 'your_secret_key'

MODEL_PATH = os.path.join("artifacts", "model.pkl")
DB_PATH = os.path.join("database", "properties.db")

# Load model
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# Load column info
with open(os.path.join("artifacts", "columns.json")) as f:
    columns_info = json.load(f)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login_user'))
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT location FROM properties ORDER BY location ASC", conn)
    conn.close()
    locations = df['location'].tolist()
    return render_template('index.html', locations=locations)

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401
    data = request.get_json()
    location = data['location']
    sqft = float(data['sqft'])
    bath = int(data['bath'])
    bhk = int(data['bhk'])
    df = pd.DataFrame([[location, sqft, bath, bhk]], columns=columns_info['all_columns'])
    pred = model.predict(df)[0]
    return jsonify({'estimated_price': round(pred, 2)})

@app.route('/properties')
def properties():
    location = request.args.get('location', '')
    conn = sqlite3.connect(DB_PATH)
    if location:
        df = pd.read_sql_query("SELECT * FROM properties WHERE location = ?", conn, params=(location,))
    else:
        df = pd.read_sql_query("SELECT * FROM properties", conn)
    conn.close()
    return df.to_dict(orient='records')

@app.route('/admin')
def admin():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login_admin'))

    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    selected_location = request.args.get("location", "")
    selected_bhk = request.args.get("bhk", "")
    selected_bath = request.args.get("bath", "")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM properties", conn)

    # Chart data should always be based on the full dataset
    chart_df = df.groupby('location')['price'].mean().sort_values(ascending=False).head(10)
    chart_data = {
        'labels': chart_df.index.tolist(),
        'values': [float(val) for val in chart_df.values.tolist()]
    }

    # Filtering
    filtered_df = df.copy()
    if selected_location:
        filtered_df = filtered_df[filtered_df['location'] == selected_location]
    if selected_bhk:
        filtered_df = filtered_df[filtered_df['bhk'] == int(selected_bhk)]
    if selected_bath:
        filtered_df = filtered_df[filtered_df['bath'] == int(selected_bath)]

    total = len(filtered_df)
    total_pages = (total + per_page - 1) // per_page
    paged_df = filtered_df.iloc[offset:offset + per_page]

    stats = {
        'total': int(len(df)),
        'avg_price': round(float(df['price'].mean()), 2),
        'top_location': str(df['location'].value_counts().idxmax())
    }

    locations = sorted(df['location'].unique().tolist())

    return render_template("admin.html",
                           data=paged_df.to_dict(orient='records'),
                           stats=stats,
                           chart_data=chart_data,
                           locations=locations,
                           selected_location=selected_location,
                           selected_bhk=selected_bhk,
                           selected_bath=selected_bath,
                           page=page,
                           total_pages=total_pages)
@app.route('/admin/add-property', methods=['GET', 'POST'])
def add_property():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login_admin'))

    if request.method == 'POST':
        location = request.form['location']
        sqft = float(request.form['sqft'])
        bath = int(request.form['bath'])
        bhk = int(request.form['bhk'])
        price = float(request.form['price'])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO properties (location, sqft, bath, bhk, price) VALUES (?, ?, ?, ?, ?)",
                       (location, sqft, bath, bhk, price))
        conn.commit()
        conn.close()
        flash('✅ Property added successfully!')
        return redirect(url_for('admin'))

        return redirect(url_for('admin'))

    return render_template('add_property.html')

@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout_admin():
    session.pop('admin_logged_in', None)
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login_user'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error="Username already taken")
    return render_template('signup.html')

@app.route('/login-user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login_user.html', error="Invalid credentials")
    return render_template('login_user.html')

@app.route('/logout-user')
def logout_user():
    session.pop('user', None)
    return redirect(url_for('login_user'))

@app.route('/save-search', methods=['POST'])
def save_search():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    username = session['user']
    location = request.json.get('location')
    bhk = request.json.get('bhk')
    bath = request.json.get('bath')
    min_sqft = request.json.get('sqft')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    user_id = user[0]
    cursor.execute('''INSERT INTO saved_searches (user_id, location, bhk, bath, min_sqft) VALUES (?, ?, ?, ?, ?)''',
                   (user_id, location, bhk, bath, min_sqft))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Search saved successfully!'})

@app.route('/my-searches')
def my_searches():
    if 'user' not in session:
        return redirect(url_for('login_user'))
    username = session['user']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return "User not found", 404
    user_id = user[0]
    cursor.execute('''SELECT location, bhk, bath, min_sqft FROM saved_searches WHERE user_id = ? ORDER BY id DESC''', (user_id,))
    saved = cursor.fetchall()
    conn.close()
    return render_template('my_searches.html', searches=saved)

@app.route('/add-favorite', methods=['POST'])
def add_favorite():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    property_id = request.json.get('property_id')
    username = session['user']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    user_id = user[0]
    cursor.execute("SELECT * FROM favorites WHERE user_id = ? AND property_id = ?", (user_id, property_id))
    if cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Already added to favorites!'})
    cursor.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (user_id, property_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Property added to favorites!'})

@app.route('/remove-favorite', methods=['POST'])
def remove_favorite():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    property_id = request.json.get('property_id')
    username = session['user']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    user_id = user[0]
    cursor.execute("DELETE FROM favorites WHERE user_id = ? AND property_id = ?", (user_id, property_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Removed from favorites!'})

@app.route('/my-favorites')
def my_favorites():
    if 'user' not in session:
        return redirect(url_for('login_user'))
    username = session['user']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return "User not found", 404
    user_id = user[0]
    cursor.execute('''SELECT p.* FROM properties p JOIN favorites f ON f.property_id = p.id WHERE f.user_id = ?''', (user_id,))
    favorites = cursor.fetchall()
    conn.close()
    return render_template('my_favorites.html', favorites=favorites)

@app.route('/properties-page', methods=['GET', 'POST'])
def properties_page():
    if 'user' not in session:
        return redirect(url_for('login_user'))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    username = session['user']
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return "User not found", 404
    user_id = user[0]
    cursor.execute("SELECT DISTINCT location FROM properties ORDER BY location ASC")
    locations = [row[0] for row in cursor.fetchall()]
    base_query = "SELECT * FROM properties WHERE 1=1"
    filters = {'location': 'All', 'bhk': 'All', 'bath': 'All', 'sort_by': 'default', 'min_price': '', 'max_price': ''}
    params = []
    if request.method == 'POST':
        filters['location'] = request.form.get('location', 'All')
        filters['bhk'] = request.form.get('bhk', 'All')
        filters['bath'] = request.form.get('bath', 'All')
        filters['sort_by'] = request.form.get('sort_by', 'default')
        filters['min_price'] = request.form.get('min_price', '')
        filters['max_price'] = request.form.get('max_price', '')
    if filters['location'] != 'All':
        base_query += " AND location = ?"
        params.append(filters['location'])
    if filters['bhk'] != 'All':
        base_query += " AND bhk = ?"
        params.append(int(filters['bhk']))
    if filters['bath'] != 'All':
        base_query += " AND bath = ?"
        params.append(int(filters['bath']))
    if filters['min_price']:
        base_query += " AND price >= ?"
        params.append(float(filters['min_price']))
    if filters['max_price']:
        base_query += " AND price <= ?"
        params.append(float(filters['max_price']))
    sort_clause = ""
    if filters['sort_by'] == 'price':
        sort_clause = " ORDER BY price ASC"
    elif filters['sort_by'] == 'sqft':
        sort_clause = " ORDER BY sqft DESC"
    elif filters['sort_by'] == 'bhk':
        sort_clause = " ORDER BY bhk DESC"
    final_query = base_query + sort_clause
    if request.form.get("export") == "csv":
        df = pd.read_sql_query(final_query, conn, params=params)
        csv_path = os.path.join("static", "export.csv")
        df.to_csv(csv_path, index=False)
        conn.close()
        return redirect(url_for('static', filename='export.csv'))
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    count_query = f"SELECT COUNT(*) FROM ({base_query})"
    total = cursor.execute(count_query, params).fetchone()[0]
    final_query += " LIMIT ? OFFSET ?"
    cursor.execute(final_query, params + [per_page, offset])
    properties = cursor.fetchall()
    cursor.execute("SELECT property_id FROM favorites WHERE user_id = ?", (user_id,))
    favorites = [row[0] for row in cursor.fetchall()]
    conn.close()
    total_pages = (total + per_page - 1) // per_page
    return render_template("properties_page.html",
                           properties=properties,
                           locations=locations,
                           filters=filters,
                           page=page,
                           total_pages=total_pages,
                           favorites=favorites,
                           total_results=total)
@app.route('/admin/edit/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login_admin'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == 'POST':
        location = request.form['location']
        sqft = float(request.form['sqft'])
        bath = int(request.form['bath'])
        bhk = int(request.form['bhk'])
        price = float(request.form['price'])

        cursor.execute('''
            UPDATE properties
            SET location = ?, sqft = ?, bath = ?, bhk = ?, price = ?
            WHERE id = ?
        ''', (location, sqft, bath, bhk, price, property_id))
        conn.commit()
        conn.close()

        flash("✅ Property updated successfully!", "success")
        return redirect(url_for('admin'))

    cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
    prop = cursor.fetchone()
    conn.close()

    if not prop:
        return "Property not found", 404

    property_data = {
        'id': prop[0],
        'location': prop[1],
        'sqft': prop[2],
        'bath': prop[3],
        'bhk': prop[4],
        'price': prop[5]
    }

    return render_template('edit_property.html', property=property_data)


@app.route('/admin/delete/<int:property_id>', methods=['POST'])
def delete_property(property_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login_admin'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    conn.commit()
    conn.close()

    flash("🗑️ Property deleted successfully!", "success")
    return redirect(url_for('admin'))
@app.route('/admin/listings')
def admin_listings_partial():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login_admin'))

    location = request.args.get('location', '')
    bhk = request.args.get('bhk', '')
    bath = request.args.get('bath', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Base query and filters
    base_query = "SELECT * FROM properties WHERE 1=1"
    params = []

    if location:
        base_query += " AND location = ?"
        params.append(location)
    if bhk:
        base_query += " AND bhk = ?"
        params.append(int(bhk))
    if bath:
        base_query += " AND bath = ?"
        params.append(int(bath))

    count_query = f"SELECT COUNT(*) FROM ({base_query})"
    total = cursor.execute(count_query, params).fetchone()[0]
    total_pages = (total + per_page - 1) // per_page

    # Fetch data with pagination
    final_query = base_query + " LIMIT ? OFFSET ?"
    cursor.execute(final_query, params + [per_page, offset])
    data = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()

    return render_template("admin_table.html",
                           data=data,
                           page=page,
                           total_pages=total_pages,
                           selected_location=location)

if __name__ == '__main__':
    app.run(debug=True)
