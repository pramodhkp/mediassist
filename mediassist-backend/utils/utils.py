import os
import pdfplumber

def parse_pdf(file_path):
    """
    Parse a PDF file and extract its text content using pdfplumber.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        # Open the PDF file
        with pdfplumber.open(file_path) as pdf:
            # Extract text from each page
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
        
        return text
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"