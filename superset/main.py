import pandas as pd
import sqlite3
import requests
from flask import Flask
from superset.app import create_app
import json
from superset_items import DashboardItems

API_URL = "http://localhost:8088/api/v1"
app = create_app()


with app.app_context():
    from superset.models.core import Database
    from superset import db
    
    # Query to check if the database already exists
    existing_db = db.session.query(Database).filter_by(database_name="SQLite Example").first()
    if not existing_db:
        # Create and add the SQLite database to Superset only if it does not exist
        database = Database(
            database_name="SQLite Example",
            sqlalchemy_uri="sqlite:////Users/ivanpedroza/Documents/Dashboard/example.db"
        )
        db.session.add(database)
        db.session.commit()
    else:
        print("Database already exists. Skipping creation.")

    # Load CSV data into a DataFrame
    data = pd.read_csv('./dash_ready_watch_data.csv')

    # Connect to SQLite database (create it if it doesn't exist) 
    conn = sqlite3.connect('/Users/ivanpedroza/Documents/Dashboard/example.db')
    data.to_sql('test_table', con=conn, if_exists='replace', index=False)
    conn.close()  

    

    # Get an auth token and headers
    auth_response = requests.post(f"{API_URL}/security/login", json={
        "password": "admin",
        "provider": "db",
        "refresh": True,
        "username": "admin"
    })
    response = auth_response.json()

    
    # Extract the access token and CSRF token
    auth_token = response['access_token']
    csrf_token = response['refresh_token']  # Adjust this if the CSRF token is sent under a different key

    # Headers for the subsequent requests
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token  # Include CSRF token in the request headers
    }


    # --------------------------------------------------------- start posting to dashboard -----------------------------------------------------------
    # Create the dataset by pulling it from the database
    create_dataset = requests.post(f"{API_URL}/dataset/", headers=headers, json=DashboardItems.create_dataset())
    
    # Create the dashboard
    dash_response = requests.post(f"{API_URL}/dashboard/", headers=headers, json=DashboardItems.create_dashboard())
    dashboard_id = dash_response.json()['id']


    # Create a sample chart
    create_chart_response = requests.post(
        f"{API_URL}/chart/",
        headers=headers,
        json=DashboardItems.create_chart()
    )


    # Update the dashboard with new chart
    update_dashboard_response = requests.put(
        f"{API_URL}/dashboard/{dashboard_id}",
        headers=headers,
        json=DashboardItems.update_dashboard("{}")
    )

    print(update_dashboard_response.json())
