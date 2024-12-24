import os
import subprocess
import sys
from flask import Flask, request, redirect, render_template, url_for, send_from_directory

# Ensure Pillow is installed
def ensure_pillow_installed():
    try:
        from PIL import Image  # Check if Pillow is installed
    except ImportError:
        print("Pillow is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        print("Pillow installed successfully.")
        from PIL import Image  # Import Pillow after installation

ensure_pillow_installed()

from PIL import Image

# Configuration
DEFAULT_UPLOAD_FOLDER = '/Users/'  # Default directory for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DEFAULT_MAX_HEIGHT = 1080
DEFAULT_MAX_WIDTH = 1920

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = DEFAULT_UPLOAD_FOLDER
app.config['MAX_HEIGHT'] = DEFAULT_MAX_HEIGHT
app.config['MAX_WIDTH'] = DEFAULT_MAX_WIDTH

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path):
    """Resize an image to fit within the configured maximum height and width."""
    max_height = app.config['MAX_HEIGHT']
    max_width = app.config['MAX_WIDTH']
    with Image.open(image_path) as img:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
        img.save(image_path)

@app.route('/')
def index():
    # List all files in the upload directory
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    images = [file for file in files if allowed_file(file)]
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return "No file part", 400
    
    files = request.files.getlist('files')  # Get all selected files
    if not files or all(file.filename == '' for file in files):
        return "No files selected", 400
    
    for file in files:
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            resize_image(file_path)  # Resize the image after saving

    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return redirect(url_for('index'))
        else:
            return f"File {filename} not found", 404
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global ALLOWED_EXTENSIONS
    error_messages = []

    if request.method == 'POST':
        new_folder = request.form.get('upload_folder', '').strip()
        new_extensions = request.form.get('allowed_extensions', '').strip()
        max_height = request.form.get('max_height', '').strip()
        max_width = request.form.get('max_width', '').strip()

        # Validate Upload Folder
        if new_folder:
            try:
                app.config['UPLOAD_FOLDER'] = new_folder
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            except Exception as e:
                error_messages.append(f"Error with upload folder: {str(e)}")
        else:
            error_messages.append("Upload folder cannot be empty.")

        # Validate Allowed Extensions
        if new_extensions:
            try:
                new_extensions_set = set(ext.strip().lower() for ext in new_extensions.split(',') if ext.strip())
                if not new_extensions_set:
                    raise ValueError("No valid extensions provided.")
                ALLOWED_EXTENSIONS = new_extensions_set
            except Exception as e:
                error_messages.append(f"Error with allowed extensions: {str(e)}")
        else:
            error_messages.append("Allowed extensions cannot be empty.")

        # Validate Height and Width
        try:
            if max_height:
                app.config['MAX_HEIGHT'] = int(max_height)
            if max_width:
                app.config['MAX_WIDTH'] = int(max_width)
        except ValueError:
            error_messages.append("Height and width must be valid integers.")

        if not error_messages:
            return redirect(url_for('settings'))

    current_folder = app.config['UPLOAD_FOLDER']
    current_extensions = ', '.join(ALLOWED_EXTENSIONS)
    max_height = app.config['MAX_HEIGHT']
    max_width = app.config['MAX_WIDTH']
    return render_template(
        'settings.html',
        current_folder=current_folder,
        current_extensions=current_extensions,
        max_height=max_height,
        max_width=max_width,
        error_messages=error_messages
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)