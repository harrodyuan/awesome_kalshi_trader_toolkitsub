#!/usr/bin/env python3
"""
Search for events in the local open_events.json file
Usage: python search_events.py "search term"
"""

import json
import sys
import os

def search_local_events(search_term):
    """Search for events in the local JSON file"""
    
    if not os.path.exists('open_events.json'):
        print("Error: open_events.json not found.")
        print("Please run 'python fetch_open_events.py' first.")
        return

    with open('open_events.json', 'r') as f:
        events = json.load(f)

    search_lower = search_term.lower()
    found = []

    for event_ticker, event_title in events.items():
        if search_lower in event_title.lower():
            found.append((event_ticker, event_title))

    if found:
        print(f"\nFound {len(found)} matching events:")
        for i, (ticker, title) in enumerate(found[:20], 1):
            print(f"\n{i}. Ticker: {ticker}")
            print(f"   Title: {title}")
        
        if len(found) > 20:
            print(f"\n... and {len(found) - 20} more matches.")

        print("\n--------------------------------------------------")
        print("Next Step:")
        print("1. Copy an Event Ticker.")
        print("2. Run the following command to find markets in that event:")
        print(f"   python search_markets_in_event.py \"{found[0][0]}\"")
        print("--------------------------------------------------")

    else:
        print(f"No events found matching '{search_term}'")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python search_events.py \"search term\"")
        print("Example: python search_events.py \"CPI\"")
        sys.exit(1)
    
    search_local_events(sys.argv[1])
