import os
import subprocess
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
COMPRESSED_FOLDER = 'static/compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

GS_PATH = r'C:\Program Files\gs\gs10.04.0\bin\gswin64c.exe'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    compressed_file_path = os.path.join(COMPRESSED_FOLDER, f'compressed_{file.filename}')

    gs_command = [
        GS_PATH,
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/screen',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={compressed_file_path}',
        file_path
    ]

    try:
        subprocess.run(gs_command, check=True)
        return f'File compressed successfully! <a href=\"/download/compressed_{file.filename}\">Download</a>'
    except subprocess.CalledProcessError as e:
        return f'Compression failed: {str(e)}', 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(COMPRESSED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
app.py
