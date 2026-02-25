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
import urllib.request
import urllib.error
from urllib.parse import urlencode
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
        # Alpaca API endpoints
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.data_url = "https://data.alpaca.markets"

    def _headers(self) -> Dict:
        """Get headers for Alpaca API requests."""
        return {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Content-Type": "application/json"
        }

    def get_account(self) -> Dict:
        """Get account information - REAL API."""
        if self.paper:
            state = ensure_state()
            return {"success": True, "balances": state.get("balances", {}), "mode": "paper"}

        if not self.api_key or not self.api_secret:
            return {"success": False, "error": "API keys required for live trading"}

        import urllib.request
        import json

        url = f"{self.base_url}/v2/account"
        req = urllib.request.Request(url, headers=self._headers())

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)
                return {
                    "success": True,
                    "mode": "live",
                    "account": {
                        "id": data.get("id"),
                        "cash": data.get("cash"),
                        "portfolio_value": data.get("portfolio_value"),
                        "equity": data.get("equity"),
                        "buying_power": data.get("buying_power"),
                        "status": data.get("status")
                    }
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_positions(self) -> Dict:
        """Get open positions - REAL API."""
        if self.paper:
            state = ensure_state()
            return {"success": True, "positions": state.get("positions", {}), "mode": "paper"}

        if not self.api_key or not self.api_secret:
            return {"success": False, "error": "API keys required for live trading"}

        import urllib.request
        import json

        url = f"{self.base_url}/v2/positions"
        req = urllib.request.Request(url, headers=self._headers())

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)
                positions = {}
                for pos in data:
                    positions[pos.get("symbol")] = {
                        "qty": float(pos.get("qty", 0)),
                        "avg_entry_price": float(pos.get("avg_entry_price", 0)),
                        "market_value": float(pos.get("market_value", 0)),
                        "unrealized_pl": float(pos.get("unrealized_pl", 0))
                    }
                return {"success": True, "positions": positions, "mode": "live"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def submit_order(self, symbol: str, qty: float, side: str, order_type: str = "market", limit_price: float = None, time_in_force: str = "day") -> Dict:
        """Submit an order - REAL API."""
        if self.paper:
            # Use paper trading logic
            return KrakenBridge(paper=self.paper).execute_trade(symbol, qty, side)

        if not self.api_key or not self.api_secret:
            return {"success": False, "error": "API keys required for live trading"}

        import urllib.request
        import json

        url = f"{self.base_url}/v2/orders"
        payload = {
            "symbol": symbol.upper(),
            "qty": str(int(qty)) if qty == int(qty) else str(qty),
            "side": side.lower(),
            "type": order_type.lower(),
            "time_in_force": time_in_force
        }
        if limit_price:
            payload["limit_price"] = str(limit_price)

        data = bytes(json.dumps(payload), 'utf-8')
        req = urllib.request.Request(url, data=data, headers=self._headers(), method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                order_data = json.load(response)
                return {
                    "success": True,
                    "mode": "live",
                    "order": {
                        "id": order_data.get("id"),
                        "symbol": order_data.get("symbol"),
                        "qty": order_data.get("qty"),
                        "side": order_data.get("side"),
                        "type": order_data.get("type"),
                        "status": order_data.get("status")
                    }
                }
        except urllib.error.HTTPError as e:
            error_body = json.loads(e.read().decode())
            return {"success": False, "error": error_body.get("message", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order - REAL API."""
        if self.paper:
            return {"success": True, "mode": "paper", "message": "Paper trading - no orders to cancel"}

        if not self.api_key or not self.api_secret:
            return {"success": False, "error": "API keys required for live trading"}

        import urllib.request

        url = f"{self.base_url}/v2/orders/{order_id}"
        req = urllib.request.Request(url, headers=self._headers(), method="DELETE")

        try:
            with urllib.request.urlopen(req) as response:
                return {"success": True, "mode": "live", "message": f"Order {order_id} cancelled"}
        except urllib.error.HTTPError as e:
            if e.code == 422:
                return {"success": True, "mode": "live", "message": f"Order {order_id} already filled or cancelled"}
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_historical(self, symbol: str, timeframe: str = "1D", start: str = None, end: str = None) -> Dict:
        """Get historical bar data - REAL API."""
        if self.paper:
            # Return mock data for paper trading
            import random
            base_prices = {
                "AAPL": 175, "GOOGL": 140, "MSFT": 380,
                "AMZN": 175, "NVDA": 450, "TSLA": 250,
                "META": 350, "NFLX": 450
            }
            base = base_prices.get(symbol.upper(), 100.0)
            return {
                "success": True,
                "mode": "paper",
                "symbol": symbol,
                "bars": [
                    {"t": f"2024-01-{i+1:02d}", "o": base * (1 + random.uniform(-0.02, 0.02)),
                     "h": base * 1.02, "l": base * 0.98, "c": base * (1 + random.uniform(-0.02, 0.02)), "v": 1000000}
                    for i in range(30)
                ]
            }

        if not self.api_key or not self.api_secret:
            return {"success": False, "error": "API keys required for live trading"}

        import urllib.request
        import json
        from urllib.parse import urlencode

        params = {"symbols": symbol.upper(), "timeframe": timeframe}
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        url = f"{self.data_url}/v2/stocks/bars?{urlencode(params)}"
        req = urllib.request.Request(url, headers=self._headers())

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)
                bars = data.get("bars", {}).get(symbol.upper(), [])
                return {
                    "success": True,
                    "mode": "live",
                    "symbol": symbol,
                    "bars": [{"t": b.get("t"), "o": b.get("o"), "h": b.get("h"),
                              "l": b.get("l"), "c": b.get("c"), "v": b.get("v")} for b in bars]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_balance(self) -> Dict:
        """Get account balance."""
        return self.get_account()

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
        return self.get_quote(symbol)

    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote."""
        if not self.api_key or not self.api_secret:
            return {"success": False, "error": "API keys required"}

        import urllib.request
        import json

        url = f"{self.data_url}/v2/stocks/{symbol.upper()}/quotes/latest"
        req = urllib.request.Request(url, headers=self._headers())

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)
                quote = data.get("quote", {})
                return {
                    "success": True,
                    "symbol": symbol,
                    "bid": quote.get("bp"),
                    "ask": quote.get("ap"),
                    "last": quote.get("lp"),
                    "mode": "live"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_trade(self, symbol: str, amount: float, trade_type: str) -> Dict:
        """Execute a stock trade (buy/sell)."""
        return self.submit_order(symbol, amount, trade_type)


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
            "api_key": state.get("api_key", ""),
            "api_secret": state.get("api_secret", ""),
            "total_deposited": state.get("total_deposited", 0),
            "balances": state.get("balances", {}),
            "positions": state.get("positions", {}),
            "transactions": state.get("transactions", []),
            "market_reports": state.get("market_reports", []),
            "transaction_count": len(state.get("transactions", []))
        }

    # Alpaca-specific actions
    elif action == "account":
        return bridge.get_account()

    elif action == "positions":
        return bridge.get_positions()

    elif action == "order":
        symbol = params.get("symbol")
        qty = params.get("qty") or params.get("amount")
        side = params.get("side") or params.get("type", "buy")
        order_type = params.get("order_type", "market")
        limit_price = params.get("limit_price")

        if not symbol or not qty:
            return {"success": False, "error": "symbol and qty are required"}

        return bridge.submit_order(symbol, float(qty), side, order_type, float(limit_price) if limit_price else None)

    elif action == "cancel_order":
        order_id = params.get("order_id")
        if not order_id:
            return {"success": False, "error": "order_id is required"}
        return bridge.cancel_order(order_id)

    elif action == "historical":
        symbol = params.get("symbol")
        if not symbol:
            return {"success": False, "error": "symbol is required"}
        timeframe = params.get("timeframe", "1D")
        start = params.get("start")
        end = params.get("end")
        return bridge.get_historical(symbol, timeframe, start, end)

    elif action == "quote":
        symbol = params.get("symbol")
        if not symbol:
            return {"success": False, "error": "symbol is required"}
        return bridge.get_quote(symbol)

    elif action == "switch_mode":
        new_mode = params.get("mode", "paper")
        if new_mode not in ["paper", "live"]:
            return {"success": False, "error": "mode must be 'paper' or 'live'"}
        state["mode"] = new_mode
        save_state(state)
        return {"success": True, "mode": new_mode}

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
