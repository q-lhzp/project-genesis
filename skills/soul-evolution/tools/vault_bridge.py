#!/usr/bin/env python3
"""
Vault Bridge - Real Asset Trading (Crypto/Stocks)
Interfaces with Kraken (Crypto) or Alpaca (Stocks) APIs.
Default mode: Paper Trading (Sandbox) for safety.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.abspath("memory/reality")
STATE_FILE = os.path.join(CONFIG_DIR, "vault_state.json")


def ensure_state() -> Dict:
    """Ensure vault state file exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    else:
        initial_state = {
            "mode": "paper",  # "paper" or "live"
            "api_provider": None,  # "kraken" or "alpaca"
            "api_key": "",
            "api_secret": "",
            "balances": {},
            "positions": {},
            "transactions": [],
            "total_deposited": 0.0,
            "last_updated": datetime.now().isoformat()
        }
        with open(STATE_FILE, "w") as f:
            json.dump(initial_state, f, indent=2)
        return initial_state


def save_state(state: Dict):
    """Save vault state."""
    state["last_updated"] = datetime.now().isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_config() -> Dict:
    """Get API configuration from model_config.json."""
    config_path = os.path.join(CONFIG_DIR, "model_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
            return {
                "api_key": config.get("vault_api_key", ""),
                "api_secret": config.get("vault_api_secret", ""),
                "provider": config.get("vault_provider", "kraken")
            }
    return {"api_key": "", "api_secret": "", "provider": "kraken"}


# -------------------------------------------------------------------
# Kraken API Implementation
# -------------------------------------------------------------------
class KrakenBridge:
    def __init__(self, api_key: str = "", api_secret: str = "", paper: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.base_url = "https://api.kraken.com"  # Sandbox uses same URL with different keys

    def get_balance(self) -> Dict:
        """Get account balance."""
        if self.paper:
            state = ensure_state()
            return {"success": True, "balances": state.get("balances", {}), "mode": "paper"}

        # Real implementation would use krakenex
        # For now, return paper mode
        return self.get_balance()

    def get_price(self, symbol: str) -> Dict:
        """Get current price for a symbol."""
        # Map common symbols to Kraken pairs
        symbol_map = {
            "BTC": "XXBTZUSD",
            "ETH": "XETHZUSD",
            "SOL": "SOLUSD",
            "XRP": "XXRPZUSD",
            "ADA": "ADAUSD",
            "DOGE": "XDGUSD"
        }
        pair = symbol_map.get(symbol.upper(), f"{symbol}USD")

        if self.paper:
            # Return mock price
            import random
            base_prices = {
                "BTC": 45000, "ETH": 2500, "SOL": 100,
                "XRP": 0.55, "ADA": 0.45, "DOGE": 0.08
            }
            price = base_prices.get(symbol.upper(), 100.0)
            price *= (1 + random.uniform(-0.02, 0.02))  # ±2% variance
            return {"success": True, "price": price, "symbol": symbol, "mode": "paper"}

        return {"success": False, "error": "Live trading not implemented"}

    def execute_trade(self, symbol: str, amount: float, trade_type: str) -> Dict:
        """Execute a trade (buy/sell)."""
        if self.paper:
            state = ensure_state()
            symbol = symbol.upper()

            # Get current price
            price_result = self.get_price(symbol)
            if not price_result.get("success"):
                return price_result
            price = price_result["price"]

            # Calculate totals
            total = amount * price

            if trade_type == "buy":
                # Check USD balance
                usd_balance = state.get("balances", {}).get("USD", 0)
                if usd_balance < total:
                    return {"success": False, "error": f"Insufficient USD balance: {usd_balance}"}

                # Update balances
                state["balances"]["USD"] = state["balances"].get("USD", 0) - total
                state["balances"][symbol] = state["balances"].get(symbol, 0) + amount

                # Add position
                if symbol in state["positions"]:
                    pos = state["positions"][symbol]
                    pos["amount"] += amount
                    pos["avg_price"] = (pos["avg_price"] * (pos["amount"] - amount) + price * amount) / pos["amount"]
                else:
                    state["positions"][symbol] = {"amount": amount, "avg_price": price}

            elif trade_type == "sell":
                # Check crypto balance
                crypto_balance = state.get("balances", {}).get(symbol, 0)
                if crypto_balance < amount:
                    return {"success": False, "error": f"Insufficient {symbol} balance: {crypto_balance}"}

                # Update balances
                state["balances"]["USD"] = state["balances"].get("USD", 0) + total
                state["balances"][symbol] = state["balances"].get(symbol, 0) - amount

                # Update position
                if symbol in state["positions"]:
                    pos = state["positions"][symbol]
                    pos["amount"] -= amount
                    if pos["amount"] <= 0:
                        del state["positions"][symbol]

            # Record transaction
            tx = {
                "id": f"tx_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "amount": amount,
                "price": price,
                "total": total,
                "type": trade_type,
                "mode": "paper"
            }
            state.setdefault("transactions", []).insert(0, tx)

            save_state(state)
            return {"success": True, "transaction": tx, "mode": "paper"}

        return {"success": False, "error": "Live trading not implemented"}


# -------------------------------------------------------------------
# Alpaca Stock API (Alternative)
# -------------------------------------------------------------------
class AlpacaBridge:
    def __init__(self, api_key: str = "", api_secret: str = "", paper: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper

    def get_balance(self) -> Dict:
        """Get account balance."""
        if self.paper:
            state = ensure_state()
            return {"success": True, "balances": state.get("balances", {}), "mode": "paper"}
        return {"success": False, "error": "Live trading not implemented"}

    def get_price(self, symbol: str) -> Dict:
        """Get current stock price."""
        if self.paper:
            import random
            base_prices = {
                "AAPL": 175, "GOOGL": 140, "MSFT": 380,
                "AMZN": 175, "NVDA": 450, "TSLA": 250,
                "META": 350, "NFLX": 450
            }
            price = base_prices.get(symbol.upper(), 100.0)
            price *= (1 + random.uniform(-0.02, 0.02))
            return {"success": True, "price": price, "symbol": symbol, "mode": "paper"}
        return {"success": False, "error": "Live trading not implemented"}

    def execute_trade(self, symbol: str, amount: float, trade_type: str) -> Dict:
        """Execute a stock trade."""
        return KrakenBridge(paper=self.paper).execute_trade(symbol, amount, trade_type)


# -------------------------------------------------------------------
# Main Bridge Interface
# -------------------------------------------------------------------
def get_bridge(provider: str = "kraken", paper: bool = True):
    """Get appropriate bridge based on provider."""
    config = get_config()
    if provider == "alpaca":
        return AlpacaBridge(config["api_key"], config["api_secret"], paper)
    return KrakenBridge(config["api_key"], config["api_secret"], paper)


def handle_action(action: str, params: Dict) -> Dict:
    """Handle trading actions."""
    state = ensure_state()
    paper = state.get("mode", "paper") == "paper"
    provider = state.get("api_provider", "kraken")

    bridge = get_bridge(provider, paper)

    if action == "balance":
        return bridge.get_balance()

    elif action == "price":
        symbol = params.get("symbol", "BTC")
        return bridge.get_price(symbol)

    elif action == "trade":
        symbol = params.get("symbol")
        amount = params.get("amount")
        trade_type = params.get("type", "buy")

        if not symbol or not amount:
            return {"success": False, "error": "symbol and amount are required"}

        return bridge.execute_trade(symbol, amount, trade_type)

    elif action == "deposit":
        # Simulate deposit to vault
        amount = params.get("amount", 0)
        if amount <= 0:
            return {"success": False, "error": "Amount must be positive"}

        state["balances"]["USD"] = state["balances"].get("USD", 0) + amount
        state["total_deposited"] = state.get("total_deposited", 0) + amount
        save_state(state)

        return {
            "success": True,
            "deposited": amount,
            "total_balance": state["balances"]["USD"],
            "mode": "paper"
        }

    elif action == "status":
        return {
            "success": True,
            "mode": state.get("mode", "paper"),
            "provider": provider,
            "total_deposited": state.get("total_deposited", 0),
            "positions": state.get("positions", {}),
            "transaction_count": len(state.get("transactions", []))
        }

    return {"success": False, "error": f"Unknown action: {action}"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Action required"}))
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])
    except:
        data = {}

    action = data.get("action", sys.argv[1]) if len(sys.argv) == 2 else data.get("action")

    result = handle_action(action, data)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
