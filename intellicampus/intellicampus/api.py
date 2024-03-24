import frappe
from frappe.utils import get_url, now_datetime

@frappe.whitelist(allow_guest=True)
def create_user(student_email, first_name, last_name):

    try:
        if not frappe.db.exists("User", student_email):
            print("User does not exist. Creating new user...")
            
            new_user = frappe.get_doc({
                "doctype": "User",
                "email": student_email,
                "first_name": first_name,
                "last_name": last_name,
                "send_welcome_email": 0, 
                "roles": [{"role": "Student"}] 
            })
            new_user.insert(ignore_permissions=True) 

            password = first_name + last_name + '1234'
            new_user.new_password = password
            new_user.save()

            send_user_credentials_email(student_email, first_name, last_name, password)

            print("User created successfully.")
            return {"status": "success", "message": "User created successfully"}
        else:
            print("User already exists.")
            return {"status": "error", "message": "User already exists"}

    except Exception as e:
        print("Error occurred:", str(e))
        return {"status": "error", "message": "Error occurred while creating user"}

def send_user_credentials_email(email, first_name, last_name, password):
    subject = "Your Account Credentials"
    message = f"Hello {first_name} {last_name},\n\nYour account has been created.\n\nEmail: {email}\nPassword: {password}\n\nPlease login using these credentials and change your password.\n\nThank you."

    print("Sending email to:", email)  # Debugging line

    try:
        frappe.sendmail(
            recipients=email,
            subject=subject,
            message=message
        )
        print("Email sent successfully.")
    except Exception as e:
        print("Error occurred while sending email:", str(e))



@frappe.whitelist()
def get_courses():
    courses = frappe.get_all('Course Offered', fields=['course', 'section', 'days', 'course_time',
    'semester', 'instructor', "capacity"])
    return courses

# @frappe.whitelist()
# def get_courses_details(course_names):
#     # Split the course names received as a comma-separated string
#     course_names_list = course_names.split(',')

#     # Fetch details for courses offered with matching course names
#     courses_details = []
#     for course_name in course_names_list:
#         course_details = frappe.get_all("Course", filters={"course_title": course_name}, fields=["course_title", "description", "course_prerequisites", "syllabus", "language", "department", "credits_number"])
#         if course_details:
#             courses_details.append(course_details[0])  # Append details for matching courses
    
#     return courses_details


@frappe.whitelist()
def get_logged_in_student():
    #user_email="wael.m@gmail.com"
    user_email = frappe.session.user

    student = frappe.get_all("Student",
        filters={"student_email": user_email},
        fields=["first_name", "middle_name", "name", "student_email",
                "phone_number", "emergency_contact_parents", "department", "birthday",
                "picture", "student_address", "advisor", "credits_finished", "student_study_program",
                "last_name"]
    )

    if student:
        return student[0]
    else:
        frappe.throw(_("Logged-in user is not a student or student details not found."), frappe.PermissionError)


@frappe.whitelist()
def get_department_courses():
    #
    user_email = frappe.session.user
    #user_email="wael.m@gmail.com"
    department = frappe.get_value("Student", {"student_email": user_email}, "department")

    if department:
        courses = frappe.get_all("Course",
            filters={"department": department},
            fields=["name", "course_code", "course_title", "description", "instructor",
                    "course_capacity", "syllabus", "course_prerequisites", "language",
                    "credits_number", "department"]
        )

        return courses
    else:
        frappe.throw(_("Department not found for the logged-in user."), frappe.PermissionError)

@frappe.whitelist()
def get_logged_in_instructor():
    #user_email = "samir@gmail.com"  # Replace with actual email or fetch from session
    user_email = frappe.session.user

    instructor = frappe.get_all("Instructor",
        filters={"instructor_email": user_email},
        fields=["name", "instructor_name", "department", "instructor_middle_name",
                "instructor_last_name", "instructor_number", "instructor_email",
                "instructor_birthday", "advisor"]
    )

    if instructor:
        return instructor[0]
    else:
        frappe.throw(_("Logged-in user is not an instructor or instructor details not found."), frappe.PermissionError)
