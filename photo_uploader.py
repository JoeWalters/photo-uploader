import os
import subprocess
import sys
import logging
import json
import argparse
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, render_template, url_for, send_from_directory, flash, jsonify
from PIL import Image, ExifTags
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('photo_uploader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure Pillow is installed
def ensure_pillow_installed():
    try:
        from PIL import Image  # Check if Pillow is installed
    except ImportError:
        logger.info("Pillow is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        logger.info("Pillow installed successfully.")
        from PIL import Image  # Import Pillow after installation

ensure_pillow_installed()

def get_app_version():
    """Get application version from version.txt file (created during Docker build)"""
    version_file = Path(__file__).parent / 'version.txt'
    try:
        if version_file.exists():
            with open(version_file, 'r') as f:
                version = f.read().strip()
                return version if version and version != 'unknown' else None
    except Exception as e:
        logger.debug(f"Could not read version file: {e}")
    
    # Fallback for development/non-Docker environments
    # Try to get version from environment variable (can be set in docker-compose)
    env_version = os.environ.get('APP_VERSION')
    if env_version:
        return env_version
    
    # If running in development, return a dev indicator
    return "dev" if not os.path.exists('/app/version.txt') else None

def load_config():
    """Load configuration from config/config.json file"""
    config_file = Path(__file__).parent / 'config' / 'config.json'
    
    # Default configuration
    default_config = {
        "server": {
            "host": "0.0.0.0",
            "port": 5001,
            "debug": False
        },
        "upload": {
            "folder": "~/photo_uploads",
            "max_file_size_mb": 10,
            "allowed_extensions": ["png", "jpg", "jpeg", "gif", "webp"]
        },
        "image_processing": {
            "max_width": 1920,
            "max_height": 1080,
            "auto_rotate": True,
            "optimize": True,
            "quality": 85
        }
    }
    
    try:
        if config_file.exists():
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            # Merge with defaults (file config overrides defaults)
            config = default_config.copy()
            if 'server' in file_config:
                config['server'].update(file_config['server'])
            if 'upload' in file_config:
                config['upload'].update(file_config['upload'])
            if 'image_processing' in file_config:
                config['image_processing'].update(file_config['image_processing'])
                
            logger.info("Configuration loaded from config/config.json")
            return config
        else:
            # Create default config file
            config_file.parent.mkdir(exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info("Created default config/config.json")
            return default_config
            
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading config file: {e}")
        logger.info("Using default configuration")
        return default_config

def parse_command_line_args(config):
    """Parse command line arguments and override config settings"""
    parser = argparse.ArgumentParser(description='Photo Uploader Server')
    parser.add_argument('--upload-folder', help='Upload folder path')
    parser.add_argument('--port', type=int, help='Port to run server on')
    parser.add_argument('--host', help='Host to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--max-file-size', type=int, help='Maximum file size in MB')
    
    args = parser.parse_args()
    
    # Override config with environment variables first (Docker support)
    env_upload_folder = os.environ.get('UPLOAD_FOLDER')
    env_port = os.environ.get('PORT')
    env_host = os.environ.get('HOST')
    env_debug = os.environ.get('DEBUG', '').lower() in ('true', '1', 'yes')
    env_max_file_size = os.environ.get('MAX_FILE_SIZE')
    
    if env_upload_folder:
        config['upload']['folder'] = env_upload_folder
    if env_port:
        try:
            config['server']['port'] = int(env_port)
        except ValueError:
            logger.warning(f"Invalid PORT environment variable: {env_port}")
    if env_host:
        config['server']['host'] = env_host
    if env_debug:
        config['server']['debug'] = True
    if env_max_file_size:
        try:
            config['upload']['max_file_size_mb'] = int(env_max_file_size)
        except ValueError:
            logger.warning(f"Invalid MAX_FILE_SIZE environment variable: {env_max_file_size}")
    
    # Override config with command line arguments (highest priority)
    if args.upload_folder:
        config['upload']['folder'] = args.upload_folder
    if args.port:
        config['server']['port'] = args.port
    if args.host:
        config['server']['host'] = args.host
    if args.debug:
        config['server']['debug'] = True
    if args.max_file_size:
        config['upload']['max_file_size_mb'] = args.max_file_size
    
    return config

def save_config_to_file(config):
    """Save configuration back to config file"""
    config_file = Path(__file__).parent / 'config' / 'config.json'
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except IOError as e:
        logger.error(f"Failed to save config: {e}")
        return False

# Load and parse configuration
config = load_config()
config = parse_command_line_args(config)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configure Flask app from config
app.config['UPLOAD_FOLDER'] = os.path.expanduser(config['upload']['folder'])
app.config['MAX_HEIGHT'] = config['image_processing']['max_height']
app.config['MAX_WIDTH'] = config['image_processing']['max_width']
app.config['MAX_CONTENT_LENGTH'] = config['upload']['max_file_size_mb'] * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = set(config['upload']['allowed_extensions'])
app.config['AUTO_ROTATE'] = config['image_processing']['auto_rotate']
app.config['OPTIMIZE'] = config['image_processing']['optimize']
app.config['QUALITY'] = config['image_processing']['quality']

# Store config globally for settings updates
app.config['APP_CONFIG'] = config

# Get and store application version
app_version = get_app_version()
app.config['APP_VERSION'] = app_version

# Template context processor to make version available in all templates
@app.context_processor
def inject_version():
    return {
        'app_version': app.config.get('APP_VERSION'),
        'version_display': f"v{app.config.get('APP_VERSION')}" if app.config.get('APP_VERSION') else None
    }

# Ensure the upload folder exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"Upload folder ready: {app.config['UPLOAD_FOLDER']}")
except Exception as e:
    logger.error(f"Failed to create upload folder: {e}")
    sys.exit(1)

def allowed_file(filename):
    """Check if a file is an allowed image type."""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in app.config['ALLOWED_EXTENSIONS']

def resize_image(image_path):
    """Resize an image to fit within the configured maximum dimensions."""
    try:
        with Image.open(image_path) as img:
            # Correct the orientation based on EXIF data if enabled
            if app.config['AUTO_ROTATE']:
                try:
                    # Get EXIF data
                    exif = img.getexif()
                    if exif is not None:
                        # Look for orientation tag (274 is the standard EXIF orientation tag)
                        orientation = exif.get(274, 1)  # Default to 1 (normal) if not found
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)
                except (AttributeError, KeyError, IndexError) as e:
                    logger.debug(f"EXIF orientation correction failed for {image_path}: {e}")
                    pass  # EXIF data might be missing or unreadable

            # Resize the image if needed
            original_size = img.size
            img.thumbnail((app.config['MAX_WIDTH'], app.config['MAX_HEIGHT']), Image.Resampling.LANCZOS)
            
            # Save the image with configured settings
            save_kwargs = {}
            if img.format == 'JPEG' or image_path.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['quality'] = app.config['QUALITY']
            if app.config['OPTIMIZE']:
                save_kwargs['optimize'] = True
                
            img.save(image_path, **save_kwargs)
            
            new_size = img.size
            if original_size != new_size:
                logger.info(f"Resized image {os.path.basename(image_path)} from {original_size} to {new_size}")
                
    except Exception as e:
        logger.error(f"Failed to resize image {image_path}: {e}")
        raise

def get_image_metadata(file_path):
    """Retrieve metadata for an image file."""
    try:
        stat = os.stat(file_path)
        file_size = stat.st_size
        mod_time = stat.st_mtime
        
        # Try to get image dimensions
        width, height = None, None
        try:
            with Image.open(file_path) as img:
                width, height = img.size
        except Exception as e:
            logger.debug(f"Could not get image dimensions for {file_path}: {e}")
        
        return {
            "name": os.path.basename(file_path),
            "mod_time": datetime.fromtimestamp(mod_time),
            "size": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "width": width,
            "height": height
        }
    except OSError as e:
        logger.error(f"Failed to get metadata for {file_path}: {e}")
        return {
            "name": os.path.basename(file_path),
            "mod_time": datetime.fromtimestamp(0),
            "size": 0,
            "size_mb": 0,
            "width": None,
            "height": None
        }

@app.route('/')
def index():
    """Main route for the image gallery."""
    try:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            flash('Upload folder does not exist. Please check settings.', 'error')
            return render_template('index.html', images=[], sort_by='name', sort_order='asc')
        
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        images = [file for file in files if allowed_file(file)]
        sort_by = request.args.get('sort_by', 'name')  # Default sort by name
        sort_order = request.args.get('sort_order', 'asc')  # Default order is ascending
        
        image_metadata = []
        for image in images:
            try:
                metadata = get_image_metadata(os.path.join(app.config['UPLOAD_FOLDER'], image))
                image_metadata.append(metadata)
            except Exception as e:
                logger.error(f"Failed to get metadata for {image}: {e}")
                continue

        if sort_by == 'date':
            reverse_order = sort_order == 'desc'
            image_metadata.sort(key=lambda x: x['mod_time'], reverse=reverse_order)
        elif sort_by == 'name':
            reverse_order = sort_order == 'desc'
            image_metadata.sort(key=lambda x: x['name'].lower(), reverse=reverse_order)
        elif sort_by == 'size':
            reverse_order = sort_order == 'desc'
            image_metadata.sort(key=lambda x: x['size'], reverse=reverse_order)

        return render_template('index.html', images=image_metadata, sort_by=sort_by, sort_order=sort_order)
    
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash('An error occurred while loading the gallery.', 'error')
        return render_template('index.html', images=[], sort_by='name', sort_order='asc')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Route for uploading images."""
    try:
        if 'files' not in request.files:
            flash("No file part in request", "error")
            return redirect(url_for('index'))

        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            flash("No files selected", "error")
            return redirect(url_for('index'))

        uploaded_count = 0
        skipped_count = 0
        error_count = 0

        for file in files:
            if file and file.filename != '':
                original_filename = file.filename
                
                if not allowed_file(original_filename):
                    logger.warning(f"File type not allowed: {original_filename}")
                    skipped_count += 1
                    continue
                
                # Secure the filename
                filename = secure_filename(original_filename)
                if not filename:
                    logger.warning(f"Invalid filename after sanitization: {original_filename}")
                    skipped_count += 1
                    continue
                
                try:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    # Check if file already exists and handle duplicates
                    if os.path.exists(file_path):
                        name, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(file_path):
                            filename = f"{name}_{counter}{ext}"
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            counter += 1
                    
                    # Save the file
                    file.save(file_path)
                    logger.info(f"Saved file: {filename}")
                    
                    # Resize the image
                    resize_image(file_path)
                    uploaded_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to upload {original_filename}: {e}")
                    error_count += 1
                    # Clean up partially uploaded file
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass

        # Provide feedback to user
        if uploaded_count > 0:
            flash(f"Successfully uploaded {uploaded_count} file(s)", "success")
        if skipped_count > 0:
            flash(f"Skipped {skipped_count} file(s) (invalid type or name)", "warning")
        if error_count > 0:
            flash(f"Failed to upload {error_count} file(s)", "error")

        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Unexpected error in upload: {e}")
        flash("An unexpected error occurred during upload", "error")
        return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Route for deleting an image."""
    try:
        # Sanitize filename to prevent path traversal
        safe_filename = secure_filename(filename)
        if not safe_filename or safe_filename != filename:
            logger.warning(f"Attempted to delete file with unsafe name: {filename}")
            flash("Invalid filename", "error")
            return redirect(url_for('index'))
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        # Ensure the file path is within the upload folder
        if not file_path.startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
            logger.warning(f"Attempted path traversal with filename: {filename}")
            flash("Invalid file path", "error")
            return redirect(url_for('index'))
        
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {safe_filename}")
            flash(f"File '{safe_filename}' deleted successfully", "success")
        else:
            flash(f"File '{safe_filename}' not found", "error")
            
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {e}")
        flash("An error occurred while deleting the file", "error")
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Route to serve uploaded images."""
    try:
        # Sanitize filename to prevent path traversal
        safe_filename = secure_filename(filename)
        if not safe_filename or safe_filename != filename:
            logger.warning(f"Attempted to access file with unsafe name: {filename}")
            return "Invalid filename", 400
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return "File not found", 404

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Route for updating application settings."""
    error_messages = []
    success_messages = []

    if request.method == 'POST':
        try:
            current_config = app.config['APP_CONFIG']
            config_updated = False
            
            new_folder = request.form.get('upload_folder', '').strip()
            new_extensions = request.form.get('allowed_extensions', '').strip()
            max_height = request.form.get('max_height', '').strip()
            max_width = request.form.get('max_width', '').strip()
            max_file_size = request.form.get('max_file_size_mb', '').strip()

            # Validate Upload Folder
            if new_folder:
                expanded_folder = os.path.expanduser(new_folder)
                try:
                    os.makedirs(expanded_folder, exist_ok=True)
                    if os.access(expanded_folder, os.W_OK):
                        app.config['UPLOAD_FOLDER'] = expanded_folder
                        current_config['upload']['folder'] = new_folder  # Store original path
                        config_updated = True
                        success_messages.append("Upload folder updated successfully")
                    else:
                        error_messages.append("Upload folder is not writable")
                except Exception as e:
                    error_messages.append(f"Error with upload folder: {str(e)}")

            # Validate Allowed Extensions
            if new_extensions:
                try:
                    new_extensions_list = [ext.strip().lower() for ext in new_extensions.split(',') if ext.strip()]
                    if not new_extensions_list:
                        raise ValueError("No valid extensions provided.")
                    
                    app.config['ALLOWED_EXTENSIONS'] = set(new_extensions_list)
                    current_config['upload']['allowed_extensions'] = new_extensions_list
                    config_updated = True
                    success_messages.append("Allowed extensions updated successfully")
                except Exception as e:
                    error_messages.append(f"Error with allowed extensions: {str(e)}")

            # Validate Height and Width
            try:
                if max_height:
                    height_val = int(max_height)
                    if height_val > 0:
                        app.config['MAX_HEIGHT'] = height_val
                        current_config['image_processing']['max_height'] = height_val
                        config_updated = True
                    else:
                        error_messages.append("Height must be a positive integer.")
                        
                if max_width:
                    width_val = int(max_width)
                    if width_val > 0:
                        app.config['MAX_WIDTH'] = width_val
                        current_config['image_processing']['max_width'] = width_val
                        config_updated = True
                    else:
                        error_messages.append("Width must be a positive integer.")
                        
                if max_file_size:
                    size_val = int(max_file_size)
                    if size_val > 0:
                        app.config['MAX_CONTENT_LENGTH'] = size_val * 1024 * 1024
                        current_config['upload']['max_file_size_mb'] = size_val
                        config_updated = True
                    else:
                        error_messages.append("File size must be a positive integer.")
                        
                if (max_height or max_width or max_file_size) and config_updated:
                    success_messages.append("Size limits updated successfully")
                    
            except ValueError:
                error_messages.append("Height, width, and file size must be valid integers.")

            # Save to config file if there were successful updates
            if config_updated and not error_messages:
                if save_config_to_file(current_config):
                    success_messages.append("Settings saved to config/config.json")
                else:
                    error_messages.append("Failed to save settings to configuration file")

            # Flash messages
            for msg in success_messages:
                flash(msg, 'success')
            for msg in error_messages:
                flash(msg, 'error')

            if not error_messages:
                return redirect(url_for('settings'))

        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            flash("An unexpected error occurred while updating settings", "error")

    # Get current settings
    current_folder = app.config['APP_CONFIG']['upload']['folder']
    current_extensions = ', '.join(sorted(app.config['ALLOWED_EXTENSIONS']))
    max_height = app.config['MAX_HEIGHT']
    max_width = app.config['MAX_WIDTH']
    max_file_size_mb = app.config.get('MAX_CONTENT_LENGTH', 10485760) // (1024 * 1024)
    
    return render_template(
        'settings.html',
        current_folder=current_folder,
        current_extensions=current_extensions,
        max_height=max_height,
        max_width=max_width,
        max_file_size_mb=max_file_size_mb,
        error_messages=error_messages
    )

@app.route('/version')
def version():
    """API endpoint to get application version"""
    version_info = {
        'version': app.config.get('APP_VERSION'),
        'timestamp': app.config.get('APP_VERSION') if app.config.get('APP_VERSION') and len(app.config.get('APP_VERSION')) == 14 else None
    }
    
    if version_info['timestamp']:
        # Parse timestamp format YYYYMMDDHHMMSS
        ts = version_info['timestamp']
        try:
            version_info['build_date'] = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}:{ts[12:14]} UTC"
        except:
            version_info['build_date'] = ts
    
    return jsonify(version_info)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    max_size_mb = app.config.get('MAX_CONTENT_LENGTH', 10485760) // (1024 * 1024)
    flash(f"File too large. Maximum size is {max_size_mb}MB", "error")
    return redirect(url_for('index'))

@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    logger.error(f"Server error: {e}")
    flash("An internal server error occurred", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    try:
        host = config['server']['host']
        port = config['server']['port']
        debug = config['server']['debug']
        
        logger.info(f"Starting Photo Uploader server on {host}:{port}")
        logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Config file: config/config.json")
        
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)