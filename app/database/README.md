# Database Module

This module handles all TimescaleDB database operations for the Stock Analyzer.

## Files

### `connection.py`
Database connection and session management.

**Key Functions:**
- `get_engine()` - Get SQLAlchemy engine
- `get_session()` - Context manager for database sessions
- `init_db()` - Initialize database schema and hypertables
- `check_connection()` - Verify database connectivity
- `close_connection()` - Cleanup database connections

**Usage:**
```python
from app.database.connection import get_session

# Use context manager for automatic commit/rollback
with get_session() as session:
    result = session.query(StockPrice).all()
```

### `models.py`
SQLAlchemy ORM models for database tables.

**Models:**

#### StockPrice
Time series data for stock prices (hypertable).
```python
class StockPrice:
    ticker: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float
    created_at: datetime
```

#### StockMetadata
Metadata about cached tickers.
```python
class StockMetadata:
    ticker: str
    last_updated: datetime
    total_records: int
    first_date: datetime
    last_date: datetime
    exchange: str
    is_active: bool
```

## Database Schema

### Hypertable
`stock_prices` is converted to a TimescaleDB hypertable with:
- Time-based partitioning (7-day chunks)
- Automatic compression (30+ days old)
- Optimized indexes for fast queries

### Indexes
- `idx_stock_prices_ticker` - Ticker-based lookups
- `idx_stock_prices_ticker_time` - Time range queries

## Initialization

Run once to set up the database:
```bash
python init_db.py
```

This creates:
1. TimescaleDB extension (if not exists)
2. Database tables
3. Hypertable conversion
4. Performance indexes
5. Compression policies

## Configuration

Database settings in `config.json`:
```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "stock_analyzer",
    "user": "postgres",
    "password": "postgres",
    "pool_size": 10,
    "max_overflow": 20
  }
}
```

## Usage Examples

### Save Data
```python
from app.database import get_session, StockPrice
from datetime import datetime

with get_session() as session:
    price = StockPrice(
        ticker="AAPL",
        timestamp=datetime.now(),
        open=150.0,
        high=152.0,
        low=149.0,
        close=151.0,
        volume=1000000
    )
    session.add(price)
    # Auto-committed on context exit
```

### Query Data
```python
from app.database import get_session, StockPrice
from sqlalchemy import and_
from datetime import datetime, timedelta

with get_session() as session:
    # Get latest price
    latest = session.query(StockPrice)\
        .filter(StockPrice.ticker == "AAPL")\
        .order_by(StockPrice.timestamp.desc())\
        .first()
    
    # Get date range
    one_year_ago = datetime.now() - timedelta(days=365)
    prices = session.query(StockPrice)\
        .filter(and_(
            StockPrice.ticker == "AAPL",
            StockPrice.timestamp >= one_year_ago
        ))\
        .order_by(StockPrice.timestamp)\
        .all()
```

### Bulk Operations
```python
from app.database import get_session, StockPrice

with get_session() as session:
    # Bulk insert
    prices = [
        StockPrice(ticker="AAPL", timestamp=ts, open=o, ...)
        for ts, o in data
    ]
    session.bulk_save_objects(prices)
    
    # Bulk delete
    session.query(StockPrice)\
        .filter(StockPrice.ticker == "AAPL")\
        .delete()
```

## Best Practices

1. **Always use context manager** (`with get_session()`)
   - Automatic commit on success
   - Automatic rollback on error
   - Proper connection cleanup

2. **Use bulk operations** for large datasets
   ```python
   session.bulk_save_objects(objects)  # Faster than individual inserts
   ```

3. **Add indexes** for common queries
   ```sql
   CREATE INDEX idx_name ON table (columns);
   ```

4. **Monitor performance**
   ```python
   # Enable query logging
   engine = get_engine()
   engine.echo = True
   ```

## TimescaleDB Features

### Automatic Compression
Data older than 30 days is automatically compressed:
```sql
-- Already configured during init_db()
SELECT * FROM timescaledb_information.compression_settings;
```

### Data Retention
Set up automatic data cleanup:
```sql
-- Keep only 2 years of data
SELECT add_retention_policy('stock_prices', INTERVAL '2 years');
```

### Continuous Aggregates
Pre-compute common aggregations:
```sql
-- Example: Daily averages
CREATE MATERIALIZED VIEW stock_daily_avg
WITH (timescaledb.continuous) AS
SELECT
    ticker,
    time_bucket('1 day', timestamp) AS day,
    AVG(close) as avg_close
FROM stock_prices
GROUP BY ticker, day;
```

## Troubleshooting

### Connection Issues
```python
from app.database.connection import check_connection

if not check_connection():
    print("Database connection failed!")
    # Check if TimescaleDB is running
    # docker-compose ps
```

### Query Performance
```python
# Enable query timing
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    print(f"Query took: {total:.4f}s")
```

## References

- [TimescaleDB Documentation](https://docs.timescale.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Setup Guide](../../TIMESCALEDB_SETUP.md)

