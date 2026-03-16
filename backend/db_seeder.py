import pandas as pd
import mysql.connector
from mysql.connector import Error as MySQLError
from datetime import datetime, timedelta


def normalize_seed_columns(frame):
    frame = frame.copy()
    frame.columns = [column.strip().lower() for column in frame.columns]
    if 'customer_name' not in frame.columns and 'name' in frame.columns:
        frame['customer_name'] = frame['name']
    if 'email_address' not in frame.columns and 'email' in frame.columns:
        frame['email_address'] = frame['email']
    return frame

# 1. Load CSV data
df = normalize_seed_columns(pd.read_csv('customer_churn_dataset.csv'))

# 2. Convert last_login_days to actual dates (dynamic calculation)
df['last_login_date'] = df['last_login_days'].apply(
    lambda days: (datetime.now() - timedelta(days=int(days))).strftime('%Y-%m-%d')
)

# 2. MySQL Connection with error handling
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sandhyaa",
        database="churn_db",
        auth_plugin='mysql_native_password'
    )
    cursor = db.cursor()
    print(f"✅ Connected to MySQL database 'churn_db'")
except MySQLError as err:
    print(f"❌ MySQL Connection Error: {err}")
    exit(1)

# 3. Clear existing data to prevent duplicates
try:
    cursor.execute("TRUNCATE TABLE customers")
    print(f"🗑️  Cleared existing data from 'customers' table")
except MySQLError as err:
    print(f" Warning: Could not clear table - {err}")

# 4. Insert all columns from CSV + calculated date
try:
    for _, row in df.iterrows():
        sql = """INSERT INTO customers (
            customer_id, customer_name, email_address, tenure_months, 
            last_login_days, last_login_date, login_frequency, avg_session_duration, 
            feature_usage_count, monthly_active_days, usage_drop_flag, 
            subscription_type, monthly_charges, payment_failures, 
            discount_applied, support_ticket_count, unresolved_tickets, 
            churn, health_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        # Map all row values (19 columns - includes last_login_date)
        values = (
            row['customer_id'],
            row['customer_name'],
            row['email_address'],
            row['tenure_months'],
            row['last_login_days'],
            row['last_login_date'],
            row['login_frequency'],
            row['avg_session_duration'],
            row['feature_usage_count'],
            row['monthly_active_days'],
            row['usage_drop_flag'],
            row['subscription_type'],
            row['monthly_charges'],
            row['payment_failures'],
            row['discount_applied'],
            row['support_ticket_count'],
            row['unresolved_tickets'],
            row['churn'],
            row['health_score'],
        )
        cursor.execute(sql, values)

    db.commit()
    print(f"✅ Successfully imported {len(df)} records into 'customers' table!")
    print(f"📅 Dynamic Date Calculation: last_login_date will update daily")
    print(f"   Example: If today is {datetime.now().strftime('%Y-%m-%d')}, inactive 55 days shows {(datetime.now() - timedelta(days=55)).strftime('%Y-%m-%d')}")
except MySQLError as err:
    print(f"❌ MySQL Insert Error: {err}")
    db.rollback()
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    cursor.close()
    db.close()