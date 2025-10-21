# Configuration Files

Each config file represents one trading pair/strategy.

## How to Add More Configs:

1. Copy `config_1.py` to `config_3.py`, `config_4.py`, etc.
2. Edit the values for your trading pair
3. The launcher will automatically detect all configs

## Config Template:

```python
# Your config name
PRIVATE_KEY = "your_key_here"
RPC_URL = "your_rpc_url"

SELL_TOKEN = "0x..."
BUY_TOKEN = "0x..."
SELL_AMOUNT = 100
SELL_TOKEN_DECIMALS = 6
BUY_TOKEN_DECIMALS = 18

TARGET_PRICE = 1000
CHECK_INTERVAL = 2
MAX_SLIPPAGE_PERCENT = 0

MAX_RUNTIME_DAYS = 1
GAS_PRICE_GWEI = 50
```

## Important:

- Each config must have unique trading pairs or targets
- All configs use the same private key (same wallet)
- Make sure you have enough balance for all trades
