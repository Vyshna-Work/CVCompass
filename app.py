#============================================
# app.py — Main Flask Application
# Connects all classes together and handles
# all the web routes for CVCompass
# ============================================

from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
from openai import OpenAI
from dotenv import load_dotenv

# Importing our custom classes
from models.country import USA, UK, NETHERLANDS, GERMANY, JAPAN, AUSTRALIA
from models.user import User
from models.cv import CV
from models.pdf_generator import PDFGenerator

# Load environment variables from .env file
load_dotenv()

# ============================================
# App Setup
# ============================================

# Creating the Flask app
app = Flask(__name__)

# Folder where generated PDFs will be saved
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Dictionary of all supported countries
# Key is used in the URL, value is the Country object
COUNTRIES = {
    "usa": USA,
    "uk": UK,
    "netherlands": NETHERLANDS,
    "germany": GERMANY,
    "japan": JAPAN,
    "australia": AUSTRALIA
}

# ============================================
# Routes
# ============================================

# Home page — new landing page
@app.route("/")
def home():
    """
    Renders the new landing homepage.
    """
    return render_template("home.html")


# Country selection page
@app.route("/countries")
def index():
    """
    Renders the country selection page.
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
    sidebar_colour = request.form.get("sidebar_colour", "#2C3E50")    # Sidebar colour chosen by user
    font_style = request.form.get("font_style", "Helvetica")           # Font style chosen by user

    # Get photo file only if one was actually uploaded
    photo_file = request.files.get("photo")
    photo = photo_file if photo_file and photo_file.filename != "" else None

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
        education=request.form.get("education", "").split("\n"),       # Split each line into a list
        experience=request.form.get("experience", "").split("\n"),     # Split each line into a list
        skills=request.form.get("skills", "").split(","),              # Split by comma into a list
        languages=request.form.get("languages", "").split(","),        # Split by comma into a list
        photo=photo                                                     # Photo file if uploaded
    )

    # Create the CV object combining user and country
    cv = CV(user, country)

    # Generate the PDF with chosen customisation options
    pdf_path = os.path.join(OUTPUT_FOLDER, f"{country_code}_cv.pdf")
    pdf_generator = PDFGenerator(cv, pdf_path, sidebar_colour, font_style)
    try:
        pdf_generator.generate()
    except Exception as e:
        print(f"PDF GENERATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Send the PDF file to the user for download
    return send_file(pdf_path, as_attachment=True, download_name=f"CVCompass_{country.name}_CV.pdf")


# Upload existing CV — reads a .docx or .pdf file and returns extracted data
@app.route("/upload-cv", methods=["POST"])
def upload_cv():
    """
    Handles the upload of an existing .docx or .pdf CV file.
    Reads the document, extracts details and returns
    them as JSON to auto fill the form fields.
    """
    from models.cv_reader import CVReader

    # Get the uploaded file
    cv_file = request.files.get("existing_cv")

    # Check if a file was actually uploaded
    if not cv_file or cv_file.filename == "":
        return jsonify({"error": "No file uploaded"}), 400

    # Check if it is a .docx or .pdf file
    if not (cv_file.filename.lower().endswith(".docx") or cv_file.filename.lower().endswith(".pdf")):
        return jsonify({"error": "Only .docx and .pdf files are supported"}), 400

    try:
        # Read and extract details from the uploaded CV
        reader = CVReader(cv_file, cv_file.filename)
        extracted_data = reader.extract_all()

        # Return extracted data as JSON to the frontend
        return jsonify(extracted_data)

    except Exception as e:
        print(f"CV reading error: {e}")
        return jsonify({"error": "Could not read the CV file"}), 500


# Generate AI powered profile summary
@app.route("/generate-summary", methods=["POST"])
def generate_summary():
    """
    Takes the user's skills, education and experience
    and uses Google Gemini AI to generate a tailored,
    natural sounding profile summary.
    """

    # Get details from the request
    data = request.get_json()
    first_name = data.get("first_name", "")
    skills = data.get("skills", "")
    education = data.get("education", "")
    experience = data.get("experience", "")
    languages = data.get("languages", "")
    country_name = data.get("country", "")
    tone = data.get("tone", "professional")

    # Build the prompt for Gemini
    prompt = f"""Write a professional CV profile summary for {first_name}.

Details:
- Education: {education}
- Work Experience: {experience}
- Skills: {skills}
- Languages: {languages}
- Target country: {country_name}
- Tone should be: {tone}

Write a natural, unique, 3 to 4 sentence profile summary that highlights their strengths based on the details above.
Do not use generic phrases like "highly motivated" or "team player" unless genuinely supported by the details.
Make it sound like a real person wrote it, tailored specifically to them.
Return ONLY the summary text — no labels, no quotation marks, no extra text."""

    try:
        # Configure OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        # Generate the summary
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content.strip()

        # Remove quotation marks if AI added them
        summary = summary.strip('"').strip("'")

        return jsonify({"summary": summary})

    except Exception as e:
        print(f"AI summary error: {e}")
        return jsonify({"error": "Could not generate summary"}), 500


# ============================================
# Run the app
# ============================================

if __name__ == "__main__":
    # debug=True means the app reloads automatically when you make changes
    app.run(debug=True)
