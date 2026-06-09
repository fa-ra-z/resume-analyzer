import fitz  # This is PyMuPDF - reads PDF files
import re    # This helps us clean up the text

def extract_text_from_pdf(uploaded_file):
    """
    Takes an uploaded PDF file from Streamlit
    Returns the text inside it as a plain string
    """
    # fitz.open reads the PDF from memory (the uploaded file)
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    full_text = ""
    
    # Loop through every page of the PDF
    for page in doc:
        full_text += page.get_text()  # Extract text from this page
    
    return clean_text(full_text)


def clean_text(text):
    """
    Removes messy characters and extra blank lines
    """
    # Replace 3+ newlines with just 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove weird non-English characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    return text.strip()