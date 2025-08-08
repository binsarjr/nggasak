# Docker Configuration

This directory contains Docker configuration files and scripts.

## Files

- **entrypoint.sh** - Container startup script
  - Shows available tools
  - Checks API key configuration
  - Provides usage examples
  - Customizable via volume mount

## Customization

You can modify `entrypoint.sh` to:
- Add new tools to the welcome message
- Change startup behavior
- Add custom environment setup
- Modify tool version checks

Changes to `entrypoint.sh` are immediately reflected in containers due to volume mounting.

## Volume Mounting

The entire `./docker/` directory is mounted to `/docker/` in the container, allowing:
- Live script updates without rebuilding
- Easy customization of container behavior
- Version control of Docker scripts
