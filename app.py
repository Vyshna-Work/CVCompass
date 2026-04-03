# ============================================
# app.py — Main Flask Application
# Connects all classes together and handles
# all the web routes for CVCompass
# ============================================

from flask import Flask, render_template, request, send_file, redirect, url_for
import os

# Importing our custom classes
from models.country import USA, UK, NETHERLANDS
from models.user import User
from models.cv import CV
from models.pdf_generator import PDFGenerator

# ============================================
# App Setup
# ============================================

# Creating the Flask app
app = Flask(__name__)

# Folder where generated PDFs will be saved
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Dictionary of all supported countries
# Key is used in the URL, value is the Country object
COUNTRIES = {
    "usa": USA,
    "uk": UK,
    "netherlands": NETHERLANDS
}

# ============================================
# Routes
# ============================================

# Home page — shows the country selection
@app.route("/")
def index():
    """
    Renders the home page.
    Passes the list of countries to the template.
    """
    return render_template("index.html", countries=COUNTRIES)


# CV Form page — shows the form for the selected country
@app.route("/cv-form/<country_code>")
def cv_form(country_code):
    """
    Renders the CV form page for the selected country.
    country_code comes from the URL e.g. /cv-form/usa
    """

    # Check if the country code is valid
    if country_code not in COUNTRIES:
        return redirect(url_for("index"))

    # Get the country object
    country = COUNTRIES[country_code]

    # Pass the country and its rules to the form template
    return render_template("cv_form.html", country=country, country_code=country_code)


# Generate CV — handles the form submission
@app.route("/generate-cv/<country_code>", methods=["POST"])
def generate_cv(country_code):
    """
    Handles the CV form submission.
    Creates a User object from the form data,
    builds the CV and generates the PDF.
    """

    # Check if the country code is valid
    if country_code not in COUNTRIES:
        return redirect(url_for("index"))

    # Get the country object
    country = COUNTRIES[country_code]

    # Get customisation choices from the form
    sidebar_colour = request.form.get("sidebar_colour", "#2C3E50")   # Sidebar colour chosen by user
    font_style = request.form.get("font_style", "Helvetica")          # Font style chosen by user

    # Get form data and create a User object
    user = User(
        first_name=request.form.get("first_name", ""),
        last_name=request.form.get("last_name", ""),
        email=request.form.get("email", ""),
        phone=request.form.get("phone", ""),
        address=request.form.get("address", ""),
        nationality=request.form.get("nationality", ""),
        dob=request.form.get("dob", ""),
        summary=request.form.get("summary", ""),
        education=request.form.get("education", "").split("\n"),      # Split each line into a list
        experience=request.form.get("experience", "").split("\n"),    # Split each line into a list
        skills=request.form.get("skills", "").split(","),             # Split by comma into a list
        languages=request.form.get("languages", "").split(",")        # Split by comma into a list
    )

    # Create the CV object combining user and country
    cv = CV(user, country)

    # Generate the PDF with chosen customisation options
    pdf_path = os.path.join(OUTPUT_FOLDER, f"{country_code}_cv.pdf")
    pdf_generator = PDFGenerator(cv, pdf_path, sidebar_colour, font_style)
    pdf_generator.generate()

    # Send the PDF file to the user for download
    return send_file(pdf_path, as_attachment=True, download_name=f"CVCompass_{country.name}_CV.pdf")


# ============================================
# Run the app
# ============================================

if __name__ == "__main__":
    # debug=True means the app reloads automatically when you make changes
    app.run(debug=True)