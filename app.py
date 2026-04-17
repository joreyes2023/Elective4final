import streamlit as st
from auth import (
    verify_login,
    create_user,
    delete_user,
    get_users,
    set_current_user,
    get_current_user,
    sign_out,
    create_student_account,
)
from db import students_collection
import base64
from io import BytesIO
from PIL import Image

# ---------- CONFIG ----------
st.set_page_config(page_title="HCCCI Student Analytics", layout="wide", page_icon="🎓")

# ---------- GRAY THEME WITH BLUE ACCENTS ----------
st.markdown("""
<style>
/* BODY & FONT */
body {
    background-color: #f5f5f5;
    color: #333333;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* HEADERS */
h1, h2, h3, h4 {
    color: #1e3a8a;
    text-shadow: none;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #e8e8e8;
    border-right: 2px solid #5a7fb8;
}

/* Sidebar text and labels */
[data-testid="stSidebar"] {
    color: #333333 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    font-weight: bold;
    color: #333333;
    padding: 0.4rem;
    transition: 0.2s;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    color: #1e3a8a;
    background-color: rgba(94, 177, 242, 0.1);
}

/* Restricted badge */
.restricted-badge {
    font-size: 0.7rem;
    background: #5a7fb8;
    color: #fff;
    padding: 2px 6px;
    border-radius: 5px;
    margin-left: 5px;
}

/* Card style for dashboards */
.css-1d391kg { 
    background-color: #e8e8e8 !important;
    border: 1px solid #5a7fb8;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    color: #333333 !important;
}

/* Tables */
.stDataFrame {
    border: 1px solid #5a7fb8;
    border-radius: 8px;
}

.stTable {
    color: #333333 !important;
}

/* Buttons - Blue gradient style */
button {
    background: linear-gradient(135deg, #5eb1f2 0%, #a855f7 100%) !important;
    color: #ffffff !important;
    font-weight: bold;
    border-radius: 8px !important;
    border: none !important;
}

button:hover {
    background: linear-gradient(135deg, #4a9fd9 0%, #9740e8 100%) !important;
}

/* Input fields */
input, textarea, select {
    background-color: #e8e8e8 !important;
    color: #333333 !important;
    border: 1px solid #5a7fb8 !important;
}

input::placeholder {
    color: #999999 !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: #1e3a8a !important;
    text-shadow: none;
}

[data-testid="stMetricLabel"] {
    color: #555555 !important;
}

/* Divider */
.css-1emrehy {
    border-top: 1px solid #5a7fb8;
    box-shadow: none;
}

/* Text visibility */
p, label, span, div {
    color: #333333 !important;
}

/* Links */
a {
    color: #1e3a8a !important;
    text-decoration: none;
}

a:hover {
    color: #5eb1f2 !important;
    text-decoration: underline;
}

/* Info/Warning/Success boxes */
.stInfo {
    background-color: #d1fae5 !important;
    border-left: 4px solid #10b981 !important;
    color: #065f46 !important;
}

.stSuccess {
    background-color: #d1fae5 !important;
    border-left: 4px solid #10b981 !important;
    color: #065f46 !important;
}

.stWarning {
    background-color: #fef3c7 !important;
    border-left: 4px solid #f59e0b !important;
    color: #92400e !important;
}

.stError {
    background-color: #fee2e2 !important;
    border-left: 4px solid #ef4444 !important;
    color: #7f1d1d !important;
}

/* Tabs */
[data-testid="stTabs"] {
    color: #333333 !important;
}

/* Select boxes and dropdowns */
.stSelectbox, .stMultiSelect {
    color: #333333 !important;
}

/* Forms */
.stForm {
    background-color: #e8e8e8 !important;
    border: 1px solid #5a7fb8 !important;
    border-radius: 8px !important;
    padding: 20px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------- STUDENT DATA FUNCTIONS ----------
def get_students_for_role(user):
    """Get students based on user role with limitations"""
    role = user["role"]

    if role == "admin":
        # Admin can see all students
        return list(students_collection.find())
    elif role == "registrar":
        # Registrar can see all students
        return list(students_collection.find())
    elif role == "faculty":
        # Faculty can see students (in this simple version, all students)
        # In a real system, this would be filtered by assigned courses
        return list(students_collection.find())
    elif role == "student":
        # Student can only see their own record
        student_id = user.get("student_id")
        if student_id:
            student = students_collection.find_one({"_id": student_id})
            return [student] if student else []
        return []
    return []

def get_student_by_id(student_id):
    """Get a specific student by ID"""
    return students_collection.find_one({"_id": student_id})

# ---------- LOGIN PAGE ----------
def login_page():
    st.title("🎓 HCCCI Student Analytics System")
    
    # Tab for login and registration
    tab1, tab2 = st.tabs(["Login", "Create Student Account"])
    
    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            user = verify_login(email, password)
            if user:
                set_current_user(user)
                st.rerun()
            else:
                st.error("Invalid login credentials")
    
    with tab2:
        st.subheader("Create a New Student Account")
        st.write("Fill in the form below to register as a student.")
        
        with st.form("student_registration_form"):
            name = st.text_input("Full Name", placeholder="Juan Dela Cruz")
            email = st.text_input("Email Address", placeholder="student@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter a strong password")
            password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            program = st.selectbox("Program", ["BSIT", "BSCS", "BSBA", "BSE"])
            year_level = st.selectbox("Year Level", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
            
            submitted = st.form_submit_button("Create Account", type="primary")
            
            if submitted:
                # Validation
                if not name or not email or not password:
                    st.error("Please fill in all required fields")
                elif password != password_confirm:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    success, result = create_student_account(email, password, name, program, year_level)
                    if success:
                        st.success(f"✓ Account created successfully!")
                        st.success(f"Your Student ID: **{result}**")
                        st.info("You can now login with your email and password.")
                    else:
                        st.error(f"Error creating account: {result}")

# ---------- DASHBOARDS ----------
def admin_dashboard():
    st.header("👑 Admin Dashboard")
    tab1, tab2, tab3 = st.tabs(["Create User", "Manage Users", "Student Records"])

    with tab1:
        st.subheader("Create User")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["student", "faculty", "registrar"])
        name = st.text_input("Name")
        student_id = ""
        if role == "student":
            student_id = st.text_input("Student ID")
        if st.button("Create Account"):
            if create_user(email, password, role, name, student_id):
                st.success("User created successfully")
            else:
                st.error("User already exists")

    with tab2:
        st.subheader("System Users")
        users = get_users()
        for email, info in users.items():
            col1, col2, col3 = st.columns([4, 2, 1])
            col1.write(f"{email} ({info['name']})")
            col2.write(info["role"])
            if col3.button("Delete", key=email):
                delete_user(email)
                st.rerun()

    with tab3:
        st.subheader("All Student Records")

        # Search and filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("Search by Name", placeholder="Enter student name...")
        with col2:
            filter_course = st.selectbox("Filter by Course", ["All Courses", "Information Technology", "Computer Science", "Business Administration", "Engineering"])
        with col3:
            filter_year = st.selectbox("Filter by Year", ["All Years", "1", "2", "3", "4"])

        # Get all students
        all_students = get_students_for_role({"role": "admin"})

        # Apply filters
        filtered_students = all_students
        if search_name:
            filtered_students = [s for s in filtered_students if search_name.lower() in s.get("Name", "").lower()]
        if filter_course != "All Courses":
            filtered_students = [s for s in filtered_students if s.get("Course") == filter_course]
        if filter_year != "All Years":
            filtered_students = [s for s in filtered_students if str(s.get("YearLevel", "")) == filter_year]

        if filtered_students:
            st.write(f"Showing {len(filtered_students)} student(s)")

            # Display student records with pagination
            page_size = 100
            total_pages = (len(filtered_students) + page_size - 1) // page_size

            if total_pages > 1:
                page = st.selectbox("Page", range(1, total_pages + 1), key="admin_page")
            else:
                page = 1

            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(filtered_students))
            page_students = filtered_students[start_idx:end_idx]

            # Display student records
            student_data = []
            for student in page_students:
                grades_count = len(student.get("Grades", {}))
                student_data.append({
                    "ID": student.get("_id", ""),
                    "Name": student.get("Name", ""),
                    "Course": student.get("Course", ""),
                    "Year Level": student.get("YearLevel", ""),
                    "Grades Recorded": grades_count
                })
            st.table(student_data)

            if total_pages > 1:
                st.write(f"Page {page} of {total_pages} (showing {len(page_students)} students)")

            # Quick stats for filtered results
            total_grades = sum(len(s.get("Grades", {})) for s in filtered_students)
            students_with_grades = sum(1 for s in filtered_students if s.get("Grades"))
            avg_grades_per_student = total_grades / len(filtered_students) if filtered_students else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Filtered Students", len(filtered_students))
            col2.metric("Students with Grades", students_with_grades)
            col3.metric("Avg Grades per Student", f"{avg_grades_per_student:.1f}")
        else:
            st.info("No student records found matching your criteria.")

def registrar_dashboard():
    st.header("📋 Registrar Dashboard")
    user = get_current_user()

    tab1, tab2 = st.tabs(["View Students", "Add Student"])

    with tab1:
        st.subheader("Student Records Management")

        # Search and filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("Search by Name", placeholder="Enter student name...", key="registrar_search")
        with col2:
            filter_course = st.selectbox("Filter by Course", ["All Courses", "Information Technology", "Computer Science", "Business Administration", "Engineering"], key="registrar_course")
        with col3:
            filter_year = st.selectbox("Filter by Year", ["All Years", "1", "2", "3", "4"], key="registrar_year")

        # Get all students
        all_students = get_students_for_role(user)

        # Apply filters
        filtered_students = all_students
        if search_name:
            filtered_students = [s for s in filtered_students if search_name.lower() in s.get("Name", "").lower()]
        if filter_course != "All Courses":
            filtered_students = [s for s in filtered_students if s.get("Course") == filter_course]
        if filter_year != "All Years":
            filtered_students = [s for s in filtered_students if str(s.get("YearLevel", "")) == filter_year]

        if filtered_students:
            st.write(f"Showing {len(filtered_students)} student(s)")

            # Display student records with pagination
            page_size = 50
            total_pages = (len(filtered_students) + page_size - 1) // page_size

            if total_pages > 1:
                page = st.selectbox("Page", range(1, total_pages + 1), key="registrar_page")
            else:
                page = 1

            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(filtered_students))
            page_students = filtered_students[start_idx:end_idx]

            # Display student records
            student_data = []
            for student in page_students:
                student_data.append({
                    "ID": student.get("_id", ""),
                    "Name": student.get("Name", ""),
                    "Course": student.get("Course", ""),
                    "Year Level": student.get("YearLevel", "")
                })
            st.table(student_data)

            if total_pages > 1:
                st.write(f"Page {page} of {total_pages} (showing {len(page_students)} students)")

            # Show detailed view
            st.subheader("Detailed Student Information")
            student_options = [f"{s.get('_id', '')} - {s.get('Name', '')}" for s in filtered_students]
            selected_student_option = st.selectbox("Select Student for Details", student_options, key="registrar_detail_select")
            if selected_student_option:
                selected_id = int(selected_student_option.split(" - ")[0])
                student = get_student_by_id(selected_id)
                if student:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Basic Information**")
                        st.write(f"Name: {student.get('Name', 'N/A')}")
                        st.write(f"ID: {student.get('_id', 'N/A')}")
                        st.write(f"Course: {student.get('Course', 'N/A')}")
                        st.write(f"Year Level: {student.get('YearLevel', 'N/A')}")

                    with col2:
                        st.write("**Additional Information**")
                        # Display all other fields
                        for key, value in student.items():
                            if key not in ['_id', 'Name', 'Course', 'YearLevel']:
                                st.write(f"{key}: {value}")
        else:
            st.info("No student records available for your access level or matching your criteria.")

    with tab2:
        st.subheader("Add New Student")
        with st.form("add_student_form"):
            name = st.text_input("Student Name")
            course = st.selectbox("Course", ["Information Technology", "Computer Science", "Business Administration", "Engineering"])
            year_level = st.selectbox("Year Level", [1, 2, 3, 4])

            submitted = st.form_submit_button("Add Student")
            if submitted:
                if name and course:
                    # Find the next available ID
                    last_student = students_collection.find_one(sort=[("_id", -1)])
                    next_id = (last_student.get("_id", 0) + 1) if last_student else 1

                    new_student = {
                        "_id": next_id,
                        "Name": name,
                        "Course": course,
                        "YearLevel": year_level
                    }

                    try:
                        students_collection.insert_one(new_student)
                        st.success(f"Student '{name}' added successfully with ID: {next_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding student: {e}")
                else:
                    st.error("Please fill in all required fields.")

def faculty_dashboard():
    st.header("📚 Faculty Dashboard")
    user = get_current_user()

    tab1, tab2 = st.tabs(["Student Analytics", "Grade Management"])

    with tab1:
        st.subheader("Student Overview")

        # Search and filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("Search by Name", placeholder="Enter student name...", key="faculty_search")
        with col2:
            filter_course = st.selectbox("Filter by Course", ["All Courses", "Information Technology", "Computer Science", "Business Administration", "Engineering"], key="faculty_course")
        with col3:
            filter_year = st.selectbox("Filter by Year", ["All Years", "1", "2", "3", "4"], key="faculty_year")

        # Get all students
        all_students = get_students_for_role(user)

        # Apply filters
        filtered_students = all_students
        if search_name:
            filtered_students = [s for s in filtered_students if search_name.lower() in s.get("Name", "").lower()]
        if filter_course != "All Courses":
            filtered_students = [s for s in filtered_students if s.get("Course") == filter_course]
        if filter_year != "All Years":
            filtered_students = [s for s in filtered_students if str(s.get("YearLevel", "")) == filter_year]

        if filtered_students:
            # Basic metrics for filtered results
            total_students = len(filtered_students)
            courses = set(s.get("Course", "") for s in filtered_students if s.get("Course"))
            year_levels = set(s.get("YearLevel", "") for s in filtered_students if s.get("YearLevel"))

            col1, col2, col3 = st.columns(3)
            col1.metric("Filtered Students", total_students)
            col2.metric("Courses", len(courses))
            col3.metric("Year Levels", len(year_levels))

            # Course distribution for filtered results
            course_counts = {}
            for student in filtered_students:
                course = student.get("Course", "Unknown")
                course_counts[course] = course_counts.get(course, 0) + 1

            st.subheader("Course Distribution")
            st.bar_chart(course_counts)

            # Year level distribution for filtered results
            year_counts = {}
            for student in filtered_students:
                year = f"Year {student.get('YearLevel', 'Unknown')}"
                year_counts[year] = year_counts.get(year, 0) + 1

            st.subheader("Year Level Distribution")
            st.bar_chart(year_counts)

            # Display student details with pagination
            st.subheader("Student Details")
            page_size = 25
            total_pages = (len(filtered_students) + page_size - 1) // page_size

            if total_pages > 1:
                page = st.selectbox("Page", range(1, total_pages + 1), key="faculty_page")
            else:
                page = 1

            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(filtered_students))
            page_students = filtered_students[start_idx:end_idx]

            student_data = []
            for student in page_students:
                student_data.append({
                    "ID": student.get("_id", ""),
                    "Name": student.get("Name", ""),
                    "Course": student.get("Course", ""),
                    "Year Level": student.get("YearLevel", "")
                })
            st.table(student_data)

            if total_pages > 1:
                st.write(f"Page {page} of {total_pages} (showing {len(page_students)} students)")
        else:
            st.info("No students found matching your criteria.")

    with tab2:
        st.subheader("Grade Management & Evaluation")

        # Search for student to grade
        col1, col2 = st.columns(2)
        with col1:
            grade_search = st.text_input("Search Student by Name", placeholder="Enter student name...", key="grade_search")
        with col2:
            grade_course_filter = st.selectbox("Filter by Course", ["All Courses", "Information Technology", "Computer Science", "Business Administration", "Engineering"], key="grade_course_filter")

        # Get all students
        all_students = get_students_for_role(user)

        # Apply filters for grading
        grade_filtered_students = all_students
        if grade_search:
            grade_filtered_students = [s for s in grade_filtered_students if grade_search.lower() in s.get("Name", "").lower()]
        if grade_course_filter != "All Courses":
            grade_filtered_students = [s for s in grade_filtered_students if s.get("Course") == grade_course_filter]

        # Select student to grade
        if grade_filtered_students:
            student_options = [f"{s.get('_id', '')} - {s.get('Name', '')}" for s in grade_filtered_students]
            selected_student = st.selectbox("Select Student to Grade", student_options, key="grade_select")

            if selected_student:
                student_id = int(selected_student.split(" - ")[0])
                student = get_student_by_id(student_id)

                if student:
                    st.write(f"**Grading Student:** {student.get('Name', '')} (ID: {student_id})")

                    with st.form(f"grade_form_{student_id}"):
                        subject = st.text_input("Subject")
                        grade = st.number_input("Grade (0-100)", min_value=0, max_value=100)

                        submitted = st.form_submit_button("Add Grade")
                        if submitted and subject and grade is not None:
                            # Initialize grades field if it doesn't exist
                            if "Grades" not in student:
                                student["Grades"] = {}

                            # Add grade
                            student["Grades"][subject] = grade

                            # Calculate pass/fail status
                            status = "PASS" if grade >= 75 else "FAIL"
                            if "Status" not in student:
                                student["Status"] = {}
                            student["Status"][subject] = status

                            # Update student record
                            students_collection.update_one(
                                {"_id": student_id},
                                {"$set": {"Grades": student["Grades"], "Status": student["Status"]}}
                            )

                            st.success(f"Grade added for {subject}: {grade} ({status})")
                            st.rerun()

                    # Display current grades
                    if "Grades" in student and student["Grades"]:
                        st.subheader("Current Grades")
                        grades_data = []
                        for subj, grd in student["Grades"].items():
                            status = student.get("Status", {}).get(subj, "Unknown")
                            grades_data.append({
                                "Subject": subj,
                                "Grade": grd,
                                "Status": status
                            })
                        st.table(grades_data)
                    else:
                        st.info("No grades recorded yet for this student.")
        else:
            st.info("No students available for grading matching your criteria.")

def student_dashboard():
    user = get_current_user()
    st.header("🎓 Student Dashboard")

    students = get_students_for_role(user)
    if students:
        student = students[0]  # Only one record for student
        student_id = student.get("_id")

        st.subheader("👤 Profile")
        
        # Profile image section
        col_img, col_info = st.columns([1, 2])
        
        with col_img:
            st.write("**Profile Picture**")
            # Display current profile image if exists
            if student.get("profile_image"):
                try:
                    image_data = base64.b64decode(student["profile_image"])
                    image = Image.open(BytesIO(image_data))
                    st.image(image, width=150)
                except:
                    st.info("📷 No profile picture yet")
            else:
                st.info("📷 No profile picture yet")
            
            # Upload new image
            uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png", "gif"])
            if uploaded_file is not None:
                try:
                    image = Image.open(uploaded_file)
                    # Resize image to prevent MongoDB size issues
                    image.thumbnail((300, 300))
                    
                    # Convert to base64
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Update student record
                    students_collection.update_one(
                        {"_id": student_id},
                        {"$set": {"profile_image": img_str}}
                    )
                    st.success("Profile picture updated! ✓")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error uploading image: {e}")
        
        with col_info:
            st.write(f"**Name:** {student.get('Name', 'N/A')}")
            st.write(f"**Student ID:** {student.get('_id', 'N/A')}")
            st.write(f"**Course:** {student.get('Course', 'N/A')}")
            st.write(f"**Year Level:** {student.get('YearLevel', 'N/A')}")
            st.write(f"**Email:** {student.get('email', 'N/A')}")

        st.divider()

        # Display grades and status
        if "Grades" in student and student["Grades"]:
            st.subheader("📊 Academic Grades")

            # Calculate GPA if there are grades
            grades = list(student["Grades"].values())
            if grades:
                gpa = sum(grades) / len(grades)
                st.metric("Overall GPA", f"{gpa:.2f}")

            # Display grades table
            grades_data = []
            for subject, grade in student["Grades"].items():
                status = student.get("Status", {}).get(subject, "Unknown")
                status_color = "🟢 PASS" if status == "PASS" else "🔴 FAIL" if status == "FAIL" else "⚪ " + status
                grades_data.append({
                    "Subject": subject,
                    "Grade": grade,
                    "Status": status_color
                })

            st.table(grades_data)

            # Grade distribution chart
            st.subheader("Grade Distribution")
            grade_counts = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "Below 60": 0}
            for grade in grades:
                if grade >= 90:
                    grade_counts["90-100"] += 1
                elif grade >= 80:
                    grade_counts["80-89"] += 1
                elif grade >= 70:
                    grade_counts["70-79"] += 1
                elif grade >= 60:
                    grade_counts["60-69"] += 1
                else:
                    grade_counts["Below 60"] += 1

            st.bar_chart(grade_counts)

        else:
            st.info("📝 No grades available yet. Please check back later.")

        st.divider()

        st.subheader("📋 Academic Status")
        st.write("**Current Status:** Active Student")
        st.write("**Enrollment:** Full-time")
        if student.get('Course'):
            st.write(f"**Program:** {student['Course']}")
        if student.get('YearLevel'):
            st.write(f"**Year Level:** {student['YearLevel']}")

        # Important notice
        st.info("ℹ️ **Note:** You can only view your academic records. Contact your faculty or registrar for any updates.")

    else:
        st.error("Your student record was not found in the database. Please contact the administrator to link your account with your student record.")
        st.info("The system is currently using restored student data from BSIT DATA. Your account may need to be properly linked to your student record.")

# ---------- MAIN ----------
def main():
    user = get_current_user()
    if not user:
        login_page()
        return

    role = user["role"]

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.write("Logged in as")
        st.write(user["email"])
        st.caption(role)

        if st.button("Logout"):
            sign_out()
            st.rerun()

        st.divider()

        pages = ["Admin", "Registrar", "Faculty", "Student"]
        restrictions = {
            "admin": [],
            "registrar": ["Admin"],
            "faculty": ["Admin", "Registrar"],
            "student": ["Admin", "Registrar", "Faculty"]
        }

        default_index = pages.index(role.capitalize()) if role.capitalize() in pages else 0
        page_labels = []
        for p in pages:
            if p in restrictions.get(role, []):
                page_labels.append(f"{p} 🚫")  # restricted badge
            else:
                page_labels.append(p)

        page = st.radio("Navigation", page_labels, index=default_index)
        page = page.split(" ")[0]  # clean label for routing

    # ---------- PAGE ROUTER ----------
    if page == "Admin":
        if role != "admin":
            st.error("❌ Unauthorized: You cannot access Admin Dashboard")
        else:
            admin_dashboard()
    elif page == "Registrar":
        if role not in ["admin", "registrar"]:
            st.error("❌ Unauthorized: You cannot access Registrar Dashboard")
        else:
            registrar_dashboard()
    elif page == "Faculty":
        if role not in ["admin", "registrar", "faculty"]:
            st.error("❌ Unauthorized: You cannot access Faculty Dashboard")
        else:
            faculty_dashboard()
    elif page == "Student":
        student_dashboard()

if __name__ == "__main__":
    main()