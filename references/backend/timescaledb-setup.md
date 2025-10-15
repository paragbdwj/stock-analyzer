# TimescaleDB Setup Guide

This guide explains how to set up and use TimescaleDB as the time series database for Stock Analyzer.

## What is TimescaleDB?

TimescaleDB is an open-source time series database built on PostgreSQL. It's optimized for storing and querying time series data, making it perfect for stock market data.

### Benefits

- **Performance**: Optimized for time series queries
- **Compression**: Automatic data compression for older data
- **SQL Support**: Full PostgreSQL compatibility
- **Scalability**: Handles millions of data points efficiently
- **Reliability**: Built on proven PostgreSQL technology

## Quick Start with Docker (Recommended)

### 1. Start TimescaleDB

```bash
# Start TimescaleDB container
docker-compose up -d

# Check if it's running
docker-compose ps
```

This will start TimescaleDB on `localhost:5432` with:
- Database: `stock_analyzer`
- Username: `postgres`
- Password: `postgres`

### 2. Initialize Database Schema

```bash
# Run database initialization
python init_db.py
```

This creates:
- Database tables (`stock_prices`, `stock_metadata`)
- TimescaleDB hypertable for `stock_prices`
- Indexes for optimal query performance
- Compression policies for old data

### 3. Start the Application

```bash
python run.py
```

The application will automatically connect to TimescaleDB!

## Manual TimescaleDB Installation

If you prefer to install TimescaleDB natively:

### macOS

```bash
# Install TimescaleDB using Homebrew
brew install timescaledb

# Follow post-install instructions to configure PostgreSQL
timescaledb-tune

# Start PostgreSQL
brew services start postgresql
```

### Ubuntu/Debian

```bash
# Add TimescaleDB repository
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"

# Import GPG key
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -

# Install TimescaleDB
sudo apt update
sudo apt install timescaledb-2-postgresql-15

# Configure TimescaleDB
sudo timescaledb-tune

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Create Database

```bash
# Create database
createdb stock_analyzer

# Enable TimescaleDB extension
psql -d stock_analyzer -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

### Update Configuration

Edit `config.json` if your database settings differ:

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "stock_analyzer",
    "user": "postgres",
    "password": "your_password",
    "pool_size": 10,
    "max_overflow": 20
  }
}
```

## Database Schema

### Tables

#### stock_prices (Hypertable)
Stores OHLCV data with automatic time-based partitioning.

```sql
CREATE TABLE stock_prices (
    ticker VARCHAR(20),
    timestamp TIMESTAMP,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT,
    adj_close DOUBLE PRECISION,
    created_at TIMESTAMP,
    PRIMARY KEY (ticker, timestamp)
);

-- Converted to hypertable with 7-day chunks
SELECT create_hypertable('stock_prices', 'timestamp', 
    chunk_time_interval => INTERVAL '7 days');
```

#### stock_metadata
Tracks metadata about cached tickers.

```sql
CREATE TABLE stock_metadata (
    ticker VARCHAR(20) PRIMARY KEY,
    last_updated TIMESTAMP,
    total_records INTEGER,
    first_date TIMESTAMP,
    last_date TIMESTAMP,
    exchange VARCHAR(20),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Features

### 1. Automatic Compression

TimescaleDB automatically compresses data older than 30 days:

```sql
-- Compression is enabled during initialization
ALTER TABLE stock_prices SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'ticker'
);

-- Add compression policy
SELECT add_compression_policy('stock_prices', INTERVAL '30 days');
```

### 2. Optimized Indexes

Indexes are created for fast queries:

```sql
-- Ticker-based queries
CREATE INDEX idx_stock_prices_ticker 
    ON stock_prices (ticker, timestamp DESC);

-- Time range queries
CREATE INDEX idx_stock_prices_ticker_time 
    ON stock_prices (ticker, timestamp);
```

### 3. Query Performance

Example queries:

```sql
-- Get latest price for a ticker
SELECT * FROM stock_prices 
WHERE ticker = 'RELIANCE.NS' 
ORDER BY timestamp DESC 
LIMIT 1;

-- Get price data for date range
SELECT * FROM stock_prices 
WHERE ticker = 'AAPL' 
  AND timestamp >= NOW() - INTERVAL '1 year'
ORDER BY timestamp;

-- Get all tickers with recent data
SELECT ticker, MAX(timestamp) as latest_date
FROM stock_prices
GROUP BY ticker
HAVING MAX(timestamp) >= NOW() - INTERVAL '7 days';
```

## Management Commands

### Database Status

```bash
# Check if TimescaleDB is running
docker-compose ps

# View logs
docker-compose logs -f timescaledb

# Check database connection
python init_db.py
```

### Backup and Restore

```bash
# Backup database
docker exec stock_analyzer_timescaledb pg_dump -U postgres stock_analyzer > backup.sql

# Restore database
docker exec -i stock_analyzer_timescaledb psql -U postgres stock_analyzer < backup.sql
```

### Cleanup

```bash
# Stop TimescaleDB
docker-compose down

# Stop and remove data (WARNING: deletes all data!)
docker-compose down -v
```

## Using the API

### Cache Operations

The API provides endpoints for cache management:

```bash
# Get cache information
curl http://localhost:8000/cache/info

# Clear all cache
curl -X DELETE http://localhost:8000/cache/clear

# Clear specific ticker
curl -X DELETE http://localhost:8000/cache/clear?ticker=RELIANCE.NS
```

### Example Response

```json
{
  "storage_type": "TimescaleDB",
  "total_tickers": 30,
  "total_records": 7500,
  "tickers": ["RELIANCE.NS", "TCS.NS", ...],
  "date_range": {
    "earliest": "2023-01-01T00:00:00",
    "latest": "2024-01-15T00:00:00"
  },
  "database_size": {
    "prices_table": "2048 kB",
    "metadata_table": "16 kB"
  }
}
```

## Performance Tuning

### Connection Pool

Adjust pool settings in `config.json`:

```json
{
  "database": {
    "pool_size": 10,        // Number of connections to maintain
    "max_overflow": 20      // Additional connections when needed
  }
}
```

### Compression Settings

Modify compression interval if needed:

```sql
-- Change compression threshold
SELECT remove_compression_policy('stock_prices');
SELECT add_compression_policy('stock_prices', INTERVAL '60 days');
```

### Data Retention

Set up automatic data retention:

```sql
-- Keep only 2 years of data
SELECT add_retention_policy('stock_prices', INTERVAL '2 years');
```

## Monitoring

### Database Size

```sql
-- Check table sizes
SELECT 
    hypertable_name,
    pg_size_pretty(hypertable_size(format('%I.%I', hypertable_schema, hypertable_name)::regclass))
FROM timescaledb_information.hypertables;

-- Check compressed data ratio
SELECT 
    pg_size_pretty(before_compression_total_bytes) as uncompressed,
    pg_size_pretty(after_compression_total_bytes) as compressed,
    round((1 - after_compression_total_bytes::numeric / before_compression_total_bytes::numeric) * 100, 2) as compression_ratio
FROM timescaledb_information.compression_settings;
```

### Query Performance

```sql
-- Enable query timing
\timing on

-- Analyze query plan
EXPLAIN ANALYZE 
SELECT * FROM stock_prices 
WHERE ticker = 'AAPL' 
  AND timestamp >= NOW() - INTERVAL '1 year';
```

## Troubleshooting

### Connection Issues

**Problem**: Can't connect to database

**Solutions**:
```bash
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs timescaledb

# Restart container
docker-compose restart timescaledb

# Check port is not in use
lsof -i :5432
```

### Extension Not Found

**Problem**: "extension timescaledb does not exist"

**Solution**:
```bash
# Connect to database
docker exec -it stock_analyzer_timescaledb psql -U postgres -d stock_analyzer

# Create extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

# Verify
\dx
```

### Slow Queries

**Problem**: Queries are slow

**Solutions**:
1. Check indexes: `\d stock_prices`
2. Analyze table: `ANALYZE stock_prices;`
3. Check compression: `SELECT * FROM timescaledb_information.compression_settings;`
4. Increase connection pool in config.json

### Out of Memory

**Problem**: Database runs out of memory

**Solutions**:
1. Reduce `pool_size` in config.json
2. Enable compression for older data
3. Add retention policy to remove old data
4. Increase Docker memory limit

## Production Deployment

### Security

1. **Change default password**:
```yaml
# docker-compose.yml
environment:
  POSTGRES_PASSWORD: ${DB_PASSWORD}  # Use environment variable
```

2. **Enable SSL**:
```yaml
volumes:
  - ./certs:/var/lib/postgresql/certs
environment:
  POSTGRES_SSL_CERT: /var/lib/postgresql/certs/server.crt
  POSTGRES_SSL_KEY: /var/lib/postgresql/certs/server.key
```

3. **Restrict network access**:
```yaml
ports:
  - "127.0.0.1:5432:5432"  # Only localhost
```

### Backup Strategy

1. **Automated backups**:
```bash
# Add to crontab
0 2 * * * docker exec stock_analyzer_timescaledb pg_dump -U postgres stock_analyzer > /backups/stock_analyzer_$(date +\%Y\%m\%d).sql
```

2. **Continuous archiving** (WAL):
Configure in PostgreSQL for point-in-time recovery

### Monitoring

Use tools like:
- pgAdmin
- Grafana + Prometheus
- TimescaleDB Cloud monitoring

## Advantages over File-based Storage

| Feature | File Storage | TimescaleDB |
|---------|-------------|-------------|
| Query Speed | Slow (full scan) | Fast (indexed) |
| Concurrent Access | Limited | Excellent |
| Data Integrity | Manual | ACID transactions |
| Compression | Manual | Automatic |
| Scalability | Poor | Excellent |
| Backup/Restore | File copy | Proper DB tools |
| Query Flexibility | Limited | Full SQL |

## Migration from File Storage

If you have existing file-based cache:

```python
# migration script (create your own)
import pandas as pd
from pathlib import Path
from app.utils.storage import StorageManager

storage = StorageManager()

# Migrate parquet files
data_path = Path("data/stocks")
for parquet_file in data_path.glob("*.parquet"):
    ticker = parquet_file.stem
    df = pd.read_parquet(parquet_file)
    storage.save_stock_data(ticker, df)
    print(f"Migrated {ticker}")
```

---

For more information:
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- Project README: [README.md](README.md)

