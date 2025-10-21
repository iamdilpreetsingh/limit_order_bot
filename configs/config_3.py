# Configuration for Trade 3
# Add your own trading pair here

# NOTE: Private key is now stored securely in AWS Secrets Manager
# No need to hardcode PRIVATE_KEY here anymore!
# The bot will fetch it automatically from: limit-order-bot/wallet-key

RPC_URL = "https://mainnet.infura.io/v3/650e1c889a15420b8567dfe1a12e2461"

# Example: USDT -> Another Token
SELL_TOKEN = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
BUY_TOKEN = "0x..."  # Replace with your token address
SELL_AMOUNT = 50
SELL_TOKEN_DECIMALS = 6
BUY_TOKEN_DECIMALS = 18  # Check on Etherscan!

TARGET_PRICE = 100
CHECK_INTERVAL = 2
MAX_SLIPPAGE_PERCENT = 0

MAX_RUNTIME_DAYS = 1
MAX_RUNTIME_MONTHS = 0
MAX_RUNTIME_YEARS = 0

GAS_PRICE_GWEI = 50
APPROVE_GAS_LIMIT = 80000
SWAP_GAS_LIMIT = 500000

BUNDLE_CHECK_DELAY = 10
MAX_BUNDLE_CHECKS = 10

