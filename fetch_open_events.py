#!/usr/bin/env python3
"""
Fetch all open markets and save to file (run once)
Usage: python fetch_open_markets.py
"""

import os
import json
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from clients import KalshiHttpClient, Environment

load_dotenv()

def fetch_and_save_open_markets():
    """Fetch all open markets and save to JSON file"""
    
    # Setup client
    try:
        with open(os.getenv('PROD_KEYFILE'), "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        
        client = KalshiHttpClient(
            key_id=os.getenv('PROD_KEYID'),
            private_key=private_key,
            environment=Environment.PROD
        )
        print("✅ Connected to Kalshi Production")
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False
    
    print("🔍 Fetching all open markets...")
    
    all_markets = {}
    cursor = None
    page = 1
    total_count = 0
    
    while True:
        url = "/trade-api/v2/events?status=open"
        if cursor:
            url += f"&cursor={cursor}"
        
        print(f"   Fetching page {page}...", end=" ")
        
        try:
            response = client.get(url)
            events = response.get('events', [])
            
            if not events:
                break
            
            # Store events
            for event in events:
                event_id = event.get('event_ticker')
                event_name = event.get('title', '')
                
                if event_id:
                    all_markets[event_id] = event_name
                    total_count += 1
            
            print(f"✅ ({len(events)} events)")
            
            cursor = response.get('cursor')
            if not cursor:
                break
                
            page += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Save to file
    try:
        with open('open_events.json', 'w') as f:
            json.dump(all_markets, f, indent=2)
        
        print(f"\n🎯 SUCCESS!")
        print(f"📊 Total open events: {total_count}")
        print(f"💾 Saved to: open_events.json")
        print(f"📝 File size: {os.path.getsize('open_events.json')} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🏛️  KALSHI OPEN MARKETS FETCHER")
    print("=" * 50)
    
    success = fetch_and_save_open_markets()
    
    if success:
        print(f"\n✅ Done! Now you can use:")
        print(f"   python search_events.py \"search term\"")
    else:
        print(f"\n❌ Failed to fetch events")
