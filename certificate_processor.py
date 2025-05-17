import cv2
import hashlib
import pytesseract
import re
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_image(image_path):
    """Preprocess the certificate image for better OCR results."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image from {image_path}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(binary)
    except Exception as e:
        logger.error(f"Error during image preprocessing: {str(e)}")
        raise

def extract_text(processed_image):
    """Extract text from the processed image."""
    try:
        text = pytesseract.image_to_string(processed_image, lang='eng')
        return text
    except Exception as e:
        logger.error(f"Error during text extraction: {str(e)}")
        raise

def extract_field(pattern, text):
    """Extract a specific field using regex pattern."""
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else "Not Found"
    except Exception as e:
        logger.error(f"Error extracting field with pattern {pattern}: {str(e)}")
        return "Error"

def process_certificate(image_path):
    """Process certificate image and extract all relevant information."""
    try:
        processed_image = preprocess_image(image_path)
        text = extract_text(processed_image)

        # Regex patterns as in 2.py
        degree_serial = extract_field(r'Degree Serial No\.?\s*([0-9]{10,})', text)
        enrollment_no = extract_field(r'Enrolment No\.?\s*([A-Z]{2}-[0-9]+)', text)
        roll_no = extract_field(r'Roll No\.?\s*([0-9]{7,})', text)

        # Name extraction with fallback
        name = extract_field(r'This is to certify that\s*([A-Za-z ]+)', text)
        if name == "Not Found":
            name = extract_field(r'\n([A-Z][a-z]+ [A-Z][a-z]+)\n', text)

        # Passing year
        passing_year = extract_field(r'examination of\s*(\d{4})', text)

        # CGPA
        cgpa = extract_field(r'CGPA\s*([0-9]+\.[0-9]+)', text)

        # Degree extraction with fallbacks
        degree = extract_field(r'Degree of\s*([A-Za-z ]+)', text)
        if degree == "Not Found":
            degree = extract_field(r'awarded the Degree of\s*([A-Za-z ]+)', text)
        if degree == "Not Found":
            degree = extract_field(r'\n([A-Za-z ]{10,})\n', text)

        # Issue date extraction with fallbacks
        issue_date = extract_field(r'Date[:\s]*([0-9]{1,2}[a-z]{2}\s+\w+\s+[0-9]{4})', text)
        if issue_date == "Not Found":
            issue_date = extract_field(r'Date[:\s]*([0-9]{1,2}\w*\s+\w+\s+[0-9]{4})', text)
        if issue_date == "Not Found":
            issue_date = extract_field(r'Date[:\s]*([0-9]{1,2}th\s+\w+\s+[0-9]{4})', text)

        data = {
            "degree_serial": degree_serial,
            "enrollment_no": enrollment_no,
            "roll_no": roll_no,
            "name": name,
            "degree": degree,
            "cgpa": cgpa,
            "passing_year": passing_year,
            "issue_date": issue_date
        }

        # Generate hash for the certificate data
        data_string = f"{data['degree_serial']}|{data['enrollment_no']}|{data['roll_no']}|{data['name']}|{data['cgpa']}|{data['passing_year']}|{data['degree']}".lower()
        data['hash'] = hashlib.sha256(data_string.encode()).hexdigest()

        return data

    except Exception as e:
        logger.error(f"Error processing certificate: {str(e)}")
        raise
