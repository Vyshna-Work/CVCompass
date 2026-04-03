# ============================================
# pdf_generator.py — PDFGenerator Class
# Takes a finished CV and converts it into
# a downloadable PDF file using ReportLab
# ============================================

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import simpleSplit


class PDFGenerator:
    """
    Handles the generation of a PDF file from a CV object.
    Uses ReportLab to create a two column PDF with a coloured sidebar.
    """

    def __init__(self, cv, output_path, sidebar_colour="#2C3E50", font_style="Helvetica"):
        """
        Constructor — takes a CV object, output path, sidebar colour and font style.
        """
        self.cv = cv                            # The CV object containing user and country data
        self.output_path = output_path          # Where to save the PDF file
        self.sidebar_colour = sidebar_colour    # Sidebar colour chosen by user
        self.font_style = font_style            # Font style chosen by user

    def generate(self):
        """
        Main method — generates the PDF file with a two column layout.
        Left sidebar contains contact details, skills and languages.
        Right main section contains summary, education and experience.
        """

        # Get CV data and sections
        cv_data = self.cv.get_formatted_cv()
        sections = cv_data["sections"]
        personal = sections["personal_info"]

        # Set font variables based on user choice
        font = self.font_style                      # Regular font
        if self.font_style == "Times-Roman":        # Times-Roman bold is called Times-Bold in ReportLab — handle separately
            font_bold = "Times-Bold"
        else:
            font_bold = f"{self.font_style}-Bold"

        # Convert sidebar colour to ReportLab colour
        sidebar_color = colors.HexColor(self.sidebar_colour)

        # Page setup
        page_width, page_height = A4
        margin = 1.5 * cm
        sidebar_width = 6.5 * cm
        main_width = page_width - sidebar_width - (margin * 2) - 0.5 * cm

        # Create the PDF canvas
        c = pdf_canvas.Canvas(self.output_path, pagesize=A4)

        # ============================================
        # Draw sidebar background
        # ============================================
        c.setFillColor(sidebar_color)
        c.rect(0, 0, sidebar_width + margin, page_height, fill=1, stroke=0)

        # ============================================
        # Sidebar Content
        # ============================================

        # Starting position for sidebar
        sidebar_x = margin * 0.8
        sidebar_y = page_height - margin

        # — Photo placeholder (if country requires it) —
        if "photo" in personal:
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.white)
            c.circle(sidebar_x + 2.5 * cm, sidebar_y - 2 * cm, 1.8 * cm, fill=0, stroke=1)
            c.setFont(font, 8)
            c.setFillColor(colors.white)
            c.drawCentredString(sidebar_x + 2.5 * cm, sidebar_y - 2 * cm, "Photo")
            sidebar_y -= 4.5 * cm

        # — Name on sidebar in uppercase —
        c.setFillColor(colors.white)
        c.setFont(font_bold, 16)
        name = personal["full_name"].upper()
        name_parts = name.split(" ")
        c.drawString(sidebar_x, sidebar_y, name_parts[0])
        sidebar_y -= 0.6 * cm
        if len(name_parts) > 1:
            c.drawString(sidebar_x, sidebar_y, " ".join(name_parts[1:]))
            sidebar_y -= 0.8 * cm

        # — Divider line —
        c.setStrokeColor(colors.white)
        c.setLineWidth(0.5)
        c.line(sidebar_x, sidebar_y, sidebar_x + 5.5 * cm, sidebar_y)
        sidebar_y -= 0.5 * cm

        # — Contact section heading —
        c.setFont(font_bold, 9)
        c.setFillColor(colors.white)
        c.drawString(sidebar_x, sidebar_y, "CONTACT")
        sidebar_y -= 0.5 * cm

        # — Contact details —
        c.setFont(font, 8)
        contact_items = [
            personal.get("email", ""),
            personal.get("phone", ""),
            personal.get("address", "")
        ]

        # Add optional fields if country requires them
        if "dob" in personal:
            contact_items.append(f"DOB: {personal['dob']}")
        if "nationality" in personal:
            contact_items.append(f"Nationality: {personal['nationality']}")

        # Print each contact item, wrapping long lines
        for item in contact_items:
            if item:
                wrapped = simpleSplit(item, font, 8, 5.2 * cm)
                for line in wrapped:
                    c.drawString(sidebar_x, sidebar_y, line)
                    sidebar_y -= 0.4 * cm
        sidebar_y -= 0.3 * cm

        # — Divider line —
        c.line(sidebar_x, sidebar_y, sidebar_x + 5.5 * cm, sidebar_y)
        sidebar_y -= 0.5 * cm

        # — Skills section heading —
        c.setFont(font_bold, 9)
        c.drawString(sidebar_x, sidebar_y, "SKILLS")
        sidebar_y -= 0.5 * cm

        # — Skills list —
        c.setFont(font, 8)
        for skill in sections.get("skills", []):
            skill = skill.strip()
            if skill:
                c.drawString(sidebar_x, sidebar_y, f"• {skill}")
                sidebar_y -= 0.4 * cm
        sidebar_y -= 0.3 * cm

        # — Divider line —
        c.line(sidebar_x, sidebar_y, sidebar_x + 5.5 * cm, sidebar_y)
        sidebar_y -= 0.5 * cm

        # — Languages section heading —
        c.setFont(font_bold, 9)
        c.drawString(sidebar_x, sidebar_y, "LANGUAGES")
        sidebar_y -= 0.5 * cm

        # — Languages list —
        c.setFont(font, 8)
        for lang in sections.get("languages", []):
            lang = lang.strip()
            if lang:
                c.drawString(sidebar_x, sidebar_y, f"• {lang}")
                sidebar_y -= 0.4 * cm

        # ============================================
        # Main Content (Right Side)
        # ============================================

        # Starting position for main content
        main_x = sidebar_width + margin + 0.5 * cm
        main_y = page_height - margin

        # — Profile Summary heading —
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.setFont(font_bold, 11)
        c.drawString(main_x, main_y, "PROFILE SUMMARY")
        main_y -= 0.3 * cm
        c.setStrokeColor(colors.HexColor("#2C3E50"))
        c.setLineWidth(1)
        c.line(main_x, main_y, main_x + main_width, main_y)
        main_y -= 0.5 * cm

        # — Summary text —
        c.setFont(font, 9)
        c.setFillColor(colors.HexColor("#333333"))
        for line in simpleSplit(sections.get("summary", ""), font, 9, main_width):
            c.drawString(main_x, main_y, line)
            main_y -= 0.4 * cm
        main_y -= 0.4 * cm

        # — Education heading —
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.setFont(font_bold, 11)
        c.drawString(main_x, main_y, "EDUCATION")
        main_y -= 0.3 * cm
        c.setStrokeColor(colors.HexColor("#2C3E50"))
        c.line(main_x, main_y, main_x + main_width, main_y)
        main_y -= 0.5 * cm

        # — Education list —
        c.setFont(font, 9)
        c.setFillColor(colors.HexColor("#333333"))
        for edu in sections.get("education", []):
            edu = edu.strip()
            if edu:
                for line in simpleSplit(edu, font, 9, main_width):
                    c.drawString(main_x, main_y, line)
                    main_y -= 0.4 * cm
                main_y -= 0.2 * cm
        main_y -= 0.4 * cm

        # — Experience heading —
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.setFont(font_bold, 11)
        c.drawString(main_x, main_y, "WORK EXPERIENCE")
        main_y -= 0.3 * cm
        c.setStrokeColor(colors.HexColor("#2C3E50"))
        c.line(main_x, main_y, main_x + main_width, main_y)
        main_y -= 0.5 * cm

        # — Experience list —
        c.setFont(font, 9)
        c.setFillColor(colors.HexColor("#333333"))
        for exp in sections.get("experience", []):
            exp = exp.strip()
            if exp:
                for line in simpleSplit(exp, font, 9, main_width):
                    c.drawString(main_x, main_y, line)
                    main_y -= 0.4 * cm
                main_y -= 0.2 * cm

        # — Save the PDF —
        c.save()
        print(f"PDF successfully generated: {self.output_path}")


# ============================================
# Test — runs only when this file is run directly
# Remove or comment this out later when complete
# ============================================

if __name__ == "__main__":

    from models.country import USA, UK, NETHERLANDS
    from models.user import User
    from models.cv import CV
    import os

    # Create output folder if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Create a test user
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
        skills=["Python", "Java", "SQL", "Flask"],
        languages=["English", "Dutch"]
    )

    # Test PDF generation for all three countries
    for country in [USA, UK, NETHERLANDS]:
        cv = CV(test_user, country)
        pdf = PDFGenerator(cv, f"output/{country.name}_cv.pdf")
        pdf.generate()