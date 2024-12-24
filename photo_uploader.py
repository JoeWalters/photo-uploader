from flask import Flask, request, redirect, render_template, url_for, send_from_directory
import os

# Configuration
DEFAULT_UPLOAD_FOLDER = '/Uploads/'  # Default directory for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = DEFAULT_UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    if request.method == 'POST':
        new_folder = request.form.get('upload_folder', '').strip()
        if new_folder:
            app.config['UPLOAD_FOLDER'] = new_folder
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        return redirect(url_for('settings'))
    current_folder = app.config['UPLOAD_FOLDER']
    return render_template('settings.html', current_folder=current_folder)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)