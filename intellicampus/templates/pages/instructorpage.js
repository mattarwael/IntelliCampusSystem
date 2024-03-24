

// Example usage
    var instructorName = "Samir Abbas Haddad"; // Replace with the actual instructor name

    // Make API call to fetch instructor details
    frappe.call({
        method: "intellicampus.intellicampus.api.get_instructor_details_by_name",
        args: {
            instructor_name: instructorName
        },
        callback: function(response) {
            if (response.message) {
                // Handle successful response
                var instructorDetails = response.message;
                console.log("Instructor Details:", instructorDetails);
                
                // Populate instructor details in HTML
                document.getElementById("instructorName").textContent = instructorDetails.instructor_name;
                // Similarly, populate other instructor details as needed
                
            } else {
                // Handle error
                console.error("Failed to fetch instructor details");
            }
        }
    });

