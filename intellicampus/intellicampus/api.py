import frappe
from frappe.utils import get_url, now_datetime
from frappe import _


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

    print("Sending email to:", email)

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
    #user_email = "samir@gmail.com"  
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


@frappe.whitelist()
def get_logged_in_admin():
    
    user_email = frappe.session.user
    #user_email="admin@admin.com"
    admin_user = frappe.get_all("User",
            filters={"email": user_email},
            fields=["name", "first_name","middle_name", "last_name", "email"]
        )

    if admin_user:
        return admin_user[0]
    else:
        frappe.throw(_("Logged-in user not found."), frappe.PermissionError)

@frappe.whitelist()
def get_courses_for_instructor():
    instructor_email = frappe.session.user
    #instructor_email="samir@gmail.com"
    # Fetch the instructor's name using their email
    instructor_name = frappe.get_value('Instructor', {'instructor_email': instructor_email}, 'name')
    if not instructor_name:
        frappe.throw(_("Instructor not found with the provided email."), frappe.DoesNotExistError)

    # Fetch courses offered by the instructor, including students_enrolled data
    courses = frappe.get_all('Course Offered', 
                             filters={'instructor': instructor_name}, 
                             fields=['name', 'course', 'section', 'days', 'course_time',
                                     'semester', 'instructor', 'capacity'])

    # Fetch students enrolled for each course
    for course in courses:
        students_enrolled = frappe.get_all('Students Enrolled',
                                           filters={'parenttype': 'Course Offered', 'parentfield': 'students_enrolled', 'parent': course['name']},
                                           fields=['student', 'student_grade', 'passfailed'])
        course['students_enrolled'] = students_enrolled

    return courses


@frappe.whitelist()
def register_student_to_course(course_name, student_name):
    try:
        course = frappe.get_doc("Course Offered", course_name)
        if not course:
            return _("Course not found")

        student = frappe.get_doc("Student", student_name)
        if not student:
            return _("Student not found")

        course.append("students_enrolled", {
            "student": student_name
        })

        course.save()

        return _("Student registered to course successfully")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("API Error"))
        return _("Failed to register student to course: {0}").format(str(e))

@frappe.whitelist()
def get_student_name(email):
    student_name = frappe.db.get_value("Student", {"student_email": email}, "name")
    return student_name


@frappe.whitelist()
def get_courses_for_student(email):
    student_name = frappe.db.get_value("Student", {"student_email": email}, "name")

    if not student_name:
        return []

    courses = frappe.db.sql("""
        SELECT
            course.name as course_name,
            course.course,
            course.section,
            course.instructor,
            course.course_time,
            course.days
        FROM
            `tabCourse Offered` AS course
        JOIN
            `tabStudents Enrolled` AS enrolled ON course.name = enrolled.parent
        WHERE
            enrolled.student = %s
            AND enrolled.parenttype = 'Course Offered'
        """, (student_name), as_dict=True)

    return courses



