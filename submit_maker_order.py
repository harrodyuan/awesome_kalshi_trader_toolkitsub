#!/usr/bin/env python3
"""
Places a single limit order and logs it to a file.
"""

import os
import sys
import uuid
import json
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from clients import KalshiHttpClient, Environment

load_dotenv()

ORDER_LOG_FILE = 'order_log.json'

def log_order_submission(order_data):
    """Appends a new order to the JSON log file."""
    try:
        with open(ORDER_LOG_FILE, 'r') as f:
            # Handle empty file case
            content = f.read()
            if not content:
                logs = []
            else:
                logs = json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    
    logs.insert(0, order_data) # Prepend to keep newest orders at the top
    
    with open(ORDER_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"   - Order details logged to {ORDER_LOG_FILE}")

def place_limit_order(market_ticker, side, action, count, price_cents):
    """Places a limit order and logs the result."""
    
    # Parameter Validation
    if side not in ['yes', 'no'] or action not in ['buy', 'sell'] or not (0 < price_cents < 100):
        print("Error: Invalid arguments. Check side, action, or price.")
        return None

    # Setup client
    try:
        with open(os.getenv('PROD_KEYFILE'), "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        client = KalshiHttpClient(key_id=os.getenv('PROD_KEYID'), private_key=private_key, environment=Environment.PROD)
        print("Connected to Kalshi Production")
    except Exception as e:
        print(f"Setup error: {e}")
        return None

    # Construct the order payload
    order_params = {
        "ticker": market_ticker,
        "client_order_id": str(uuid.uuid4()),
        "type": "limit",
        "action": action,
        "side": side,
        "count": count,
        "post_only": True,
    }
    if side == 'yes':
        order_params['yes_price'] = price_cents
    else:
        order_params['no_price'] = price_cents

    print("\nPlacing order...")
    
    try:
        response = client.post("/trade-api/v2/portfolio/orders", body=order_params)
        
        if 'order' in response:
            print("Order submitted successfully!")
            order_data = response['order']
            order_id = order_data.get('order_id')
            print(f"   - Status: {order_data.get('status')}")
            print(f"   - Order ID: {order_id}")
            
            log_order_submission(order_data)
            return order_id
        else:
            print("Order submission failed.")
            print(f"   Response from API: {response}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python place_order.py <market_ticker> <side> <action> <count> <price_cents>")
        print("Example: python place_order.py KXHIGHNY-25JUL20-B87.5 yes buy 1 92")
        sys.exit(1)
    
    ticker_arg, side_arg, action_arg = sys.argv[1], sys.argv[2].lower(), sys.argv[3].lower()
    try:
        count_arg, price_arg = int(sys.argv[4]), int(sys.argv[5])
    except ValueError:
        print("Error: 'count' and 'price_cents' must be integers.")
        sys.exit(1)

    place_limit_order(ticker_arg, side_arg, action_arg, count_arg, price_arg)
