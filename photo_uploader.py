import os
import subprocess
import sys
from flask import Flask, request, redirect, render_template, url_for, send_from_directory
from PIL import Image, ExifTags
from datetime import datetime

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

# Configuration
UPLOAD_FOLDER = '/Users/'  # Path to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_HEIGHT = 1080
MAX_WIDTH = 1920

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_HEIGHT'] = MAX_HEIGHT
app.config['MAX_WIDTH'] = MAX_WIDTH

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if a file is an allowed image type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path):
    """Resize an image to fit within the configured maximum dimensions."""
    with Image.open(image_path) as img:
        # Correct the orientation based on EXIF data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                orientation_value = exif.get(orientation)
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass  # EXIF data might be missing or unreadable

        # Resize the image
        img.thumbnail((app.config['MAX_WIDTH'], app.config['MAX_HEIGHT']), Image.Resampling.LANCZOS)
        img.save(image_path)

def get_image_metadata(file_path):
    """Retrieve metadata for an image file."""
    try:
        mod_time = os.path.getmtime(file_path)
    except OSError:
        mod_time = 0
    return {
        "name": os.path.basename(file_path),
        "mod_time": datetime.fromtimestamp(mod_time)
    }

@app.route('/')
def index():
    """Main route for the image gallery."""
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    images = [file for file in files if allowed_file(file)]
    sort_by = request.args.get('sort_by', 'name')  # Default sort by name
    image_metadata = [
        get_image_metadata(os.path.join(app.config['UPLOAD_FOLDER'], image))
        for image in images
    ]

    if sort_by == 'date':
        image_metadata.sort(key=lambda x: x['mod_time'], reverse=True)  # Newest first
    else:
        image_metadata.sort(key=lambda x: x['name'])  # Alphabetical order

    return render_template('index.html', images=image_metadata, sort_by=sort_by)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Route for uploading images."""
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
    """Route for deleting an image."""
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
    """Route to serve uploaded images."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Route for updating application settings."""
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