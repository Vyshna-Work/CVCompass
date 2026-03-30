# ============================================
# cv.py — CV Class
# Combines user details and country rules
# to build a properly formatted CV
# ============================================

# Importing Country and User classes
from models.country import Country
from models.user import User


class CV:
    """
    Represents a CV document.
    Takes the user's details and applies the
    correct formatting rules for the selected country.
    """

    def __init__(self, user, country):
        """
        Constructor — takes a User object and a Country object.
        Combines them to create a formatted CV.
        """
        self.user = user          # The person's details
        self.country = country    # The country's formatting rules

    def get_sections(self):
        """
        Returns the CV sections in the correct order.
        Different countries have different section orders and requirements.
        """

        # Base sections every country includes
        sections = {
            "personal_info": {
                "full_name": self.user.get_full_name(),
                "email": self.user.email,
                "phone": self.user.phone,
                "address": self.user.address
            },
            "summary": self.user.summary,
            "education": self.user.education,
            "experience": self.user.experience,
            "skills": self.user.skills,
            "languages": self.user.languages
        }

        # Add optional sections based on country rules
        if self.country.include_dob:
            sections["personal_info"]["dob"] = self.user.dob

        if self.country.include_nationality:
            sections["personal_info"]["nationality"] = self.user.nationality

        if self.country.photo_required:
            sections["personal_info"]["photo"] = "Photo Required"

        return sections

    def get_formatted_cv(self):
        """
        Returns the complete CV as a dictionary.
        Contains both the country rules and user details.
        Used by Flask to pass everything to the HTML template.
        """
        return {
            "country_rules": self.country.get_rules(),
            "sections": self.get_sections(),
            "document_title": self.country.cv_name,
            "tone": self.country.tone
        }

    def __str__(self):
        """
        Returns a clean string summary of the CV.
        Useful for debugging and testing.
        """
        return f"{self.country.cv_name} for {self.user.get_full_name()} — {self.country.name} format"


# ============================================
# Test — runs only when this file is run directly
# Remove or comment this out later when complete
# ============================================

if __name__ == "__main__":

    # Import test country and user
    from models.country import USA, UK, NETHERLANDS
    from models.user import User

    # Creating a test user
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

    # Testing with all three countries
    for country in [USA, UK, NETHERLANDS]:
        cv = CV(test_user, country)
        print(cv)
        print("Sections:", cv.get_sections())
        print("---")