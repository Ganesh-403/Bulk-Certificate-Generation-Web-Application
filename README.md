# Certificate Generator

A modern, Flask-based web application for generating customizable certificates with a streamlined user interface. Developed by Anad Bora.

## Features

- Clean, modern user interface with responsive design
- Simplified certificate generation workflow
- Upload and manage certificate templates (JPG/PDF)
- Drag-and-drop interface for text positioning
- Customizable font styles and sizes
- Bulk certificate generation using CSV upload
- Real-time certificate preview
- PDF certificate generation
- Multiple font family support (Cooper font family)

## Prerequisites

- Python 3.7+
- Flask
- ReportLab
- PyPDF2
- Pandas
- Additional Python packages (see requirements.txt)

## Project Structure

```
certificate-generator/
├── static/
│   ├── templates/     # Certificate templates
│   └── fonts/         # Font files
├── templates/
│   ├── index.html            # Modern landing page
│   ├── certificate_form.html  # Streamlined certificate form
│   └── certificate_preview.html   # Preview and positioning
├── app.py                    # Main Flask application
└── positions.json           # Text position configurations
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd certificate-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up the required directories:
```bash
mkdir -p static/templates static/fonts
```

5. Place Cooper font family files in the `static/fonts` directory:
- CooperBlkBT-Italic.ttf
- CooperBlkBT-Regular.ttf
- CooperLtBT-Bold.ttf
- CooperLtBT-BoldItalic.ttf
- CooperLtBT-Italic.ttf
- CooperLtBT-Regular.ttf
- CooperMdBT-Regular.ttf

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Access the application at `http://localhost:5000`

3. Certificate Generation:
   - Click on "Generate Certificate" from the main menu
   - Enter certificate details
   - Use the drag-and-drop interface to position text
   - Preview and download the generated PDF

4. Bulk Certificate Generation:
   - Prepare a CSV file with columns:
     - user_name
     - course_duration
     - certificate_id
   - Upload the CSV file
   - Download the ZIP file containing all certificates

## API Endpoints

- `GET /`: Modern landing page
- `GET /certificate-form`: Streamlined certificate generation form
- `POST /upload-templates`: Upload certificate templates
- `POST /save-positions`: Save text element positions
- `POST /download-pdf`: Generate and download certificate PDF
- `POST /upload-csv`: Bulk certificate generation

## File Requirements

### Templates
- JPG Template: `certificate-template.jpg`
- PDF Template: `certificate-template.pdf`

### CSV Format for Bulk Generation
```csv
user_name,course_duration,certificate_id
John Doe,6 Months,CERT001
Jane Smith,3 Months,CERT002
```

## Development

To run the application in debug mode:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## UI Features

- Modern, minimalist design
- Responsive layout
- Intuitive navigation
- Clean button styling
- Consistent color scheme
- Mobile-friendly interface

## Browser Compatibility

Tested and supported on:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Security Considerations

- Input validation for all form fields
- Secure file handling for uploads
- File type restrictions
- Error handling for malformed requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Developed by Anand Bora

For questions or support, please open an issue in the repository.