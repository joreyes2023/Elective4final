from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
from dotenv import load_dotenv
import os
import ssl

# Load environment variables from .env if available
load_dotenv()

# MongoDB connection
default_uri = 'mongodb://localhost:27017/'
mongo_uri = os.getenv('MONGODB_URI', default_uri)

# Avoid connecting to placeholder Atlas URI if .env has not been configured yet
if any(tag in mongo_uri for tag in ['<username>', '<password>', '<cluster-url>']):
    mongo_uri = default_uri

# MongoDB connection options for better SSL/TLS handling
connection_kwargs = {
    'serverSelectionTimeoutMS': 30000,
    'connectTimeoutMS': 30000,
    'socketTimeoutMS': 30000,
    'retryWrites': True,
}

# Add SSL options for Atlas if needed
if 'mongodb+srv://' in mongo_uri:
    connection_kwargs['ssl'] = True

try:
    client = MongoClient(mongo_uri, **connection_kwargs)
    # Test the connection
    client.server_info()
    db = client['bsit_database']
    print("✓ Connected to MongoDB successfully")
except (ServerSelectionTimeoutError, ConfigurationError, Exception) as e:
    print(f"⚠ Warning: Could not connect to Atlas ({str(e)[:100]}...)")
    print("  Falling back to local MongoDB...")
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client['bsit_database']
        print("✓ Connected to local MongoDB")
    except Exception as local_err:
        print(f"✗ Local MongoDB also unavailable: {local_err}")
        # Still create client object for graceful degradation
        client = MongoClient(default_uri)
        db = client['bsit_database']


# Collections
users_collection = db['users']
students_collection = db['students']

# Initialize default users if not exist
def initialize_default_users():
    try:
        default_users = [
            {
                "email": "admin@gmail.com",
                "name": "Admin",
                "password": "admin123",
                "role": "admin",
            },
            {
                "email": "faculty@gmail.com",
                "name": "Faculty",
                "password": "faculty123",
                "role": "faculty",
            },
            {
                "email": "registrar@gmail.com",
                "name": "Registrar",
                "password": "registrar123",
                "role": "registrar",
            },
            {
                "email": "student@gmail.com",
                "name": "Juan Dela Cruz",
                "password": "student123",
                "role": "student",
                "student_id": "2021001"
            },
             {
                "email": "Anating@gmail.com",
                "name": "Anating",
                "password": "anating123",
                "role": "student",
                "student_id": "2021002"
            },
             {
                "email": "Alegre@gmail.com",
                "name": "Alegre",
                "password": "alegre123",
                "role": "student",
                "student_id": "2021003"
            },
             {
                "email": "Reyes@gmail.com",
                "name": "Reyes",
                "password": "reyes123",
                "role": "student",
                "student_id": "2021004"
            },
        ]
        
        # Add missing users
        for user in default_users:
            if not users_collection.find_one({"email": user["email"]}):
                users_collection.insert_one(user)
        
        print("✓ Default users initialized/verified")
    except Exception as e:
        print(f"⚠ Could not initialize default users: {str(e)[:100]}")

# Initialize default students if not exist
def initialize_default_students():
    try:
        default_students = [
            {
                "_id": "2021001",
                "student_id": "2021001",
                "Name": "Juan Dela Cruz",
                "email": "student@gmail.com",
                "Course": "BSIT",
                "YearLevel": "3rd Year",
                "Grades": {
                    "Programming": 90,
                    "Database": 85,
                    "Networking": 88,
                    "Web Dev": 92
                },
                "Status": {
                    "Programming": "PASS",
                    "Database": "PASS",
                    "Networking": "PASS",
                    "Web Dev": "PASS"
                },
                "gpa": 88.75,
                "profile_image": ""
            },
            {
                "_id": "2021002",
                "student_id": "2021002",
                "Name": "Anating",
                "email": "Anating@gmail.com",
                "Course": "BSIT",
                "YearLevel": "2nd Year",
                "Grades": {
                    "Programming": 88,
                    "Database": 86,
                    "Networking": 89,
                    "Web Dev": 85
                },
                "Status": {
                    "Programming": "PASS",
                    "Database": "PASS",
                    "Networking": "PASS",
                    "Web Dev": "PASS"
                },
                "gpa": 87.0,
                "profile_image": ""
            },
            {
                "_id": "2021003",
                "student_id": "2021003",
                "Name": "Alegre",
                "email": "Alegre@gmail.com",
                "Course": "BSIT",
                "YearLevel": "1st Year",
                "Grades": {
                    "Programming": 82,
                    "Database": 84,
                    "Networking": 81,
                    "Web Dev": 83
                },
                "Status": {
                    "Programming": "PASS",
                    "Database": "PASS",
                    "Networking": "PASS",
                    "Web Dev": "PASS"
                },
                "gpa": 82.5,
                "profile_image": ""
            },
            {
                "_id": "2021004",
                "student_id": "2021004",
                "Name": "Reyes",
                "email": "Reyes@gmail.com",
                "Course": "BSIT",
                "YearLevel": "3rd Year",
                "Grades": {
                    "Programming": 91,
                    "Database": 89,
                    "Networking": 90,
                    "Web Dev": 93
                },
                "Status": {
                    "Programming": "PASS",
                    "Database": "PASS",
                    "Networking": "PASS",
                    "Web Dev": "PASS"
                },
                "gpa": 90.75,
                "profile_image": ""
            }
        ]
        
        # Add missing students
        for student in default_students:
            if not students_collection.find_one({"_id": student["_id"]}):
                students_collection.insert_one(student)
        
        print("✓ Default students initialized/verified")
    except Exception as e:
        print(f"⚠ Could not initialize default students: {str(e)[:100]}")

# Call initialization with error handling
try:
    initialize_default_users()
    initialize_default_students()
except Exception as e:
    print(f"⚠ Initialization warning (app will still run): {e}")