import streamlit as st
from db import users_collection, students_collection

# ---------------- LOGIN ----------------
def verify_login(email, password):
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        return {"email": user["email"], "role": user["role"], "name": user.get("name", ""), "student_id": user.get("student_id")}
    return None

# ---------------- CREATE USER ----------------
def create_user(email, password, role, name="", student_id=""):
    if users_collection.find_one({"email": email}):
        return False

    user_data = {
        "email": email,
        "password": password,
        "role": role,
        "name": name
    }

    if role == "student" and student_id:
        user_data["student_id"] = student_id

    users_collection.insert_one(user_data)
    return True

# ---------------- DELETE USER ----------------
def delete_user(email):
    users_collection.delete_one({"email": email})

# ---------------- GET USERS ----------------
def get_users():
    users = {}
    for user in users_collection.find():
        users[user["email"]] = {
            "name": user.get("name", ""),
            "password": user["password"],
            "role": user["role"]
        }
    return users

# ---------------- SESSION ----------------
def set_current_user(user):
    st.session_state["user"] = user

def get_current_user():
    return st.session_state.get("user")

def sign_out():
    if "user" in st.session_state:
        del st.session_state["user"]

# ---------------- CREATE STUDENT ACCOUNT ----------------
def create_student_account(email, password, name, program, year_level):
    """Create a student user account and student record"""
    if users_collection.find_one({"email": email}):
        return False, "Email already exists"
    
    # Generate a new student ID (auto-increment from existing ones)
    last_user = users_collection.find_one(sort=[("student_id", -1)])
    new_student_id = str(int(last_user.get("student_id", "2020000")) + 1) if last_user and last_user.get("student_id") else "2021001"
    
    # Create user account
    user_data = {
        "email": email,
        "password": password,
        "role": "student",
        "name": name,
        "student_id": new_student_id
    }
    
    try:
        # Insert user account
        users_collection.insert_one(user_data)
        
        # Create corresponding student record
        student_data = {
            "_id": new_student_id,
            "Name": name,
            "email": email,
            "Course": program,
            "YearLevel": year_level,
            "Grades": {},
            "Status": {},
            "profile_image": "",
            "registration_date": st.session_state.get("_timestamp", "")
        }
        
        students_collection.insert_one(student_data)
        return True, new_student_id
    except Exception as e:
        # If student record fails, try to delete the user account
        try:
            users_collection.delete_one({"email": email})
        except:
            pass
        return False, str(e)