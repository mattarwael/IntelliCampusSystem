import frappe

@frappe.whitelist(allow_guest=True)
def get_instructor_details_by_name(instructor_name):
    try:
        instructor = frappe.get_doc("Instructor", {"instructor_name": instructor_name})

        # Extract required fields
        details = {
            "name": instructor.name,
            "instructor_name": instructor.instructor_name,
            "department": instructor.department,
            "instructor_middle_name": instructor.instructor_middle_name,
            "instructor_last_name": instructor.instructor_last_name,
            "instructor_number": instructor.instructor_number,
            "instructor_email": instructor.instructor_email,
            "instructor_birthday": instructor.instructor_birthday.strftime("%Y-%m-%d"),
            "advisor": instructor.advisor
        }

        return details
    except Exception as e:
        frappe.log_error(f"Error fetching instructor details: {e}")
        return None
