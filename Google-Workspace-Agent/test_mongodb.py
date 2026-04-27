# test_mongodb.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pymongo
import sys

load_dotenv()

print("🔧 Testing MongoDB Atlas Connection...")
print("=" * 50)

# Get connection string
uri = os.getenv('MONGO_URI')
if not uri:
    print("❌ MONGO_URI not found in .env file")
    sys.exit(1)

# Mask password for printing
safe_uri = uri.replace(uri.split(':')[2].split('@')[0], '****') if '@' in uri else uri
print(f"Connection string: {safe_uri}")

try:
    # Connect with timeout
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    
    # Test connection
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
    # Get database info
    db_name = uri.split('/')[-1].split('?')[0] if '?' in uri else uri.split('/')[-1]
    db = client[db_name or 'workspace_agent']
    
    # Test write operation
    test_collection = db.test_connection
    test_collection.insert_one({"test": "data", "timestamp": "now"})
    print("✅ Successfully wrote test data")
    
    # Test read operation
    count = test_collection.count_documents({})
    print(f"✅ Test collection has {count} documents")
    
    # Clean up
    test_collection.drop()
    print("✅ Test data cleaned up")
    
    # List collections
    collections = db.list_collection_names()
    print(f"📊 Available collections: {collections}")
    
    client.close()
    print("\n✅ All tests passed! MongoDB is working correctly.")
    
except pymongo.errors.OperationFailure as e:
    print(f"\n❌ Authentication failed: {e}")
    print("\n🔧 FIX THIS BY:")
    print("1. Check your username and password in .env")
    print("2. If password has special chars, URL encode them:")
    print("   @ → %40, # → %23, $ → %24, % → %25, & → %26")
    print("3. Or create a new database user with simple password")
    
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"\n❌ Connection timeout: {e}")
    print("\n🔧 FIX THIS BY:")
    print("1. Go to MongoDB Atlas → Network Access")
    print("2. Click 'Add IP Address' → 'Add Current IP Address'")
    print("3. Wait 2 minutes and try again")
    print("4. If still failing, temporarily add 0.0.0.0/0 for testing")
    
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    print("\n🔧 Check your internet connection and firewall settings")