import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

def get_influxdb_client():
    return InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

def store_stock_data(symbol, data):
    client = get_influxdb_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for index, row in data.iterrows():
        point = {
            "measurement": "stock_prices",
            "tags": {"symbol": symbol},
            "fields": {
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"]
            },
            "time": index
        }
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Successfully stored data for {symbol}")

def get_stock_data_from_db(symbol):
    client = get_influxdb_client()
    query_api = client.query_api()

    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "stock_prices")
    |> filter(fn: (r) => r.symbol == "{symbol.upper()}")
    '''

    result = query_api.query(org=INFLUXDB_ORG, query=query)
    
    results = []
    for table in result:
        for record in table.records:
            results.append(record.values)
            
    return results