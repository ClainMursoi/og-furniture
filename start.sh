#!/bin/bash
echo "=== Starting The OG Furniture ==="

# Run database migration
echo "Running database migration..."
flask db upgrade

# Start the app
echo "Starting the Flask app..."
python run.py