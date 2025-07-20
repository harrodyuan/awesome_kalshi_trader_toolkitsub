#!/usr/bin/env python3
"""
Search for markets within a specific event ticker
Usage: python search_markets_in_event.py "EVENT_TICKER"
"""

import os
import sys
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from clients import KalshiHttpClient, Environment

load_dotenv()

def format_money(value):
    """Format cents to dollars"""
    try:
        return f"${float(value)/100:.2f}"
    except:
        return "$0.00"

def search_markets_in_event(event_ticker):
    """Find all markets for a given event ticker"""
    # Setup client
    try:
        with open(os.getenv('PROD_KEYFILE'), "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        
        client = KalshiHttpClient(
            key_id=os.getenv('PROD_KEYID'),
            private_key=private_key,
            environment=Environment.PROD
        )
    except Exception as e:
        print(f"Setup error: {e}")
        return
    
    print(f"Searching for markets in event '{event_ticker}'...")
    
    try:
        response = client.get(f"/trade-api/v2/markets?event_ticker={event_ticker}&status=open")
        markets = response.get('markets', [])
        
        if not markets:
            print(f"No open markets found for event '{event_ticker}'")
            # Lets try to see if the event exists at all
            try:
                event_response = client.get(f"/trade-api/v2/events/{event_ticker}")
                if event_response.get('event'):
                    print("   Event exists, but has no open markets right now.")
            except:
                print(f"   Could not find an event with ticker '{event_ticker}'. Check for typos.")
            return

        print(f"\nFound {len(markets)} markets for event '{event_ticker}':")
        
        for i, market in enumerate(markets, 1):
            print("-" * 50)
            print(f"{i}. Market Ticker: {market.get('ticker')}")
            print(f"   Title: {market.get('title')}")
            print(f"   YES Bid/Ask: {format_money(market.get('yes_bid'))} / {format_money(market.get('yes_ask'))}")
            print(f"   Volume: {market.get('volume')}")

        print("\n--------------------------------------------------")
        print("Next Step:")
        print("1. Copy a Market Ticker.")
        print("2. Use one of the following scripts to place an order:")
        print(f"   - python simple_order.py {markets[0].get('ticker')} yes buy 1 10")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"API error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python search_markets_in_event.py \"EVENT_TICKER\"")
        print("Example: python search_markets_in_event.py \"CPI-24DEC\"")
        sys.exit(1)
    
    search_markets_in_event(sys.argv[1])
