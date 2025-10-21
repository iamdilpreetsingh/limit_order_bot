# Configuration for Trade 2
# USDT -> CHEX (example)

# NOTE: Private key is now stored securely in AWS Secrets Manager
# No need to hardcode PRIVATE_KEY here anymore!
# The bot will fetch it automatically from: limit-order-bot/wallet-key

# RPC endpoint
RPC_URL = "https://mainnet.infura.io/v3/650e1c889a15420b8567dfe1a12e2461"

# Swap Configuration
SELL_TOKEN = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
BUY_TOKEN = "0x295B42684F90c77DA7ea46336001010F2791Ec8c"   # Xi
SELL_AMOUNT = 60
SELL_TOKEN_DECIMALS = 6
BUY_TOKEN_DECIMALS = 18

# Limit Order Settings
TARGET_PRICE = 100000
CHECK_INTERVAL = 1
MAX_SLIPPAGE_PERCENT = 0

# Max Runtime Settings
MAX_RUNTIME_DAYS = 0
MAX_RUNTIME_MONTHS = 1
MAX_RUNTIME_YEARS = 0

# Gas settings
GAS_PRICE_GWEI = 5
APPROVE_GAS_LIMIT = 80000
SWAP_GAS_LIMIT = 500000

# Bundle Tracing
BUNDLE_CHECK_DELAY = 10
MAX_BUNDLE_CHECKS = 10

