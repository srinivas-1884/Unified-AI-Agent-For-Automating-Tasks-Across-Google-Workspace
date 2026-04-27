# setup_mongodb.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

load_dotenv()

print("🔧 Setting up MongoDB for Workspace Agent...")
print("=" * 50)

# Connect to MongoDB
uri = os.getenv('MONGO_URI')
client = MongoClient(uri)
db = client.get_default_database()  # Uses database name from URI

# Create friends collection with validation
try:
    db.create_collection('friends')
    print("✅ Created 'friends' collection")
except Exception as e:
    print("ℹ️ 'friends' collection already exists")

# Create indexes for better performance
friends = db.friends

# Unique index on user_id + name (case-insensitive)
try:
    friends.create_index(
        [("user_id", ASCENDING), ("name", ASCENDING)],
        unique=True,
        collation={'locale': 'en', 'strength': 2}  # Case-insensitive
    )
    print("✅ Created unique index on user_id + name")
except DuplicateKeyError:
    print("ℹ️ Index on user_id + name already exists")

# Index for searching by email
try:
    friends.create_index([("user_id", ASCENDING), ("email", ASCENDING)])
    print("✅ Created index on user_id + email")
except:
    print("ℹ️ Index on user_id + email already exists")

# Index for timestamp queries
try:
    friends.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    print("✅ Created index on user_id + created_at")
except:
    print("ℹ️ Index on user_id + created_at already exists")

print("\n✅ MongoDB setup complete!")
print(f"📊 Database: {db.name}")
print(f"📊 Collections: {db.list_collection_names()}")
print("=" * 50)