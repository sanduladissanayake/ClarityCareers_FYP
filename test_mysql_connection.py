import pymysql
import sys

try:
    # Connect to MySQL
    print("Connecting to MySQL at localhost:3306...")
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        port=3306,
        connect_timeout=5
    )
    print("✓ Connected to MySQL successfully!")
    
    # Check if claritycareers database exists
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES LIKE 'claritycareers'")
    result = cursor.fetchone()
    
    if result:
        print("✓ claritycareers database EXISTS")
    else:
        print("✗ claritycareers database NOT FOUND - will be created")
    
    # Show all databases
    print("\nAvailable databases:")
    cursor.execute("SHOW DATABASES")
    for db in cursor.fetchall():
        print(f"  - {db[0]}")
    
    cursor.close()
    conn.close()
    
except pymysql.Error as e:
    print(f"✗ MySQL Connection Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
