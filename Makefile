# Makefile for Stock Analyzer

.PHONY: help setup install run clean test docs load-nse load-nasdaq

help:
	@echo "Stock Analyzer - Available Commands"
	@echo "===================================="
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make install    - Install dependencies only"
	@echo "  make run        - Start the API server"
	@echo "  make clean      - Remove virtual environment and cache"
	@echo "  make docs       - Open API documentation in browser"
	@echo "  make example    - Run example usage script"
	@echo "  make load-nse   - Bulk load NSE stock data (top 30)"
	@echo "  make load-nasdaq- Bulk load NASDAQ stock data (top 30)"
	@echo "  make cache-info - Show database cache information"
	@echo ""

setup:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo ""
	@echo "Setup complete! Activate with: source venv/bin/activate"
	@echo "Then run: make run"

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Dependencies installed!"

run:
	@echo "Starting Stock Analyzer API..."
	python run.py

clean:
	@echo "Cleaning up..."
	rm -rf venv/
	rm -rf data/
	rm -rf __pycache__/
	rm -rf app/__pycache__/
	rm -rf app/**/__pycache__/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	@echo "Cleanup complete!"

docs:
	@echo "Opening API documentation..."
	@sleep 1
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Please open http://localhost:8000/docs in your browser"

example:
	@echo "Running example usage script..."
	python examples/example_usage.py

load-nse:
	@echo "Bulk loading NSE stock data..."
	python load_data.py --exchange NSE --top-n 30

load-nasdaq:
	@echo "Bulk loading NASDAQ stock data..."
	python load_data.py --exchange NASDAQ --top-n 30

cache-info:
	@echo "Retrieving cache information..."
	python load_data.py --info

