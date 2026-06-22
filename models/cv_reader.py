# ============================================
# cv_reader.py — AI Powered CV Reader Class
# Reads an uploaded .docx or .pdf CV file and uses
# OpenAI to extract details accurately
# Works with any CV format
# ============================================

import os
import json
from docx import Document
import fitz  # PyMuPDF — for reading PDF files
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class CVReader:
    """
    Reads an uploaded Word document or PDF CV and uses
    OpenAI to extract key details accurately.
    Works with any CV format regardless of structure.
    """

    def __init__(self, file, filename):
        """
        Constructor — takes the uploaded file and its filename.
        Filename is used to detect whether it's .docx or .pdf
        """
        self.file = file                # The uploaded file
        self.filename = filename        # Original filename — used to detect file type
        self.raw_text = ""              # Raw text extracted from the document

        # Configure OpenAI client with API key from .env file
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def read_docx(self):
        """
        Reads a .docx file and extracts all text content.
        """
        doc = Document(self.file)

        paragraphs = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)

        self._apply_cutoff(paragraphs)

    def read_pdf(self):
        """
        Reads a .pdf file and extracts all text content using PyMuPDF.
        """
        # Read the PDF bytes
        pdf_bytes = self.file.read()

        # Open the PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        paragraphs = []
        for page in pdf_document:
            text = page.get_text()
            # Split text into lines and clean up
            for line in text.split("\n"):
                line = line.strip()
                if line:
                    paragraphs.append(line)

        pdf_document.close()
        self._apply_cutoff(paragraphs)

    def _apply_cutoff(self, paragraphs):
        """
        Stops reading at motivation letter or cover letter if present.
        Keeps only CV content before that point.
        """
        cutoff_keywords = [
            "dear hiring", "dear sir", "dear madam",
            "motivation letter", "cover letter",
            "to whom it may concern"
        ]
        cutoff_index = len(paragraphs)
        for i, para in enumerate(paragraphs):
            if any(kw in para.lower() for kw in cutoff_keywords):
                cutoff_index = i
                break

        self.raw_text = "\n".join(paragraphs[:cutoff_index])

    def read_file(self):
        """
        Reads the uploaded file — detects whether it's .docx or .pdf
        and calls the appropriate reading method.
        """
        if self.filename.lower().endswith(".pdf"):
            self.read_pdf()
        else:
            self.read_docx()

    def extract_with_ai(self):
        """
        Sends the CV text to OpenAI and asks it
        to extract all key details accurately.
        Returns a dictionary of extracted details.
        """

        # Build the prompt for OpenAI
        prompt = f"""You are a CV parser. Read the following CV text and extract the details.
Return ONLY a JSON object with exactly these fields — no extra text, no markdown, no backticks:

{{
    "first_name": "first name only",
    "last_name": "last name and any middle names",
    "email": "email address",
    "phone": "phone number",
    "address": "full address",
    "summary": "profile summary or objective paragraph",
    "education": "all education entries separated by newlines",
    "experience": "all work experience entries separated by newlines",
    "skills": "all skills separated by commas",
    "languages": "all languages separated by commas"
}}

If a field is not found in the CV, return an empty string for that field.
Do not include any explanation or extra text — only the JSON object.

CV TEXT:
{self.raw_text}
"""

        try:
            # Send to OpenAI and get response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.choices[0].message.content.strip()
            #print("RAW AI RESPONSE:", response_text)  # Debug line

            # Clean up response — remove any markdown backticks if present
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            # Parse the JSON response
            extracted = json.loads(response_text)

            return extracted

        except Exception as e:
            print(f"AI extraction error: {e}")
            # Return empty fields if AI fails
            return {
                "first_name": "",
                "last_name": "",
                "email": "",
                "phone": "",
                "address": "",
                "summary": "",
                "education": "",
                "experience": "",
                "skills": "",
                "languages": ""
            }

    def extract_all(self):
        """
        Main method — reads the CV and extracts all details using AI.
        Returns a dictionary ready to auto fill the form.
        """
        # First read the document — detects .docx or .pdf automatically
        self.read_file()

        # Use AI to extract details
        extracted = self.extract_with_ai()

        return extracted
