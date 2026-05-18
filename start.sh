#!/bin/bash
echo "=== The OG Furniture - Starting ==="

# Run database migration
echo "Running database migration..."
python -m flask db upgrade

# Start the app
echo "Starting the application..."
python run.py