"""
Database Configuration Module
Handles MySQL connection with comprehensive error handling.
"""

import mysql.connector
from mysql.connector import Error as MySQLError


def get_db_connection():
    """
    Establishes MySQL connection with comprehensive error handling.
    Handles authentication errors gracefully.
    
    Returns:
        mysql.connector.connection: Active database connection
        
    Raises:
        Exception: If connection fails with detailed error message
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sandhyaa",  # ⚠️ Change this to your actual MySQL password
            database="churn_db",
            auth_plugin='mysql_native_password'  # For MySQL 8.0+ compatibility
        )
        return conn
    except MySQLError as err:
        if err.errno == 1045:  # Access Denied Error
            print(f"❌ MySQL Access Denied: Incorrect username or password.")
            raise Exception("Database authentication failed. Please check MySQL credentials.")
        elif err.errno == 2003:  # Can't Connect
            print(f"❌ MySQL Connection Error: Cannot connect to database server.")
            raise Exception("Database server is not running or unreachable.")
        elif err.errno == 1049:  # Unknown Database
            print(f"❌ MySQL Error: Database 'churn_db' does not exist.")
            raise Exception("Database 'churn_db' not found. Please create it first.")
        else:
            print(f"❌ MySQL Error [{err.errno}]: {err}")
            raise Exception(f"Database connection error: {err.msg}")
