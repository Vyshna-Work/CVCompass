# ============================================
# pdf_generator.py — PDFGenerator Class
# Takes a finished CV and converts it into
# a downloadable PDF file using ReportLab
# ============================================

import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import simpleSplit, ImageReader


class PDFGenerator:
    """
    Handles the generation of a PDF file from a CV object.
    Uses ReportLab to create a two column PDF with a coloured sidebar.
    Supports photo upload for countries that require it.
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
        Left sidebar contains photo, contact details, skills and languages.
        Right main section contains summary, education and experience.
        """

        # Get CV data and sections
        cv_data = self.cv.get_formatted_cv()
        sections = cv_data["sections"]
        personal = sections["personal_info"]

        # Set font variables based on user choice
        font = self.font_style
        if self.font_style == "Times-Roman":
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

        # — Photo (if country requires it and user uploaded one) —
        if "photo" in personal and self.cv.user.photo:
            try:
                # Save uploaded photo to a temporary file
                photo = self.cv.user.photo
                photo.seek(0)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(photo.read())
                    tmp_path = tmp.name

                # Draw square photo at top of sidebar
                photo_x = sidebar_x
                photo_y = sidebar_y - 3 * cm
                photo_size = 3.5 * cm

                c.drawImage(
                    tmp_path,
                    photo_x,
                    photo_y,
                    width=photo_size,
                    height=photo_size,
                    preserveAspectRatio=False
                )
                sidebar_y -= 4 * cm

                # Clean up temp file
                os.unlink(tmp_path)

            except Exception as e:
                print(f"Photo error: {e}")
                # Show placeholder square if photo fails to load
                c.setFillColor(colors.white)
                c.setStrokeColor(colors.white)
                c.setLineWidth(1)
                c.rect(sidebar_x, sidebar_y - 3.5 * cm, 3.5 * cm, 3.5 * cm, fill=0, stroke=1)
                c.setFont(font, 9)
                c.setFillColor(colors.white)
                c.drawCentredString(sidebar_x + 1.75 * cm, sidebar_y - 2 * cm, "Add Photo")
                sidebar_y -= 4.2 * cm

        elif "photo" in personal:
            # Country requires photo but none uploaded — show placeholder square
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.white)
            c.setLineWidth(1)
            c.rect(sidebar_x, sidebar_y - 3.5 * cm, 3.5 * cm, 3.5 * cm, fill=0, stroke=1)
            c.setFont(font, 9)
            c.setFillColor(colors.white)
            c.drawCentredString(sidebar_x + 1.75 * cm, sidebar_y - 2 * cm, "Add Photo")
            sidebar_y -= 4.2 * cm

        # — Name on sidebar in uppercase —
        c.setFillColor(colors.white)
        c.setFont(font_bold, 18)                # Increased from 16
        name = personal["full_name"].upper()
        for line in simpleSplit(name, font_bold, 18, 5.5 * cm):
            c.drawString(sidebar_x, sidebar_y, line)
            sidebar_y -= 0.7 * cm
        sidebar_y -= 0.2 * cm

        # — Divider line —
        c.setStrokeColor(colors.white)
        c.setLineWidth(0.5)
        c.line(sidebar_x, sidebar_y, sidebar_x + 5.5 * cm, sidebar_y)
        sidebar_y -= 0.5 * cm

        # — Contact section heading —
        c.setFont(font_bold, 10)                # Increased from 9
        c.setFillColor(colors.white)
        c.drawString(sidebar_x, sidebar_y, "CONTACT")
        sidebar_y -= 0.5 * cm

        # — Contact details —
        c.setFont(font, 9)                      # Increased from 8
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

        # Print each contact item wrapping long lines
        for item in contact_items:
            if item:
                wrapped = simpleSplit(item, font, 9, 5.2 * cm)
                for line in wrapped:
                    c.drawString(sidebar_x, sidebar_y, line)
                    sidebar_y -= 0.45 * cm
        sidebar_y -= 0.3 * cm

        # — Divider line —
        c.line(sidebar_x, sidebar_y, sidebar_x + 5.5 * cm, sidebar_y)
        sidebar_y -= 0.5 * cm

        # — Skills section heading —
        c.setFont(font_bold, 10)                # Increased from 9
        c.drawString(sidebar_x, sidebar_y, "SKILLS")
        sidebar_y -= 0.5 * cm

        # — Skills list —
        c.setFont(font, 9)                      # Increased from 8
        for skill in sections.get("skills", []):
            skill = skill.strip()
            if skill:
                c.drawString(sidebar_x, sidebar_y, f"• {skill}")
                sidebar_y -= 0.45 * cm
        sidebar_y -= 0.3 * cm

        # — Divider line —
        c.line(sidebar_x, sidebar_y, sidebar_x + 5.5 * cm, sidebar_y)
        sidebar_y -= 0.5 * cm

        # — Languages section heading —
        c.setFont(font_bold, 10)                # Increased from 9
        c.drawString(sidebar_x, sidebar_y, "LANGUAGES")
        sidebar_y -= 0.5 * cm

        # — Languages list —
        c.setFont(font, 9)                      # Increased from 8
        for lang in sections.get("languages", []):
            lang = lang.strip()
            if lang:
                c.drawString(sidebar_x, sidebar_y, f"• {lang}")
                sidebar_y -= 0.45 * cm

        # ============================================
        # Main Content (Right Side)
        # ============================================

        # Starting position for main content
        main_x = sidebar_width + margin + 0.5 * cm
        main_y = page_height - margin

        # — Profile Summary heading —
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.setFont(font_bold, 13)                # Increased from 11
        c.drawString(main_x, main_y, "PROFILE SUMMARY")
        main_y -= 0.3 * cm
        c.setStrokeColor(colors.HexColor("#2C3E50"))
        c.setLineWidth(1)
        c.line(main_x, main_y, main_x + main_width, main_y)
        main_y -= 0.5 * cm

        # — Summary text —
        c.setFont(font, 10)                     # Increased from 9
        c.setFillColor(colors.HexColor("#333333"))
        for line in simpleSplit(sections.get("summary", ""), font, 10, main_width):
            c.drawString(main_x, main_y, line)
            main_y -= 0.45 * cm
        main_y -= 0.2 * cm

        # — Education heading —
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.setFont(font_bold, 13)                # Increased from 11
        c.drawString(main_x, main_y, "EDUCATION")
        main_y -= 0.3 * cm
        c.setStrokeColor(colors.HexColor("#2C3E50"))
        c.line(main_x, main_y, main_x + main_width, main_y)
        main_y -= 0.5 * cm

        # — Education list —
        c.setFont(font, 10)                     # Increased from 9
        c.setFillColor(colors.HexColor("#333333"))
        for edu in sections.get("education", []):
            edu = edu.strip()
            if edu:
                for line in simpleSplit(edu, font, 10, main_width):
                    c.drawString(main_x, main_y, line)
                    main_y -= 0.45 * cm
                main_y -= 0.1 * cm
        main_y -= 0.2 * cm

        # — Experience heading —
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.setFont(font_bold, 13)                # Increased from 11
        c.drawString(main_x, main_y, "WORK EXPERIENCE")
        main_y -= 0.3 * cm
        c.setStrokeColor(colors.HexColor("#2C3E50"))
        c.line(main_x, main_y, main_x + main_width, main_y)
        main_y -= 0.5 * cm

        # — Experience list —
        c.setFont(font, 10)                     # Increased from 9
        c.setFillColor(colors.HexColor("#333333"))
        for exp in sections.get("experience", []):
            exp = exp.strip()
            if exp:
                for line in simpleSplit(exp, font, 10, main_width):
                    c.drawString(main_x, main_y, line)
                    main_y -= 0.45 * cm
                main_y -= 0.1 * cm

        # — Save the PDF —
        c.save()
        print(f"PDF successfully generated: {self.output_path}")
