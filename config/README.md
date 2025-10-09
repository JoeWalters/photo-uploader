# Configuration Directory

This directory contains configuration files for the Photo Uploader application.

## config.json

Main configuration file for the application. Edit this file to customize settings.

### Configuration Options:

#### Server Settings
- `host`: IP address to bind the server to (default: "0.0.0.0" for all interfaces)
- `port`: Port number for the web server (default: 5001)
- `debug`: Enable debug mode for development (default: false)

#### Upload Settings
- `folder`: Directory where uploaded images will be stored (default: "~/photo_uploads")
  - Use `~` for home directory
  - Use absolute paths like `/home/user/photos` or relative paths like `./uploads`
- `max_file_size_mb`: Maximum file size in megabytes (default: 10)
- `allowed_extensions`: List of allowed file extensions (default: common image formats)

#### Image Processing Settings
- `max_width`: Maximum width in pixels - larger images will be resized (default: 1920)
- `max_height`: Maximum height in pixels - larger images will be resized (default: 1080)
- `auto_rotate`: Automatically rotate images based on EXIF data (default: true)
- `optimize`: Optimize images when saving (default: true)
- `quality`: JPEG quality when saving (1-100, default: 85)

### Example Configurations:

#### For a local development setup:
```json
{
    "server": {
        "host": "127.0.0.1",
        "port": 8080,
        "debug": true
    },
    "upload": {
        "folder": "./dev_uploads",
        "max_file_size_mb": 5
    }
}
```

#### For a home media server:
```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 80,
        "debug": false
    },
    "upload": {
        "folder": "/media/photos",
        "max_file_size_mb": 50,
        "allowed_extensions": ["jpg", "jpeg", "png", "raw", "cr2", "nef"]
    },
    "image_processing": {
        "max_width": 4000,
        "max_height": 3000,
        "quality": 95
    }
}
```

## Notes:
- Restart the application after changing configuration files
- Invalid JSON will cause the application to use default settings
- Comments (lines starting with "_") are ignored by the application
- The web interface settings page can also modify some of these settings