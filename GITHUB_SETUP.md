# GitHub Actions Setup Instructions

To enable automatic Docker image building and pushing to Docker Hub, you need to configure GitHub secrets:

## Required GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following repository secrets:

### Docker Hub Credentials
- **`DOCKERHUB_USERNAME`**: Your Docker Hub username
- **`DOCKERHUB_TOKEN`**: Docker Hub access token (not your password!)

### How to create a Docker Hub access token:
1. Log in to [Docker Hub](https://hub.docker.com)
2. Go to **Account Settings** → **Security**
3. Click **New Access Token**
4. Give it a name (e.g., "GitHub Actions")
5. Copy the generated token and add it as `DOCKERHUB_TOKEN` secret

## What the GitHub Action Does

When you push to the `main` branch, the action will:

1. **Build** a multi-architecture Docker image (AMD64 and ARM64)
2. **Tag** the image with:
   - `latest` (for the main branch)
   - `YYYYMMDDHHMMSS` timestamp (e.g., `20251009151500`)
   - Version tags (if you create GitHub releases)
3. **Push** to Docker Hub as `joewalters/photo-uploader`
4. **Test** the image to ensure it starts correctly
5. **Cache** build layers for faster subsequent builds

## Image Tags Available

After the first successful build, you'll have:
- `joewalters/photo-uploader:latest`
- `joewalters/photo-uploader:20251009151500` (timestamp example)

## Triggering a Build

The action triggers on:
- **Push to main branch** (builds and pushes)
- **Pull requests** (builds only, doesn't push)
- **Releases** (builds with version tags)

## Monitoring Builds

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Watch the build progress in real-time
4. Check the Docker Hub repository for new images

## Local Testing

Before pushing, you can test the Docker image locally:

```bash
# Build the image
docker build -t photo-uploader-test .

# Test run
docker run -d --name test-uploader -p 5001:5001 photo-uploader-test

# Check if it's working
curl http://localhost:5001

# Clean up
docker stop test-uploader && docker rm test-uploader
```

## Troubleshooting

### Build Fails
- Check the Actions tab for error logs
- Verify Dockerfile syntax
- Ensure all required files are present

### Push Fails
- Verify Docker Hub credentials in GitHub secrets
- Check that the Docker Hub repository exists
- Ensure the access token has write permissions

### Image Won't Start
- Check Docker logs: `docker logs container-name`
- Verify config file syntax
- Check file permissions on mounted volumes