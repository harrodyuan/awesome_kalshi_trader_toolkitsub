# Comprehensive Guide of using Kalshi API to submit an order 

I think betting market API is extremly horrible. You're here to make trades, not to read a textbook. Here’s how Kalshi is structured from a trader's perspective and how you can use these tools to get in the game.

 Most of the time,  **Authorization** is the part that trips everyone up, especially when you're trying to use AI tools that don't understand. This guide breaks down how we've solved the hard part so you can focus on the easy part: making trades and the hardest part: trading strategy.

## CONFUSION 1: Events and Markets

Think of it like this:

1.  **Event:** This is the big picture, the main thing happening. Is the Fed going to raise rates? Will it rain in Chicago tomorrow? Highest temperature in NYC today? That's the **Event**.

2.  **Market:** This is where the money is. For any given Event, there are multiple ways to bet on it. These are the **Markets**. For a temperature event, you might have markets for ">80°", ">85°", ">90°", etc. Each one is a separate, tradable thing.

So, the workflow is simple: **Find an Event you have an opinion on, then find the specific Market within that Event that you want to trade.**

## CONFUSION 2: Authorization

This part is tricky. For those interested in the technical details of how we handle secure request signing, see the [Appendix on Authorization](#appendix-the-hard-part---how-authorization-works) at the end of this guide.

## Trading Toolkit

Here’s how you use this repo to go from zero to placing an order.

### Step 1: Fetch Events

Submit an order require you know the ID for that event, which you can not know fromt the website.

Run this command to download a list of all currently open Events.

**Command:**
```bash
python fetch_open_events.py
```
This creates a local file, `open_events.json`. It's your personal, offline map of the Kalshi universe. Run it whenever you feel like your map is getting old (maybe once a day).

### Step 2: Find Your Event

Now, search your local map for something that catches your eye. Got a hunch about inflation? Search for it.

**Command:**
```bash
python search_events.py "Your Keyword"
```
**Example:**
```bash
python search_events.py "inflation"
```
The script will spit out a list of matching Events. Find the one you want and **copy the `Ticker`**. That's your target.

### Step 3: Find the Markets

With your Event Ticker, you can now see all the specific, tradable Markets available for it.

**Command:**
```bash
python search_markets_in_event.py "EVENT_TICKER"
```
**Example:**
```bash
python search_markets_in_event.py "CPI-24DEC"
```
This shows you the real action: the market tickers, what they're asking, what they're bidding. Find the one you want to play in and **copy its `Market Ticker`**.

### Step 4: Place Your Bet (Submit a Maker Order)

This is the final step. Use the `submit_maker_order.py` script to get your order on the books. It's built to be run directly from your terminal—no code editing required.

**Usage:**
```bash
python submit_maker_order.py <market_ticker> <side> <action> <count> <price_cents>
```

**Example:**
We wanted to bet that the high temperature in NYC would be between 87-88°.
1.  We searched for the event and got the ticker `KXHIGHNY-25JUL20`.
2.  We searched that event for markets and found the market ticker `KXHIGHNY-25JUL20-B87.5`.
3.  The current "yes" bid was 99 cents. To place a competitive maker order, we decided to bid 98 cents.
4.  We ran the following command to place the order:

```bash
python submit_maker_order.py KXHIGHNY-25JUL20-B87.5 yes buy 1 98
```

The script will confirm your details, send the order, and then print the `Order ID`. **Copy this ID.** You'll need it for the next step.

For those of you who does not know what does a maker/taker order mean, I can not help you. You should GPT it.

### Step 5: Change Your Mind

If you want to pull your order off the book, use the `cancel_order.py` script with the `Order ID` you just copied.

**Command:**
```bash
python cancel_order.py "YOUR_ORDER_ID"
```

**Example:**
Let's say the previous command returned an Order ID of `XXXX75c3-XXXX-XXXX-a0XX-XXXX`. To cancel it, you would run:

```bash
python cancel_order.py "`XXXX75c3-XXXX-XXXX-a0XX-XXXX"
```
The script will confirm that the order has been successfully canceled.

---

## Initial Setup

Just two things before you start:
1.  **Install dependencies:** `pip install -r requirements.txt`
2.  **Set up your keys:** This repo uses a `.env` file to handle API keys.
    - Rename the `env.example` file to `.env`.
    - Open the `.env` file and fill in your `PROD_KEYID` and the absolute path to your `PROD_KEYFILE`.

I mean, who wants to use the mock environment??? like it is 1 cent that we are talking about. You should put 1 dollar in your account when you are testing.

---

## Appendix: How Authorization Works

This is the step where most people, and most AI tools, fail. Here’s the secret sauce, which is handled entirely by our `clients.py` file so you don't have to worry about it.

Kalshi needs to be 100% sure that every single request is coming from you. This is done through a process called **Request Signing**.

1.  **Create a Unique Message:** For every API call, the client creates a unique string of text. It's a simple combination of:
    *   The exact time (down to the millisecond).
    *   The request type (`GET` or `POST`).
    *   The API endpoint path (like `/portfolio/orders`).

    The raw message looks something like this: `1672531200000POST/portfolio/orders`

2.  **Sign It with Your Private Key:** The client then takes this unique message and uses your secret `.pem` file to create a cryptographic signature. This signature is a long, scrambled piece of text that can only be created by your specific private key. It's impossible to fake.

3.  **Send Everything to Kalshi:** The final request sent to Kalshi includes the normal stuff (like the order details) plus three critical security headers:
    *   Your public API Key ID.
    *   The timestamp from step 1.
    *   The unique signature from step 2.

Kalshi's servers perform the same process on their end. If the signature they generate matches the one you sent, they know the request is authentic. If not, the request is rejected. Our `clients.py` handles this flawlessly every time so you can focus on your trading strategy.
