#!/usr/bin/env python3
"""
Cancels a specific order by its ID.
"""

import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from clients import KalshiHttpClient, Environment

load_dotenv()

def cancel_order_by_id(order_id):
    """Sends a DELETE request to cancel the specified order."""

    # --- Parameter Validation ---
    if not order_id or len(order_id) < 10: # Basic check for a UUID-like string
        print("Invalid 'order_id'. Please provide a valid ID.")
        return
    # --- End of Validation ---

    # Setup client
    try:
        # Assumes .env file is in the parent directory
        with open(os.getenv('PROD_KEYFILE'), "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        
        client = KalshiHttpClient(
            key_id=os.getenv('PROD_KEYID'),
            private_key=private_key,
            environment=Environment.PROD
        )
        print("Connected to Kalshi Production")
    except Exception as e:
        print(f"Setup error: {e}")
        return

    print(f"\nAttempting to cancel order with ID: {order_id}")
    
    try:
        # The endpoint for canceling an order is a DELETE request
        # with the order_id in the path.
        path = f"/trade-api/v2/portfolio/orders/{order_id}"
        response = client.delete(path)
        
        if 'order' in response and response['order'].get('status') == 'canceled':
            print("\nOrder canceled successfully!")
            order_data = response['order']
            print(f"   - Ticker: {order_data.get('ticker')}")
            print(f"   - Final Status: {order_data.get('status')}")
        else:
            print("\nOrder cancellation failed.")
            print(f"   Response from API: {response}")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if hasattr(e, 'response_body'):
            print(f"   API Response Body: {e.response_body}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cancel_order.py <order_id>")
        print("Example: python cancel_order.py 123e4567-e89b-12d3-a456-426614174000")
        sys.exit(1)
    
    order_id_arg = sys.argv[1]
    cancel_order_by_id(order_id_arg)
