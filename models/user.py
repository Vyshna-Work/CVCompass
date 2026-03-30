# ============================================
# user.py — User Class
# Stores all the personal details entered by
# the user when filling in the CV form
# ============================================


class User:
    """
    Represents the person filling in the CV.
    Stores all personal and professional details
    entered through the CV form.
    """

    def __init__(self, first_name, last_name, email, phone, address,
                 nationality, dob, summary, education, experience, skills, languages):
        """
        Constructor — sets up all the user's personal details.
        These details come from the CV form the user fills in.
        """

        # Personal details
        self.first_name = first_name          # User's first name
        self.last_name = last_name            # User's last name
        self.email = email                    # User's email address
        self.phone = phone                    # User's phone number
        self.address = address               # User's home address

        # Optional details — shown only if country requires them
        self.nationality = nationality        # User's nationality
        self.dob = dob                       # User's date of birth

        # Professional details
        self.summary = summary               # Short personal summary / profile
        self.education = education           # List of education entries
        self.experience = experience         # List of work experience entries
        self.skills = skills                 # List of skills
        self.languages = languages    # List of languages the user speaks

    def get_full_name(self):
        """
        Returns the user's full name by combining first and last name.
        """
        return f"{self.first_name} {self.last_name}"

    def get_details(self):
        """
        Returns all user details as a dictionary.
        Used by Flask to pass user data to the HTML templates.
        """
        return {
            "full_name": self.get_full_name(),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "nationality": self.nationality,
            "dob": self.dob,
            "summary": self.summary,
            "education": self.education,
            "experience": self.experience,
            "skills": self.skills,
            "languages": self.languages
        }

    def __str__(self):
        """
        Returns a clean string representation of the user.
        Useful for debugging and testing.
        """
        return f"User: {self.get_full_name()} | Email: {self.email}"


# ============================================
# Test — runs only when this file is run directly
# Remove or comment this out later when complete
# ============================================

if __name__ == "__main__":

    # Creating a test user object
    test_user = User(
        first_name="Vyshna",
        last_name="Smith",
        email="vyshna@email.com",
        phone="+31 612345678",
        address="Amsterdam, Netherlands",
        nationality="Indian",
        dob="01/01/2000",
        summary="First year Computer Science student with a passion for problem solving.",
        education=["BSc Computer Science — University of Amsterdam, 2024 - Present"],
        experience=["Intern — Tech Company, 2023"],
        skills=["Python", "Java", "SQL", "Flask"]
    )

    # Testing the methods
    print(test_user)
    print("---")
    print(f"Full Name: {test_user.get_full_name()}")
    print("---")
    print("All Details:")
    for key, value in test_user.get_details().items():
        print(f"  {key}: {value}")