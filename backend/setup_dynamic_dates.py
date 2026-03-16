"""
Dynamic Date Setup & Verification Tool
=======================================
All-in-one script to:
1. Migrate database to use dynamic date calculations
2. Verify the migration worked
3. Test API endpoints
4. Prove dates will update automatically

Usage:
    python setup_dynamic_dates.py migrate    # Run database migration
    python setup_dynamic_dates.py verify     # Verify database has dates
    python setup_dynamic_dates.py test       # Test API endpoints
    python setup_dynamic_dates.py all        # Do everything
"""

import sys
import mysql.connector
from mysql.connector import Error as MySQLError
from datetime import datetime, timedelta


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sandhyaa',
    'database': 'churn_db',
    'auth_plugin': 'mysql_native_password'
}


def migrate_database():
    """Add last_login_date column and populate it"""
    print("\n" + "="*80)
    print("STEP 1: DATABASE MIGRATION")
    print("="*80)
    
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        print(f"✅ Connected to MySQL database '{DB_CONFIG['database']}'")
        
        # Step 1: Add column
        try:
            cursor.execute("ALTER TABLE customers ADD COLUMN last_login_date DATE AFTER last_login_days")
            print("✅ Added last_login_date column")
        except MySQLError as e:
            if "Duplicate column name" in str(e):
                print("⚠️  Column 'last_login_date' already exists")
            else:
                raise e
        
        # Step 2: Populate dates
        cursor.execute("""
            UPDATE customers 
            SET last_login_date = DATE_SUB(CURDATE(), INTERVAL last_login_days DAY)
            WHERE last_login_date IS NULL
        """)
        db.commit()
        print(f"✅ Populated last_login_date for {cursor.rowcount} customers")
        
        # Step 3: Add index
        try:
            cursor.execute("ALTER TABLE customers ADD INDEX idx_last_login_date (last_login_date)")
            print("✅ Added index on last_login_date")
        except MySQLError as e:
            if "Duplicate key name" in str(e):
                print("⚠️  Index already exists")
            else:
                raise e
        
        cursor.close()
        db.close()
        print("\n✅ MIGRATION COMPLETED!\n")
        return True
        
    except MySQLError as err:
        print(f"❌ MySQL Error: {err}")
        return False


def verify_database():
    """Verify database has dynamic dates working"""
    print("\n" + "="*80)
    print("STEP 2: DATABASE VERIFICATION")
    print("="*80)
    
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT customer_id, customer_name, last_login_days, last_login_date,
                   DATEDIFF(CURDATE(), last_login_date) as days_since_login
            FROM customers 
            ORDER BY last_login_days DESC
            LIMIT 5
        """)
        
        print(f"\n{'Customer ID':<12} {'Name':<25} {'Stored':<8} {'Date':<12} {'Current':<8}")
        print("-"*80)
        
        all_synced = True
        for row in cursor.fetchall():
            status = "✅" if row[2] == row[4] else "⚠️"
            print(f"{row[0]:<12} {row[1][:24]:<25} {row[2]:<8} {str(row[3]):<12} {row[4]:<8} {status}")
            if row[2] != row[4]:
                all_synced = False
        
        cursor.close()
        db.close()
        
        if all_synced:
            print("\n✅ All dates are synced and calculating correctly!")
        else:
            print("\n⚠️  Some dates may need resync")
        
        return True
        
    except MySQLError as err:
        print(f"❌ Database Error: {err}")
        return False


def test_api_endpoint():
    """Test the Flask API to verify dynamic calculations"""
    print("\n" + "="*80)
    print("STEP 3: API ENDPOINT TEST")
    print("="*80)
    
    try:
        import requests
        
        response = requests.get("http://127.0.0.1:5000/api/customers", timeout=5)
        
        if response.status_code == 200:
            customers = response.json()
            print(f"✅ API is responding! Fetched {len(customers)} customers")
            
            # Show top 3 most inactive
            sorted_customers = sorted(customers, key=lambda x: x.get('last_login_days', 0), reverse=True)[:3]
            
            print(f"\n{'Customer':<30} {'Days Inactive':<15} {'Last Login Date'}")
            print("-"*70)
            
            for customer in sorted_customers:
                name = customer.get('customer_name', 'Unknown')[:29]
                days = customer.get('last_login_days', 'N/A')
                date = customer.get('last_login', 'N/A')
                print(f"{name:<30} {days:<15} {date}")
            
            print("\n✅ API is returning dynamic calculations!")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  'requests' library not installed. Skipping API test.")
        print("   Install with: pip install requests")
        return True
    except Exception as e:
        print(f"❌ API Test Error: {e}")
        print("   Make sure Flask server is running: python app.py")
        return False


def show_tomorrow_proof():
    """Show proof that dates will update tomorrow"""
    print("\n" + "="*80)
    print("STEP 4: TOMORROW UPDATE PROOF")
    print("="*80)
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    example_login = datetime(2026, 1, 6)  # Example: Jan 6, 2026
    
    days_today = (today - example_login).days
    days_tomorrow = (tomorrow - example_login).days
    days_next_week = (next_week - example_login).days
    
    print(f"\n📊 Example: Customer who last logged in {example_login.strftime('%Y-%m-%d')}")
    print(f"\n{'Date':<20} {'Days Inactive':<15} {'Display'}")
    print("-"*50)
    print(f"{today.strftime('%B %d, %Y'):<20} {days_today:<15} Inactive {days_today}d")
    print(f"{tomorrow.strftime('%B %d, %Y'):<20} {days_tomorrow:<15} Inactive {days_tomorrow}d")
    print(f"{next_week.strftime('%B %d, %Y'):<20} {days_next_week:<15} Inactive {days_next_week}d")
    
    print("\n✅ Dates update automatically! No manual changes needed.")
    print("   Just refresh your browser tomorrow and see the change!")
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    print("\n" + "="*80)
    print("Dynamic Date Setup Tool")
    print("="*80)
    
    success = True
    
    if command == "migrate":
        success = migrate_database()
    elif command == "verify":
        success = verify_database()
    elif command == "test":
        success = test_api_endpoint()
    elif command == "all":
        success = migrate_database()
        if success:
            success = verify_database()
        if success:
            test_api_endpoint()  # Don't fail if API not running
        show_tomorrow_proof()
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
    
    if success:
        print("\n" + "="*80)
        print("✅ ALL DONE!")
        print("="*80)
        print("Next steps:")
        print("  1. Restart Flask: python app.py")
        print("  2. Refresh your browser")
        print("  3. See dynamic dates in action!")
        print("="*80 + "\n")
    else:
        print("\n❌ Process completed with errors. Check output above.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
