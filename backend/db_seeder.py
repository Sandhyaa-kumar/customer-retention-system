import pandas as pd
import mysql.connector
from mysql.connector import Error as MySQLError

# 1. Load CSV data
df = pd.read_csv('customer_churn_dataset.csv')

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

# 4. Insert all columns from CSV
try:
    for _, row in df.iterrows():
        sql = """INSERT INTO customers (
            customer_id, Customer_Name, Email_Address, tenure_months, 
            last_login_days, login_frequency, avg_session_duration, 
            feature_usage_count, monthly_active_days, usage_drop_flag, 
            subscription_type, monthly_charges, payment_failures, 
            discount_applied, support_ticket_count, unresolved_tickets, 
            churn, health_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        # Map all row values (18 columns)
        values = tuple(row)
        cursor.execute(sql, values)

    db.commit()
    print(f"✅ Successfully imported {len(df)} records into 'customers' table!")
except MySQLError as err:
    print(f"❌ MySQL Insert Error: {err}")
    db.rollback()
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    cursor.close()
    db.close()