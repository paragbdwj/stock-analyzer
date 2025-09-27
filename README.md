# Stock Analyzer

A software application for stock market related activities. This project uses Python with the FastAPI framework, Docker for containerization, and a shell script for easy deployment.

## Requirements

* A script using `yfinance` API which takes a stock symbol and stores the daily stock details (all the details that are available along with OHLCV) inside a time-series database (InfluxDB).
* A FastAPI application to expose the collected data.
* The application is dockerized for easy deployment.
* A `.sh` deployment script is provided.

## Project Structure
stock-analyzer/
|-- app/
|   |-- init.py
|   |-- main.py
|   |-- stock_data.py
|-- scripts/
|   |-- fetch_data.py
|-- .dockerignore
|-- docker-compose.yml
|-- Dockerfile
|-- deploy.sh
|-- README.md
|-- requirements.txt


## Setup and Deployment

### Prerequisites

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Instructions

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd stock-analyzer
    ```

2.  **Make the deployment script executable:**

    ```bash
    chmod +x deploy.sh
    ```

3.  **Run the deployment script:**

    ```bash
    ./deploy.sh
    ```

This script will build and start the FastAPI application and the InfluxDB database using `docker-compose`.

## How to Use

### 1. Fetch Stock Data

To fetch and store stock data, you can run the `fetch_data.py` script.

**Example:**

```bash
docker-compose run --rm app python scripts/fetch_data.