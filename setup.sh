#!/bin/bash

# Setup script for Stock Analyzer

echo "========================================"
echo "Stock Analyzer - Setup Script"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "Virtual environment created successfully!"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Setting up TimescaleDB..."
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Warning: Docker is not installed."
    echo "Please install Docker and run: docker-compose up -d"
    echo "Or follow manual TimescaleDB installation in TIMESCALEDB_SETUP.md"
else
    echo "Starting TimescaleDB container..."
    docker-compose up -d
    
    echo "Waiting for database to be ready..."
    sleep 5
    
    echo "Initializing database schema..."
    python init_db.py
fi

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Make sure TimescaleDB is running: docker-compose ps"
echo "  3. Run the server: python run.py"
echo ""
echo "The API will be available at:"
echo "  - http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo ""
echo "Optional: Create .env file and add FMP_API_KEY for enhanced fundamental data"
echo ""
echo "Database: TimescaleDB is running on localhost:5432"
echo ""

