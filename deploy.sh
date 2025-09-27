#!/bin/bash

# Build and start the containers in detached mode
docker-compose up -d --build

echo "Application is deployed and running."
echo "API is available at http://localhost:8000"
echo "InfluxDB is available at http://localhost:8086"