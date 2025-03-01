#!/bin/bash

# Interactive script for uploading packages to PyPI or TestPyPI

echo "Welcome to the PyPI upload script!"

# Clean old builds
echo "Cleaning up old builds..."
rm -rf ./build ./dist ./*.egg-info

# Build the package
echo "Building the package..."
python3 -m build --no-isolation

# Check metadata
echo "Checking package metadata with Twine..."
twine check dist/*

# Prompt for upload target
echo "Do you want to upload to (1) PyPI or (2) TestPyPI? (Enter 1 or 2):"
read choice
if [[ "$choice" -eq 1 ]]; then
    echo "Uploading to PyPI..."
    python3 -m twine upload dist/*
elif [[ "$choice" -eq 2 ]]; then
    echo "Uploading to TestPyPI..."
    python3 -m twine upload --repository testpypi dist/*
else
    echo "Invalid choice. Exiting..."
    exit 1
fi

echo "Upload completed."
