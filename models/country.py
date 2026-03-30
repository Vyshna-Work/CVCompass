# ============================================
# country.py — Country Class
# Defines the formatting rules for each country
# ============================================


class Country:
    """
    Represents a country with its specific CV formatting rules.
    Each country has different requirements for photos, pages, tone etc.
    """

    def __init__(self, name, cv_name, photo_required, max_pages, include_dob, include_nationality, tone):
        """
        Constructor — runs automatically when a Country object is created.
        Sets up all the formatting rules for that specific country.
        """
        self.name = name                          # Full country name e.g. "United States"
        self.cv_name = cv_name                    # What the document is called e.g. "Resume" or "CV"
        self.photo_required = photo_required      # True if photo is required, False if not
        self.max_pages = max_pages                # Maximum number of pages allowed
        self.include_dob = include_dob            # True if date of birth should be included
        self.include_nationality = include_nationality  # True if nationality should be included
        self.tone = tone                          # Recommended tone of writing for that country

    def display_rules(self):
        """
        Prints all the formatting rules for this country to the terminal.
        Useful for testing and debugging.
        """
        print(f"Country: {self.name}")
        print(f"Document Name: {self.cv_name}")
        print(f"Photo Required: {'Yes' if self.photo_required else 'No'}")
        print(f"Max Pages: {self.max_pages}")
        print(f"Include Date of Birth: {'Yes' if self.include_dob else 'No'}")
        print(f"Include Nationality: {'Yes' if self.include_nationality else 'No'}")
        print(f"Tone: {self.tone}")

    def get_rules(self):
        """
        Returns all the country rules as a dictionary.
        Used by Flask to pass rules to the HTML templates.
        """
        return {
            "name": self.name,
            "cv_name": self.cv_name,
            "photo_required": self.photo_required,
            "max_pages": self.max_pages,
            "include_dob": self.include_dob,
            "include_nationality": self.include_nationality,
            "tone": self.tone
        }


# ============================================
# Country Objects
# Creating one object for each supported country
# Each object stores that country's specific rules
# ============================================

# United States — called Resume, 1 page, no photo, no personal details
USA = Country(
    name="United States",
    cv_name="Resume",
    photo_required=False,
    max_pages=1,
    include_dob=False,
    include_nationality=False,
    tone="Concise and punchy"
)

# United Kingdom — called CV, 2 pages max, no photo, no personal details
UK = Country(
    name="United Kingdom",
    cv_name="CV",
    photo_required=False,
    max_pages=2,
    include_dob=False,
    include_nationality=False,
    tone="Professional and formal"
)

# Netherlands — called CV, 2 pages max, photo optional, personal details included
NETHERLANDS = Country(
    name="Netherlands",
    cv_name="CV",
    photo_required=True,
    max_pages=2,
    include_dob=True,
    include_nationality=True,
    tone="Skills focused and direct"
)


# ============================================
# Test — runs only when this file is run directly
# Remove or comment this out later when project is complete
# ============================================

if __name__ == "__main__":
    print("Testing Country Class")
    print("=====================")
    USA.display_rules()
    print("---")
    UK.display_rules()
    print("---")
    NETHERLANDS.display_rules()