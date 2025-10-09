# Docker Deployment Guide

This guide covers deploying the Photo Uploader using Docker, including setup for Unraid.

## Quick Start with Docker

### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JoeWalters/photo-uploader.git
   cd photo-uploader
   ```

2. **Start the application:**
   ```bash
   docker-compose up -d
   ```

3. **Access the web interface:**
   Open http://localhost:5001 in your browser

### Using Docker Run

```bash
docker run -d \
  --name photo-uploader \
  -p 5001:5001 \
  -v ./config:/app/config \
  -v ./uploads:/app/uploads \
  -e TZ=America/New_York \
  --restart unless-stopped \
  joewalters/photo-uploader:latest
```

## Unraid Installation

### Method 1: Community Applications (Recommended)
1. Install the **Community Applications** plugin if not already installed
2. Search for "Photo Uploader" in Community Applications
3. Click Install and configure the paths as needed

### Method 2: Manual Template Installation
1. In Unraid, go to **Docker** tab
2. Click **Add Container**
3. Set **Template repositories** to: `https://github.com/JoeWalters/photo-uploader`
4. Select the Photo Uploader template
5. Configure paths and settings as needed

### Method 3: Manual Docker Installation
1. In Unraid, go to **Docker** tab
2. Click **Add Container**
3. Fill in the following settings:

   | Setting | Value |
   |---------|-------|
   | Name | photo-uploader |
   | Repository | joewalters/photo-uploader:latest |
   | Network Type | Bridge |
   | Port | 5001:5001 (TCP) |
   | Config Path | /mnt/user/appdata/photo-uploader/config:/app/config |
   | Upload Path | /mnt/user/photos/uploads:/app/uploads |

## Volume Mounts

### Required Volumes
- **Config Directory** (`/app/config`): Contains configuration files
  - `config.json` - Main configuration file
  - Automatically created on first run
  - Edit this file to customize settings
  
- **Upload Directory** (`/app/uploads`): Where uploaded photos are stored
  - This is where your photos will be saved
  - Make sure it has sufficient storage space

### Optional Volumes
- **Logs Directory** (`/app/logs`): Application logs (if you want to persist logs)

## Configuration

### Environment Variables
You can override configuration using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TZ` | Timezone | `UTC` |
| `UPLOAD_FOLDER` | Override upload folder path | `/app/uploads` |
| `PORT` | Override server port | `5001` |
| `HOST` | Override server host | `0.0.0.0` |
| `MAX_FILE_SIZE` | Max file size in MB | `10` |

### Config File Method (Recommended)
Edit the `config/config.json` file in your mounted config directory:

```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 5001,
        "debug": false
    },
    "upload": {
        "folder": "/app/uploads",
        "max_file_size_mb": 10,
        "allowed_extensions": ["png", "jpg", "jpeg", "gif", "webp"]
    },
    "image_processing": {
        "max_width": 1920,
        "max_height": 1080,
        "auto_rotate": true,
        "optimize": true,
        "quality": 85
    }
}
```

## Unraid Specific Setup

### Recommended Paths
- **Config**: `/mnt/user/appdata/photo-uploader/config`
- **Uploads**: `/mnt/user/photos/uploads` (or your preferred photo storage location)

### User/Group IDs
For proper file permissions in Unraid:
- **PUID**: `99` (nobody user)
- **PGID**: `100` (users group)

### Network Settings
- **Network Type**: Bridge
- **Port**: 5001 (or your preferred port)

## Updates

### Docker Compose
```bash
docker-compose pull
docker-compose up -d
```

### Docker Run
```bash
docker pull joewalters/photo-uploader:latest
docker stop photo-uploader
docker rm photo-uploader
# Run your docker run command again
```

### Unraid
1. Go to Docker tab
2. Click the photo-uploader container
3. Click "Check for Updates"
4. If an update is available, click "Update"

## Troubleshooting

### Container Won't Start
1. Check logs: `docker logs photo-uploader`
2. Verify mounted directories exist and are writable
3. Check port conflicts

### Can't Access Web Interface
1. Verify port mapping is correct
2. Check firewall settings
3. Ensure container is running: `docker ps`

### Permission Issues
1. Check file permissions on mounted directories
2. In Unraid, ensure PUID/PGID are set correctly
3. Verify the upload directory is writable

### Configuration Issues
1. Check `config/config.json` syntax (must be valid JSON)
2. Verify file paths in configuration
3. Check logs for configuration errors

## Docker Image Tags

- `latest` - Latest stable release
- `YYYYMMDDHHMMSS` - Timestamp-based tags for specific builds (e.g., `20251009151500`)
- `v1.0.0` - Semantic version tags (if using releases)

## Version Information

The application displays its build version in the web interface:

- **Footer**: Shows version number (e.g., "v20251009151500")
- **Settings Page**: Shows detailed build information including formatted date/time
- **API Endpoint**: Access version info at `/version` endpoint

### Version Format
The timestamp format `YYYYMMDDHHMMSS` represents:
- `YYYY` - Year (2025)
- `MM` - Month (01-12)  
- `DD` - Day (01-31)
- `HH` - Hour (00-23)
- `MM` - Minute (00-59)
- `SS` - Second (00-59)

Example: `20251009151500` = October 9, 2025 at 15:15:00 UTC

## Security Considerations

- The container runs as a non-root user for security
- Only expose necessary ports
- Consider using a reverse proxy (Traefik, nginx) for HTTPS
- Regularly update the container image
- Limit upload directory size if needed

## Support

- **GitHub Issues**: https://github.com/JoeWalters/photo-uploader/issues
- **Docker Hub**: https://hub.docker.com/r/joewalters/photo-uploader
- **Documentation**: See repository README.md