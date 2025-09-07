#!/bin/bash
# Setup script for MangaDex Cover Downloader
#
# This script creates a virtual environment, installs dependencies,
# and runs a test to verify the MangaDex API is working.

set -e

echo "Setting up MangaDex Cover Downloader..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Test the API
echo "Testing MangaDex API..."
python test_mangadex_api.py

echo ""
echo "Setup complete!"
echo ""
echo "To use the cover downloader:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the downloader: python mangadex_cover_downloader.py"
echo ""
echo "For help: python mangadex_cover_downloader.py --help"
