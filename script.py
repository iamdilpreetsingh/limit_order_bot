import asyncio
from web3 import Web3
from eth_account import Account
from pythereum import TitanBuilder, BuilderRPC, Bundle

# ========================================
# CONFIGURATION - Edit these values
# ========================================

# Your Ethereum private key (keep it secret!)
PRIVATE_KEY = "6c6338e824fcb10f01d7ac61876dac98dbf9de115964914d428353ba43293dc5"

# RPC endpoint
RPC_URL = "https://mainnet.infura.io/v3/650e1c889a15420b8567dfe1a12e2461"

# Swap Configuration
SELL_TOKEN = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
BUY_TOKEN = "0x9Ce84F6A69986a83d92C324df10bC8E64771030f"   # CHEX
SELL_AMOUNT = 100  # Amount of tokens to sell (in human-readable units)
SELL_TOKEN_DECIMALS = 6  # USDT has 6 decimals
MIN_TOKENS_OUT = 2000  # Minimum tokens to receive (0 = no slippage protection)

# Gas settings
GAS_PRICE_GWEI = 50
APPROVE_GAS_LIMIT = 50000
SWAP_GAS_LIMIT = 150000

# ========================================
# Constants
# ========================================

WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
UNISWAP_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
CHAIN_ID = 1  # Ethereum Mainnet

# ERC20 ABI (minimal)
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

# Uniswap Router ABI (minimal)
UNISWAP_ABI = [
    {
        "name": "swapExactTokensForTokens",
        "type": "function",
        "inputs": [
            {"type": "uint256", "name": "amountIn"},
            {"type": "uint256", "name": "amountOutMin"},
            {"type": "address[]", "name": "path"},
            {"type": "address", "name": "to"},
            {"type": "uint256", "name": "deadline"}
        ],
        "outputs": [{"type": "uint256[]", "name": "amounts"}]
    }
]


async def main():
    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    # Create account from private key
    account = Account.from_key(PRIVATE_KEY)
    
    print("=" * 60)
    print("GENERIC UNISWAP SWAP VIA TITAN BUILDER")
    print("=" * 60)
    print(f"Account: {account.address}")
    print(f"Selling: {SELL_AMOUNT} tokens from {SELL_TOKEN}")
    print(f"Buying: {BUY_TOKEN}")
    print(f"Swap path: TOKEN -> WETH -> TOKEN")
    print("=" * 60)
    
    # Create contract instances
    sell_token_contract = w3.eth.contract(address=SELL_TOKEN, abi=ERC20_ABI)
    router_contract = w3.eth.contract(address=UNISWAP_ROUTER, abi=UNISWAP_ABI)
    
    # Convert sell amount to token units (accounting for decimals)
    amount_in_token_units = int(SELL_AMOUNT * (10 ** SELL_TOKEN_DECIMALS))
    
    # Get current nonce
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Get current block timestamp for deadline
    latest_block = w3.eth.get_block('latest')
    deadline = latest_block['timestamp'] + 15778458  # 6 months from now
    
    # Build swap path (SELL_TOKEN -> WETH -> BUY_TOKEN)
    swap_path = [SELL_TOKEN, WETH_ADDRESS, BUY_TOKEN]
    
    print("\n" + "=" * 60)
    print("STEP 1: Approve Uniswap Router to spend tokens")
    print("=" * 60)
    
    # Build approve transaction
    approve_tx = sell_token_contract.functions.approve(
        UNISWAP_ROUTER,
        amount_in_token_units
    ).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": APPROVE_GAS_LIMIT,
        "gasPrice": w3.to_wei(GAS_PRICE_GWEI, 'gwei'),
        "chainId": CHAIN_ID
    })
    
    # Sign approve transaction
    signed_approve = Account.sign_transaction(approve_tx, PRIVATE_KEY)
    approve_tx_hex = signed_approve.rawTransaction.hex()
    print(f"✓ Approve transaction signed")
    print(f"  Nonce: {nonce}")
    print(f"  Approving: {SELL_AMOUNT} tokens")
    
    print("\n" + "=" * 60)
    print("STEP 2: Build swap transaction")
    print("=" * 60)
    
    # Build swap transaction
    swap_tx = router_contract.functions.swapExactTokensForTokens(
        amount_in_token_units,
        MIN_TOKENS_OUT,
        swap_path,
        account.address,
        deadline
    ).build_transaction({
        "from": account.address,
        "nonce": nonce + 1,  # Next nonce after approve
        "gas": SWAP_GAS_LIMIT,
        "gasPrice": w3.to_wei(GAS_PRICE_GWEI, 'gwei'),
        "chainId": CHAIN_ID
    })
    
    # Sign swap transaction
    signed_swap = Account.sign_transaction(swap_tx, PRIVATE_KEY)
    swap_tx_hex = signed_swap.rawTransaction.hex()
    print(f"✓ Swap transaction signed")
    print(f"  Nonce: {nonce + 1}")
    print(f"  Selling: {SELL_AMOUNT} tokens")
    print(f"  Min output: {MIN_TOKENS_OUT} tokens")
    
    print("\n" + "=" * 60)
    print("PRE-FLIGHT CHECKS")
    print("=" * 60)
    
    # Check balances for debugging
    token_balance = sell_token_contract.functions.balanceOf(account.address).call()
    token_balance_human = token_balance / (10 ** SELL_TOKEN_DECIMALS)
    eth_balance = w3.eth.get_balance(account.address)
    eth_balance_human = w3.from_wei(eth_balance, 'ether')
    
    print(f"Token balance: {token_balance_human} tokens")
    print(f"ETH balance: {eth_balance_human} ETH")
    print(f"Trying to sell: {SELL_AMOUNT} tokens")
    
    # Simulate approve transaction
    print("\n🔍 Simulating approve transaction...")
    try:
        w3.eth.call({
            'from': account.address,
            'to': SELL_TOKEN,
            'data': approve_tx['data']
        })
        print("✓ Approve simulation: SUCCESS")
    except Exception as e:
        print(f"✗ Approve simulation FAILED: {str(e)[:200]}")
    
    # Simulate swap transaction
    print("\n🔍 Simulating swap transaction...")
    try:
        w3.eth.call({
            'from': account.address,
            'to': UNISWAP_ROUTER,
            'data': swap_tx['data']
        })
        print("✓ Swap simulation: SUCCESS")
    except Exception as e:
        print(f"✗ Swap simulation FAILED: {str(e)[:200]}")
    
    # Calculate max gas cost
    max_gas_cost_wei = (APPROVE_GAS_LIMIT + SWAP_GAS_LIMIT) * w3.to_wei(GAS_PRICE_GWEI, 'gwei')
    max_gas_cost_eth = w3.from_wei(max_gas_cost_wei, 'ether')
    print(f"\nMax gas cost: {max_gas_cost_eth} ETH")
    
    if eth_balance < max_gas_cost_wei:
        print(f"⚠ WARNING: Not enough ETH for gas! Need {max_gas_cost_eth} ETH")
    
    print("\n" + "=" * 60)
    print("STEP 3: Send transactions to Titan Builder")
    print("=" * 60)
    
    # Send transactions via Titan Builder as a bundle
    async with BuilderRPC(TitanBuilder()) as client:
        # Send as a bundle (preferred for dependent transactions)
        print("\n📤 Sending transaction bundle (approve + swap)...")
        try:
            # Create a Bundle object with the transactions
            bundle = Bundle(txs=[approve_tx_hex, swap_tx_hex])
            bundle_result = await client.send_bundle(bundle)
            print(f"   Bundle Result: {bundle_result}")
            
            # Extract transaction hashes from bundle result
            if bundle_result and len(bundle_result) > 0:
                print(f"   ✓ Bundle submitted successfully!")
                approve_result = bundle_result
                swap_result = bundle_result
            else:
                approve_result = None
                swap_result = None
                
        except Exception as e:
            print(f"   Bundle ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            approve_result = None
            swap_result = None
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        if approve_result and len(approve_result) > 0 and approve_result[0]:
            print(f"✓ Approve TX Hash: {approve_result[0]}")
        else:
            print(f"⚠ Approve returned: {approve_result}")
        
        if swap_result and len(swap_result) > 0 and swap_result[0]:
            print(f"✓ Swap TX Hash: {swap_result[0]}")
            print(f"\n🎉 SUCCESS! Your swap has been submitted privately!")
        else:
            print(f"⚠ Swap returned: {swap_result}")
            print("\nPossible reasons:")
            print("  - Builder rejected the transaction")
            print("  - Invalid transaction parameters")
            print("  - Liquidity issues on the swap path")
            print("  - Transaction would revert (see simulation above)")


if __name__ == "__main__":
    asyncio.run(main())
