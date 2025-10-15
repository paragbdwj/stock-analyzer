#!/usr/bin/env python3
"""
Example usage of the Stock Analyzer API.

Make sure the API server is running before executing this script:
    python run.py
"""
import requests
import json
from typing import Dict, Any


# API base URL
BASE_URL = "http://localhost:8000"


def print_json(data: Dict[Any, Any]) -> None:
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2, default=str))


def example_1_health_check():
    """Example 1: Check API health."""
    print("\n" + "=" * 60)
    print("Example 1: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print_json(response.json())


def example_2_list_exchanges():
    """Example 2: List available exchanges."""
    print("\n" + "=" * 60)
    print("Example 2: List Available Exchanges")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/exchanges")
    print(f"Status Code: {response.status_code}")
    print_json(response.json())


def example_3_get_tickers():
    """Example 3: Get tickers for an exchange."""
    print("\n" + "=" * 60)
    print("Example 3: Get NSE Tickers (Top 10)")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/tickers/NSE?top_n=10")
    print(f"Status Code: {response.status_code}")
    tickers = response.json()
    print(f"Found {len(tickers)} tickers:")
    for ticker in tickers:
        print(f"  - {ticker}")


def example_4_analyze_stock():
    """Example 4: Analyze a single stock."""
    print("\n" + "=" * 60)
    print("Example 4: Analyze RELIANCE.NS")
    print("=" * 60)
    
    ticker = "RELIANCE.NS"
    response = requests.get(f"{BASE_URL}/analyze/{ticker}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTicker: {data['ticker']}")
        print(f"Current Price: ₹{data['current_price']:.2f}")
        
        if data['technical']:
            print("\nTechnical Indicators:")
            tech = data['technical']
            print(f"  RSI: {tech.get('rsi', 'N/A')}")
            print(f"  SMA 50: {tech.get('sma_50', 'N/A')}")
            print(f"  SMA 200: {tech.get('sma_200', 'N/A')}")
            print(f"  MACD: {tech.get('macd', 'N/A')}")
        
        if data['fundamental']:
            print("\nFundamental Data:")
            fund = data['fundamental']
            print(f"  P/E Ratio: {fund.get('trailing_pe', 'N/A')}")
            print(f"  Price to Book: {fund.get('price_to_book', 'N/A')}")
            print(f"  Debt to Equity: {fund.get('debt_to_equity', 'N/A')}")
            print(f"  Market Cap: ₹{fund.get('market_cap', 'N/A'):,.0f}" if fund.get('market_cap') else "  Market Cap: N/A")
            print(f"  Sector: {fund.get('sector', 'N/A')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def example_5_scan_oversold_stocks():
    """Example 5: Scan for oversold stocks with good fundamentals."""
    print("\n" + "=" * 60)
    print("Example 5: Scan for Oversold Stocks (RSI < 30, P/E < 20)")
    print("=" * 60)
    
    scan_request = {
        "exchange": "NSE",
        "technical_filters": [
            {"field": "rsi", "operator": "<", "value": 30}
        ],
        "fundamental_filters": [
            {"field": "trailing_pe", "operator": "<", "value": 20},
            {"field": "trailing_pe", "operator": ">", "value": 0}  # Exclude negative P/E
        ],
        "filter_logic": "AND",
        "force_refresh": False
    }
    
    print("\nScan Request:")
    print_json(scan_request)
    
    print("\nScanning... (this may take a minute)")
    response = requests.post(f"{BASE_URL}/scan", json=scan_request)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Scan Complete!")
        print(f"  Total Scanned: {result['total_scanned']}")
        print(f"  Total Matched: {result['total_matched']}")
        print(f"  Duration: {result['scan_duration_seconds']}s")
        
        if result['stocks']:
            print(f"\nMatched Stocks:")
            for stock in result['stocks'][:5]:  # Show first 5
                print(f"\n  {stock['ticker']}:")
                print(f"    Price: ₹{stock['current_price']:.2f}")
                if stock['technical']:
                    print(f"    RSI: {stock['technical'].get('rsi', 'N/A')}")
                if stock['fundamental']:
                    print(f"    P/E: {stock['fundamental'].get('trailing_pe', 'N/A')}")
                print(f"    Matched: {', '.join(stock['matched_filters'])}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def example_6_scan_golden_cross():
    """Example 6: Scan for potential Golden Cross stocks."""
    print("\n" + "=" * 60)
    print("Example 6: Scan for Golden Cross Candidates (SMA50 approaching SMA200)")
    print("=" * 60)
    
    scan_request = {
        "exchange": "NASDAQ",
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],  # Limit to specific tickers
        "technical_filters": [
            {"field": "rsi", "operator": ">", "value": 45},
            {"field": "rsi", "operator": "<", "value": 65}
        ],
        "filter_logic": "AND"
    }
    
    print("\nScan Request:")
    print_json(scan_request)
    
    print("\nScanning...")
    response = requests.post(f"{BASE_URL}/scan", json=scan_request)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Scan Complete!")
        print(f"  Total Scanned: {result['total_scanned']}")
        print(f"  Total Matched: {result['total_matched']}")
        
        if result['stocks']:
            print(f"\nMatched Stocks:")
            for stock in result['stocks']:
                print(f"\n  {stock['ticker']}:")
                print(f"    Price: ${stock['current_price']:.2f}")
                if stock['technical']:
                    print(f"    SMA 50: ${stock['technical'].get('sma_50', 'N/A')}")
                    print(f"    SMA 200: ${stock['technical'].get('sma_200', 'N/A')}")
                    print(f"    RSI: {stock['technical'].get('rsi', 'N/A')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def example_7_get_current_price():
    """Example 7: Get current price for stocks."""
    print("\n" + "=" * 60)
    print("Example 7: Get Current Prices")
    print("=" * 60)
    
    tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    
    for ticker in tickers:
        response = requests.get(f"{BASE_URL}/price/{ticker}")
        if response.status_code == 200:
            data = response.json()
            print(f"  {data['ticker']}: ₹{data['price']:.2f}")
        else:
            print(f"  {ticker}: Error fetching price")


def example_8_cache_management():
    """Example 8: Manage cache."""
    print("\n" + "=" * 60)
    print("Example 8: Cache Management")
    print("=" * 60)
    
    # Get cache info
    print("\nCache Information:")
    response = requests.get(f"{BASE_URL}/cache/info")
    if response.status_code == 200:
        cache_info = response.json()
        print(f"  Total Tickers Cached: {cache_info['total_tickers']}")
        print(f"  Total Size: {cache_info['total_size_mb']:.2f} MB")
        print(f"  Storage Type: {cache_info['storage_type']}")
        print(f"  Storage Path: {cache_info['storage_path']}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Stock Analyzer API - Example Usage")
    print("=" * 60)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("Start it with: python run.py")
    
    input("\nPress Enter to continue...")
    
    try:
        # Run examples
        example_1_health_check()
        example_2_list_exchanges()
        example_3_get_tickers()
        example_4_analyze_stock()
        example_5_scan_oversold_stocks()
        # example_6_scan_golden_cross()  # Uncomment to run NASDAQ scan
        example_7_get_current_price()
        example_8_cache_management()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        print("\nFor more information, visit: http://localhost:8000/docs")
        print("")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print("Please make sure the server is running:")
        print("  python run.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

