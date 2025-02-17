from flask import Flask, render_template, request, send_file, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import os
import pandas as pd
from datetime import datetime
import uuid
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
from io import BytesIO


app = Flask(__name__)

UPLOAD_FOLDER = 'static/templates'
ALLOWED_EXTENSIONS = {'jpg', 'pdf'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-templates', methods=['POST'])
def upload_templates():
    if 'jpgTemplate' not in request.files or 'pdfTemplate' not in request.files:
        return jsonify({'error': 'Both templates are required'}), 400
    
    jpg_file = request.files['jpgTemplate']
    pdf_file = request.files['pdfTemplate']
    
    # Check if files are selected
    if jpg_file.filename == '' or pdf_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate filenames
    if jpg_file.filename != 'certificate-template.jpg' or pdf_file.filename != 'certificate-template.pdf':
        return jsonify({'error': 'Invalid filename'}), 400
    
    try:
        # Save the files
        jpg_file.save(os.path.join(UPLOAD_FOLDER, 'certificate-template.jpg'))
        pdf_file.save(os.path.join(UPLOAD_FOLDER, 'certificate-template.pdf'))
        return jsonify({'message': 'Files uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register fonts
def register_fonts():
    font_dir = os.path.join(app.root_path, 'static', 'fonts')
    fonts = {
        'CooperBlkBT-Italic': 'CooperBlkBT-Italic.ttf',
        'CooperBlkBT-Regular': 'CooperBlkBT-Regular.ttf',
        'CooperLtBT-Bold': 'CooperLtBT-Bold.ttf',
        'CooperLtBT-BoldItalic': 'CooperLtBT-BoldItalic.ttf',
        'CooperLtBT-Italic': 'CooperLtBT-Italic.ttf',
        'CooperLtBT-Regular': 'CooperLtBT-Regular.ttf',
        'CooperMdBT-Regular': 'CooperMdBT-Regular.ttf'
    }
    
    for font_name, font_file in fonts.items():
        font_path = os.path.join(font_dir, font_file)
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        except Exception as e:
            print(f"Error registering font {font_name}: {e}")

# Load font mapping
FONT_MAPPING = {
    'Arial': 'Helvetica',
    'Times New Roman': 'Times-Roman',
    'CooperBlkBT-Italic': 'CooperBlkBT-Italic',
    'CooperBlkBT-Regular': 'CooperBlkBT-Regular',
    'CooperLtBT-Bold': 'CooperLtBT-Bold',
    'CooperLtBT-BoldItalic': 'CooperLtBT-BoldItalic',
    'CooperLtBT-Italic': 'CooperLtBT-Italic',
    'CooperLtBT-Regular': 'CooperLtBT-Regular',
    'CooperMdBT-Regular': 'CooperMdBT-Regular'
}

def load_courses():
    if os.path.exists('courses.json'):
        with open('courses.json', 'r') as file:
            return json.load(file)
    return []

def save_courses(courses):
    with open('courses.json', 'w') as file:
        json.dump(courses, file, indent=2)

def load_positions():
    try:
        with open('positions.json', 'r') as file:
            positions = json.load(file)
            # Ensure fontSize is stored as a number without 'px'
            for element in positions.values():
                element['fontSize'] = str(element.get('fontSize', '16')).replace('px', '')
            return positions
    except (FileNotFoundError, json.JSONDecodeError):
        default_positions = {
            'name': {
                'top': '280',
                'left': '442',
                'fontSize': '46',
                'fontStyle': 'CooperBlkBT-Italic'
            },
            'certificate_id': {
                'top': '600',
                'left': '160',
                'fontSize': '16',
                'fontStyle': 'CooperBlkBT-Italic'
            },
            'course_duration': {
                'top': '600',
                'left': '850',
                'fontSize': '16',
                'fontStyle': 'CooperLtBT-Italic'
            }
        }
        save_positions(default_positions)
        return default_positions

def save_positions(positions):
    cleaned_positions = {}
    for key, value in positions.items():
        cleaned_positions[key] = {
            'top': str(value.get('top', '0')).replace('px', ''),
            'left': str(value.get('left', '0')).replace('px', ''),
            'fontSize': str(value.get('fontSize', '16')).replace('px', ''),
            'fontStyle': value.get('fontStyle', 'CooperBlkBT-Italic')
        }
    
    with open('positions.json', 'w') as file:
        json.dump(cleaned_positions, file, indent=2)
        
def generate_certificate(user_name, course_duration, certificate_id, positions, output):
    page_width, page_height = landscape(letter)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))

    def convert_coordinates(web_x, web_y, web_width=1084, web_height=799):
        pdf_x = (float(web_x) / web_width) * page_width
        pdf_y = page_height - ((float(web_y) / web_height) * page_height)
        return pdf_x, pdf_y

    for elem_id, content in {
        'name': user_name,
        'certificate_id': certificate_id,
        'course_duration': course_duration
    }.items():
        if elem_id in positions:
            pos = positions[elem_id]
            x, y = convert_coordinates(pos['left'], pos['top'])

            font_name = FONT_MAPPING.get(pos['fontStyle'].strip("'"), 'Helvetica')
            font_size = float(str(pos['fontSize']).replace('px', ''))

            try:
                c.setFont(font_name, font_size)

                # Calculate text width and adjust x to center it dynamically
                text_width = c.stringWidth(str(content), font_name, font_size)
                centered_x = x - (text_width / 2)

                c.drawString(centered_x, y, str(content))

                # Add underline for the user name
                if elem_id == 'name':
                    line_y = y - 2  # Slightly below the text
                    c.line(centered_x, line_y, centered_x + text_width, line_y)

            except Exception as e:
                print(f"Error with font {font_name}: {e}")
                c.setFont('Helvetica', font_size)
                c.drawString(x, y, str(content))

    c.save()
    buffer.seek(0)

    template_path = os.path.join('static', 'templates', 'certificate-template.pdf')
    reader = PdfReader(template_path)
    template_page = reader.pages[0]

    overlay = PdfReader(buffer)
    overlay_page = overlay.pages[0]

    template_page.merge_page(overlay_page)

    writer = PdfWriter()
    writer.add_page(template_page)

    if isinstance(output, io.BytesIO):
        writer.write(output)
    else:
        with open(output, 'wb') as output_file:
            writer.write(output_file)

    buffer.close()

# Add this new route to Flask (app.py)
@app.route('/delete-templates', methods=['POST'])
def delete_templates():
    try:
        jpg_path = os.path.join(UPLOAD_FOLDER, 'certificate-template.jpg')
        pdf_path = os.path.join(UPLOAD_FOLDER, 'certificate-template.pdf')
        
        # Delete files if they exist
        if os.path.exists(jpg_path):
            os.remove(jpg_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
        return jsonify({'message': 'Templates deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add this new route to check template existence
@app.route('/check-templates', methods=['GET'])
def check_templates():
    try:
        jpg_exists = os.path.exists(os.path.join(UPLOAD_FOLDER, 'certificate-template.jpg'))
        pdf_exists = os.path.exists(os.path.join(UPLOAD_FOLDER, 'certificate-template.pdf'))
        
        return jsonify({
            'jpg_exists': jpg_exists,
            'pdf_exists': pdf_exists
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/certificate-form')
def certificate_form():
    return render_template('course_form.html')

# Update the root route to serve the new page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save-positions', methods=['POST'])
def save_positions_route():
    try:
        positions = request.json
        save_positions(positions)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get-positions', methods=['GET'])
def get_positions():
    try:
        positions = load_positions()
        return jsonify(positions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    try:
        user_name = request.form.get('user_name', '')
        course_duration = request.form.get('course_duration', '')
        certificate_id = request.form.get('certificate_id', '')
        
        positions = load_positions()
        output_path = 'generated_certificate.pdf'
        
        generate_certificate(user_name, course_duration, certificate_id, positions, output_path)
        
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'csv_file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['csv_file']
    if file.filename == '' or not file.filename.endswith('.csv'):
        return 'Invalid file', 400

    try:
        # Read CSV and generate certificates
        df = pd.read_csv(file)
        positions = load_positions()

        # Create an in-memory ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for _, row in df.iterrows():
                output_pdf = io.BytesIO()
                generate_certificate(
                    row.get('user_name', ''),
                    row.get('course_duration', ''),
                    row.get('certificate_id', ''),
                    positions,
                    output_pdf
                )
                output_pdf.seek(0)
                zipf.writestr(f"certificate_{uuid.uuid4()}.pdf", output_pdf.getvalue())

        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='certificates.zip')
    except Exception as e:
        return f'Error generating certificates: {str(e)}', 500



@app.route('/course/<course_name>', methods=['GET', 'POST'])
def course_page(course_name):
    if request.method == 'GET':
        return render_template('course_form.html', course_name=course_name)
    return certificate_preview()

@app.route('/certificate-preview', methods=['POST'])
def certificate_preview():
    return render_template(
        'certificate_preview.html',
        user_name=request.form.get('user_name'),
        course_duration=request.form.get('course_duration'),
        certificate_id=request.form.get('certificate_id'),
        course_name=request.form.get('course_name')
    )

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/fonts', exist_ok=True)
    os.makedirs('static/certificates', exist_ok=True)
    
    # Register fonts
    register_fonts()
    
    # Initialize positions.json if it doesn't exist
    if not os.path.exists('positions.json'):
        default_positions = {
            'name': {'top': '280', 'left': '442', 'fontSize': '46', 'fontStyle': 'CooperBlkBT-Italic'},
            'certificate_id': {'top': '600', 'left': '160', 'fontSize': '16', 'fontStyle': 'CooperBlkBT-Italic'},
            'course_duration': {'top': '600', 'left': '850', 'fontSize': '16', 'fontStyle': 'CooperBlkBT-Italic'}
        }
        save_positions(default_positions)
    
    app.run(debug=True)