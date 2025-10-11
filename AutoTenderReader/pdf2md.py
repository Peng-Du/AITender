import argparse
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import re
import os

# Reminder: Ensure Tesseract is installed and in your PATH.
# For Windows, you might need to set the command path explicitly:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Reminder: Ensure Poppler is installed and its 'bin' directory is in your PATH.

def has_significant_text(pdf_path, min_words_per_page=10):
    """Check if a PDF contains a significant amount of extractable text by counting words."""
    total_words = 0
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            # Check the first few pages to make a decision
            pages_to_check = pdf.pages[:min(3, len(pdf.pages))]
            if not pages_to_check:
                return False

            for page in pages_to_check:
                text = page.extract_text()
                if text:
                    # Count sequences of alphabetic characters as words, including Spanish accents
                    words = re.findall(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]{2,}', text)
                    total_words += len(words)
            
            avg_words = total_words / len(pages_to_check)
            print(f"DEBUG: Found an average of {avg_words:.2f} words per page.")
            return avg_words > min_words_per_page
    except Exception as e:
        print(f"Could not check for text due to: {e}")
        return False

def convert_pdf_direct(pdf_path):
    """Directly extract text from a PDF."""
    print("Attempting direct text extraction...")
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + f"\n\n--- Page {i+1} ---\n\n"
    return text

def convert_pdf_ocr(pdf_path, lang='spa'):
    """Extract text from a PDF using OCR."""
    print("Falling back to OCR extraction...")
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for i, image in enumerate(images):
            print(f"OCR processing page {i+1}/{len(images)}")
            pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
            page_text = pytesseract.image_to_string(image, lang='spa')
            text += page_text + f"\n\n--- Page {i+1} ---\n\n"
    except Exception as e:
        return f"OCR conversion failed: {e}. Make sure Poppler and Tesseract are installed and in your system's PATH."
    return text

def main():
    parser = argparse.ArgumentParser(description='Convert a PDF to a Markdown file, using OCR as a fallback.')
    parser.add_argument('input_pdf', help='The path to the input PDF file.')
    parser.add_argument('output_md', help='The path for the output Markdown file.')
    args = parser.parse_args()

    pdf_path = args.input_pdf
    md_path = args.output_md

    if not os.path.exists(pdf_path):
        print(f"Error: Input file not found at {pdf_path}")
        return

    print(f"Processing {pdf_path}...")
    if has_significant_text(pdf_path):
        final_text = convert_pdf_direct(pdf_path)
    else:
        final_text = convert_pdf_ocr(pdf_path)

    try:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(final_text)
        print(f"\nSuccessfully converted {pdf_path} to {md_path}")
    except Exception as e:
        print(f"\nFailed to write to output file: {e}")

if __name__ == "__main__":
    main()