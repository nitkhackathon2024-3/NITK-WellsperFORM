from flask import Flask, request, render_template, jsonify
import PyPDF2
import re

app = Flask(__name__)

# Function to extract common fields (Name, DOB, VID, Aadhaar Number) from the text
def extract_fields(text):
    details = {}
    general_text = text.strip()

    # Name extraction (using terms like "Name", "Full Name")
    name_match = re.search(r'(?i)(Name[:\s]*|Full Name[:\s]*)([A-Za-z\s]+)', text)
    if name_match:
        details['Name'] = name_match.group(2).strip()
        general_text = general_text.replace(name_match.group(0), '')  # Remove matched text from general

    # Date of Birth extraction (formats like DD/MM/YYYY, DD-MM-YYYY)
    dob_match = re.search(r'\b(?:[0-2][0-9]|3[0-1])[- /.](?:0[1-9]|1[0-2])[- /.](?:19|20)\d\d\b', text)
    if dob_match:
        details['Date of Birth'] = dob_match.group(0)
        general_text = general_text.replace(dob_match.group(0), '')

    # VID (12 to 16 digit numbers)
    vid_match = re.search(r'\b\d{12,16}\b', text)
    if vid_match:
        details['VID'] = vid_match.group(0)
        general_text = general_text.replace(vid_match.group(0), '')

    # Aadhaar Number (Typically 12-digit numbers, formatted in 4-digit blocks)
    aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    if aadhaar_match:
        details['Aadhaar Number'] = aadhaar_match.group(0)
        general_text = general_text.replace(aadhaar_match.group(0), '')

    return details, general_text.strip()

# Home route to render the upload form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file uploads and extract PDF fields
@app.route('/extract-fields', methods=['POST'])
def extract_fields_route():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400

    pdf_file = request.files['pdf']
    
    try:
        # Extract fields from the uploaded PDF
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""

        # Extract text from each page and append
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()

        # Extract structured fields and general unstructured text
        extracted_details, general_text = extract_fields(text)

        if not extracted_details and not general_text:
            return jsonify({'error': 'No relevant fields or text found'}), 404

        return jsonify({
            'extracted_fields': extracted_details,
            'general_text': general_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
