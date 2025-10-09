#!/bin/bash

# Default values
PUID=${PUID:-1000}
PGID=${PGID:-1000}

# Create group if it doesn't exist
if ! getent group photoapp > /dev/null 2>&1; then
    groupadd -g $PGID photoapp
fi

# Create user if it doesn't exist
if ! getent passwd photoapp > /dev/null 2>&1; then
    useradd -u $PUID -g $PGID -d /app -s /bin/bash photoapp
fi

# Set ownership of app directories
chown -R $PUID:$PGID /app

# If volumes are mounted, try to set permissions
if [ -d "/app/config" ]; then
    chown -R $PUID:$PGID /app/config 2>/dev/null || true
fi

if [ -d "/app/uploads" ]; then
    chown -R $PUID:$PGID /app/uploads 2>/dev/null || true
fi

if [ -d "/app/logs" ]; then
    chown -R $PUID:$PGID /app/logs 2>/dev/null || true
fi

echo "Starting Photo Uploader as UID:$PUID GID:$PGID"

# Execute the command as the photoapp user
exec gosu photoapp "$@"