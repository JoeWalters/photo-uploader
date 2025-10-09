#!/usr/bin/env python3
"""
Demo script showing command line usage of Photo Uploader
"""

import subprocess
import sys
import os

def demo_help():
    """Show help for the photo uploader"""
    print("=== Photo Uploader Command Line Help ===")
    result = subprocess.run([sys.executable, "photo_uploader.py", "--help"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

def demo_config():
    """Show current configuration"""
    print("\n=== Current Configuration ===")
    
    # Show the config file content
    config_file = "config/config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config_content = f.read()
        print(config_content)
    else:
        print("Config file not found. Run the application once to create it.")
        
    print(f"\n=== Config File Location ===")
    print(f"Configuration file: {os.path.abspath(config_file)}")
    print("Edit this file to change default settings!")

if __name__ == "__main__":
    print("Photo Uploader Configuration Demo")
    print("=" * 40)
    
    demo_help()
    demo_config()
    
    print("\n=== Example Usage ===")
    print("Start server with custom settings:")
    print("  python3 photo_uploader.py --upload-folder ~/my_photos --port 8080")
    print("\nStart in debug mode:")
    print("  python3 photo_uploader.py --debug")
    print("\nSet maximum file size:")
    print("  python3 photo_uploader.py --max-file-size 50")