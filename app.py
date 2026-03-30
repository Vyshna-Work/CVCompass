# ============================================
# app.py — Main Flask Application
# Connects all classes together and handles
# all the web routes for CVCompass
# ============================================

from flask import Flask, render_template, request, send_file, redirect, url_for
import os

from models.country import USA, UK, NETHERLANDS
from models.user import User
from models.cv import CV
from models.pdf_generator import PDFGenerator

# ============================================
# App Setup
# ============================================

app = Flask(__name__)

# Folder where generated PDFs will be saved
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Dictionary of all supported countries
COUNTRIES = {
    "usa": USA,
    "uk": UK,
    "netherlands": NETHERLANDS
}

# ============================================
# Routes
# ============================================

# Home page
@app.route("/")
def index():
    """
    Renders the home page with country selection.
    """
    return render_template("index.html", countries=COUNTRIES)


# CV Form page
@app.route("/cv-form/<country_code>")
def cv_form(country_code):
    """
    Renders the CV form for the selected country.
    """
    if country_code not in COUNTRIES:
        return redirect(url_for("index"))

    country = COUNTRIES[country_code]
    return render_template("cv_form.html", country=country, country_code=country_code)


# Generate CV
@app.route("/generate-cv/<country_code>", methods=["POST"])
def generate_cv(country_code):
    """
    Handles form submission, builds the CV and generates the PDF.
    """
    if country_code not in COUNTRIES:
        return redirect(url_for("index"))

    country = COUNTRIES[country_code]

    # Get sidebar colour chosen by user
    sidebar_colour = request.form.get("sidebar_colour", "#2C3E50")
    font_style = request.form.get("font_style", "Helvetica")

    # Create User object from form data
    user = User(
        first_name=request.form.get("first_name", ""),
        last_name=request.form.get("last_name", ""),
        email=request.form.get("email", ""),
        phone=request.form.get("phone", ""),
        address=request.form.get("address", ""),
        nationality=request.form.get("nationality", ""),
        dob=request.form.get("dob", ""),
        summary=request.form.get("summary", ""),
        education=request.form.get("education", "").split("\n"),
        experience=request.form.get("experience", "").split("\n"),
        skills=request.form.get("skills", "").split(","),
        languages=request.form.get("languages", "").split(",")
    )

    # Create CV object
    cv = CV(user, country)

    # Generate PDF with chosen sidebar colour
    pdf_path = os.path.join(OUTPUT_FOLDER, f"{country_code}_cv.pdf")
    pdf_generator = PDFGenerator(cv, pdf_path, sidebar_colour, font_style)
    pdf_generator.generate()

    # Send PDF to user for download
    return send_file(pdf_path, as_attachment=True, download_name=f"CVCompass_{country.name}_CV.pdf")


# ============================================
# Run the app
# ============================================

if __name__ == "__main__":
    app.run(debug=True)