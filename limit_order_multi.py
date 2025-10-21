"""
Multi-instance compatible limit order script
Accepts config file as command line argument
"""
import asyncio
import time
import requests
import sys
import importlib.util
import json
import boto3
from botocore.exceptions import ClientError
from web3 import Web3
from eth_account import Account
from pythereum import TitanBuilder, BuilderRPC, Bundle

# ============================================================
# AWS Secrets Manager Integration
# ============================================================

def get_secret(secret_name, region_name="us-east-1"):
    """
    Fetch secret from AWS Secrets Manager
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(f"❌ Error fetching secret from AWS Secrets Manager: {e}")
        raise e
    
    # Secrets Manager returns a JSON string
    secret = get_secret_value_response['SecretString']
    secret_dict = json.loads(secret)
    return secret_dict

# Load config from command line argument
if len(sys.argv) < 2:
    print("Usage: python limit_order_multi.py <config_file>")
    print("Example: python limit_order_multi.py configs/config_1.py")
    sys.exit(1)

config_file = sys.argv[1]

# Load configuration dynamically
spec = importlib.util.spec_from_file_location("config", config_file)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

# Extract config values
# Fetch WALLET_KEY from AWS Secrets Manager
try:
    print("🔐 Fetching private key from AWS Secrets Manager...")
    secrets = get_secret("limit-order-bot/wallet-key", "eu-north-1")
    WALLET_KEY = secrets['WALLET_KEY']
    print("✅ Private key loaded securely!")
except Exception as e:
    print(f"❌ Failed to load private key from Secrets Manager: {e}")
    print("💡 Make sure:")
    print("   1. Your EC2 has the correct IAM role attached")
    print("   2. The secret 'limit-order-bot/wallet-key' exists")
    print("   3. The secret contains key 'WALLET_KEY'")
    sys.exit(1)
RPC_URL = config.RPC_URL
SELL_TOKEN = config.SELL_TOKEN
BUY_TOKEN = config.BUY_TOKEN
SELL_AMOUNT = config.SELL_AMOUNT
SELL_TOKEN_DECIMALS = config.SELL_TOKEN_DECIMALS
BUY_TOKEN_DECIMALS = config.BUY_TOKEN_DECIMALS
TARGET_PRICE = config.TARGET_PRICE
CHECK_INTERVAL = config.CHECK_INTERVAL
MAX_SLIPPAGE_PERCENT = config.MAX_SLIPPAGE_PERCENT
MAX_RUNTIME_DAYS = config.MAX_RUNTIME_DAYS
MAX_RUNTIME_MONTHS = config.MAX_RUNTIME_MONTHS
MAX_RUNTIME_YEARS = config.MAX_RUNTIME_YEARS
GAS_PRICE_GWEI = config.GAS_PRICE_GWEI
APPROVE_GAS_LIMIT = config.APPROVE_GAS_LIMIT
SWAP_GAS_LIMIT = config.SWAP_GAS_LIMIT
BUNDLE_CHECK_DELAY = config.BUNDLE_CHECK_DELAY
MAX_BUNDLE_CHECKS = config.MAX_BUNDLE_CHECKS

# Constants
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
UNISWAP_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
CHAIN_ID = 1
TITAN_STATS_URL = "https://stats.titanbuilder.xyz"

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
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_owner", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

# Uniswap Router ABI
UNISWAP_ABI = [
    {
        "name": "getAmountsOut",
        "type": "function",
        "inputs": [
            {"type": "uint256", "name": "amountIn"},
            {"type": "address[]", "name": "path"}
        ],
        "outputs": [{"type": "uint256[]", "name": "amounts"}],
        "stateMutability": "view"
    },
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


def check_bundle_status(bundle_hash):
    """Check the status of a bundle using Titan Builder's bundle tracing API"""
    try:
        payload = {
            "method": "titan_getBundleStats",
            "params": [{"bundleHash": bundle_hash}],
            "jsonrpc": "2.0",
            "id": 1
        }
        
        response = requests.post(TITAN_STATS_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if "result" in result:
            return result["result"]
        return None
    except Exception as e:
        print(f"   ⚠ Error checking bundle status: {str(e)[:100]}")
        return None


def explain_bundle_status(status_data):
    """Explain the bundle status in human-readable terms"""
    if not status_data:
        return "❓ Unknown - could not fetch status"
    
    status = status_data.get("status", "Unknown")
    
    explanations = {
        "Received": "⏳ Received but arrived too late to be added to the pool",
        "Invalid": "❌ Invalid bundle (check RLP encoding, block number, nonces, Chain ID)",
        "SimulationFail": "❌ Simulation failed (transaction reverted or insufficient builder payment)",
        "SimulationPass": "✓ Passed simulation but sent too late to be included",
        "ExcludedFromBlock": "⚠️ Valid but not selected (likely insufficient gas/bribe or sent too late)",
        "IncludedInBlock": "🟡 Considered but another algorithm produced a more valuable block",
        "Submitted": "✅ INCLUDED IN BLOCK AND EXECUTED! Trade completed successfully!"
    }
    
    explanation = explanations.get(status, f"❓ Unknown status: {status}")
    
    if "error" in status_data and status_data["error"]:
        explanation += f"\n   Error: {status_data['error']}"
    
    if "builderPayment" in status_data:
        explanation += f"\n   Builder Payment: {status_data['builderPayment']} wei"
    
    return explanation


async def track_bundle_status(bundle_hash):
    """Track bundle status over time until it's confirmed or clearly rejected"""
    print(f"\n🔍 Tracking bundle status...")
    print(f"   Bundle Hash: {bundle_hash}")
    print(f"   Will check every {BUNDLE_CHECK_DELAY} seconds for up to {MAX_BUNDLE_CHECKS} attempts")
    
    for attempt in range(1, MAX_BUNDLE_CHECKS + 1):
        await asyncio.sleep(BUNDLE_CHECK_DELAY)
        
        print(f"\n📊 Status Check #{attempt}...")
        status_data = check_bundle_status(bundle_hash)
        
        if status_data:
            status = status_data.get("status", "Unknown")
            print(f"   Status: {status}")
            print(f"   {explain_bundle_status(status_data)}")
            
            if status == "Submitted":
                print(f"\n🎉 SUCCESS! Your trade was EXECUTED on-chain!")
                return True
            
            if status in ["Invalid", "SimulationFail", "ExcludedFromBlock"]:
                print(f"\n⚠️ Bundle was NOT included. Your funds are safe (nothing spent).")
                if status == "ExcludedFromBlock":
                    print(f"💡 TIP: Increase GAS_PRICE_GWEI (currently {GAS_PRICE_GWEI} gwei) and try again")
                return False
            
            if status in ["Received", "SimulationPass", "IncludedInBlock"]:
                print(f"   ⏳ Continuing to monitor...")
        else:
            print(f"   ⚠️ Could not fetch status (bundle may be too recent)")
    
    print(f"\n⏱️ Stopped tracking after {MAX_BUNDLE_CHECKS} attempts ({MAX_BUNDLE_CHECKS * BUNDLE_CHECK_DELAY} seconds)")
    print(f"⚠️ Bundle status unclear - please check your wallet manually!")
    return False


def get_current_price(w3, router_contract, amount_in, swap_path):
    """Get the current price for the swap"""
    try:
        amounts_out = router_contract.functions.getAmountsOut(
            amount_in,
            swap_path
        ).call()
        return amounts_out[-1]
    except Exception as e:
        print(f"   ⚠ Could not get price: {str(e)[:100]}")
        return None


def check_allowance(w3, token_contract, owner, spender):
    """Check current allowance for a token"""
    try:
        return token_contract.functions.allowance(spender, owner).call()
    except:
        return 0


async def execute_order(w3, account, sell_token_contract, router_contract, 
                       amount_in_token_units, min_tokens_out, swap_path):
    """Execute the swap order by sending a bundle to Titan Builder"""
    print("\n" + "=" * 60)
    print("⚡ EXECUTING ORDER")
    print("=" * 60)
    
    nonce = w3.eth.get_transaction_count(account.address)
    latest_block = w3.eth.get_block('latest')
    deadline = latest_block['timestamp'] + 300
    
    current_allowance = check_allowance(w3, sell_token_contract, account.address, UNISWAP_ROUTER)
    needs_approval = current_allowance < amount_in_token_units
    
    transactions = []
    current_nonce = nonce
    
    if needs_approval:
        print(f"✓ Building approve transaction (nonce: {current_nonce})...")
        approve_tx = sell_token_contract.functions.approve(
            UNISWAP_ROUTER,
            amount_in_token_units
        ).build_transaction({
            "from": account.address,
            "nonce": current_nonce,
            "gas": APPROVE_GAS_LIMIT,
            "gasPrice": w3.to_wei(GAS_PRICE_GWEI, 'gwei'),
            "chainId": CHAIN_ID
        })
        
        signed_approve = Account.sign_transaction(approve_tx, WALLET_KEY)
        approve_tx_hex = signed_approve.rawTransaction.hex()
        transactions.append(approve_tx_hex)
        current_nonce += 1
    else:
        print(f"✓ Approval not needed (allowance: {current_allowance})")
    
    print(f"✓ Building swap transaction (nonce: {current_nonce})...")
    swap_tx = router_contract.functions.swapExactTokensForTokens(
        amount_in_token_units,
        min_tokens_out,
        swap_path,
        account.address,
        deadline
    ).build_transaction({
        "from": account.address,
        "nonce": current_nonce,
        "gas": SWAP_GAS_LIMIT,
        "gasPrice": w3.to_wei(GAS_PRICE_GWEI, 'gwei'),
        "chainId": CHAIN_ID
    })
    
    signed_swap = Account.sign_transaction(swap_tx, WALLET_KEY)
    swap_tx_hex = signed_swap.rawTransaction.hex()
    transactions.append(swap_tx_hex)
    
    print("\n🔍 Final simulation check...")
    try:
        w3.eth.call({
            'from': account.address,
            'to': UNISWAP_ROUTER,
            'data': swap_tx['data']
        })
        print("✓ Swap simulation: SUCCESS")
    except Exception as e:
        print(f"✗ Swap simulation FAILED: {str(e)[:200]}")
        print("❌ Aborting order - would likely fail on-chain!")
        return None
    
    print("\n📤 Sending bundle to Titan Builder...")
    try:
        async with BuilderRPC(TitanBuilder()) as client:
            bundle = Bundle(txs=transactions)
            bundle_result = await client.send_bundle(bundle)
            
            if bundle_result and len(bundle_result) > 0:
                bundle_hash = bundle_result[0].get('bundleHash') if isinstance(bundle_result[0], dict) else bundle_result[0]
                print(f"✅ Bundle submitted to Titan Builder!")
                print(f"   Bundle Hash: {bundle_hash}")
                return bundle_hash
            else:
                print(f"❌ Bundle submission failed: {bundle_result}")
                return None
                
    except Exception as e:
        print(f"❌ Error submitting bundle: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def monitor_and_execute():
    """Main monitoring loop"""
    print(f"\n🔧 Loading config: {config_file}")
    
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    account = Account.from_key(WALLET_KEY)
    
    total_runtime_seconds = 0
    if MAX_RUNTIME_YEARS > 0:
        total_runtime_seconds += MAX_RUNTIME_YEARS * 365 * 24 * 60 * 60
    if MAX_RUNTIME_MONTHS > 0:
        total_runtime_seconds += MAX_RUNTIME_MONTHS * 30 * 24 * 60 * 60
    if MAX_RUNTIME_DAYS > 0:
        total_runtime_seconds += MAX_RUNTIME_DAYS * 24 * 60 * 60
    
    has_max_runtime = total_runtime_seconds > 0
    start_time = time.time()
    expiration_time = start_time + total_runtime_seconds if has_max_runtime else None
    
    print("=" * 60)
    print("🎯 LIMIT ORDER MONITOR - TITAN BUILDER")
    print("=" * 60)
    print(f"Config: {config_file}")
    print(f"Account: {account.address}")
    print(f"Selling: {SELL_AMOUNT} tokens (decimals: {SELL_TOKEN_DECIMALS})")
    print(f"Buying: tokens (decimals: {BUY_TOKEN_DECIMALS})")
    print(f"Target: At least {TARGET_PRICE} tokens")
    print(f"Checking every: {CHECK_INTERVAL} seconds")
    if has_max_runtime:
        runtime_str = []
        if MAX_RUNTIME_YEARS > 0:
            runtime_str.append(f"{MAX_RUNTIME_YEARS} year(s)")
        if MAX_RUNTIME_MONTHS > 0:
            runtime_str.append(f"{MAX_RUNTIME_MONTHS} month(s)")
        if MAX_RUNTIME_DAYS > 0:
            runtime_str.append(f"{MAX_RUNTIME_DAYS} day(s)")
        print(f"Max runtime: {', '.join(runtime_str)}")
        expiration_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expiration_time))
        print(f"Will expire at: {expiration_timestamp}")
    else:
        print(f"Max runtime: Unlimited")
    print("=" * 60)
    
    sell_token_contract = w3.eth.contract(address=SELL_TOKEN, abi=ERC20_ABI)
    router_contract = w3.eth.contract(address=UNISWAP_ROUTER, abi=UNISWAP_ABI)
    
    amount_in_token_units = int(SELL_AMOUNT * (10 ** SELL_TOKEN_DECIMALS))
    swap_path = [SELL_TOKEN, WETH_ADDRESS, BUY_TOKEN]
    target_tokens_human = TARGET_PRICE * (1 - MAX_SLIPPAGE_PERCENT / 100)
    min_acceptable = int(target_tokens_human * (10 ** BUY_TOKEN_DECIMALS))
    
    token_balance = sell_token_contract.functions.balanceOf(account.address).call()
    token_balance_human = token_balance / (10 ** SELL_TOKEN_DECIMALS)
    eth_balance = w3.eth.get_balance(account.address)
    eth_balance_human = w3.from_wei(eth_balance, 'ether')
    
    print(f"\n💰 Initial Balances:")
    print(f"   Sell Token: {token_balance_human}")
    print(f"   ETH: {eth_balance_human}")
    
    if token_balance < amount_in_token_units:
        print(f"\n❌ ERROR: Insufficient token balance!")
        print(f"   Need: {SELL_AMOUNT}, Have: {token_balance_human}")
        return
    
    print(f"\n🔍 Starting price monitoring...")
    print(f"   Will execute when price >= {TARGET_PRICE} tokens")
    print(f"   Minimum acceptable: {target_tokens_human} tokens")
    print(f"\n   Press Ctrl+C to stop monitoring\n")
    
    check_count = 0
    
    try:
        while True:
            if has_max_runtime:
                current_time = time.time()
                if current_time >= expiration_time:
                    elapsed = current_time - start_time
                    elapsed_hours = elapsed / 3600
                    print(f"\n⏱️ Max runtime exceeded!")
                    print(f"   Ran for: {elapsed_hours:.2f} hours")
                    print(f"   Total checks: {check_count}")
                    print(f"\n⏹️ Stopping monitor - expired")
                    break
            
            check_count += 1
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            current_output = get_current_price(w3, router_contract, amount_in_token_units, swap_path)
            
            if current_output is None:
                print(f"[{timestamp}] ⚠ Check #{check_count}: Could not fetch price, retrying...")
            else:
                current_price_human = current_output / (10 ** BUY_TOKEN_DECIMALS)
                print(f"[{timestamp}] Check #{check_count}: Current price = {current_price_human:.4f} tokens for {SELL_AMOUNT}")
                
                if current_output >= min_acceptable:
                    print(f"\n🎯 TARGET PRICE MET!")
                    print(f"   Current: {current_price_human:.4f}")
                    print(f"   Target: {TARGET_PRICE}")
                    print(f"   Executing order NOW...")
                    
                    bundle_hash = await execute_order(
                        w3, account, sell_token_contract, router_contract,
                        amount_in_token_units, min_acceptable, swap_path
                    )
                    
                    if bundle_hash:
                        was_executed = await track_bundle_status(bundle_hash)
                        
                        if was_executed:
                            print(f"\n✅ Trade completed! Monitor stopping.")
                            break
                        else:
                            print(f"\n⚠️ Bundle was not executed. Returning to price monitoring...")
                            print(f"   Will continue checking for better opportunities...")
                    else:
                        print(f"\n⚠️ Bundle submission failed, will keep monitoring...")
                else:
                    percentage = (current_price_human / TARGET_PRICE) * 100
                    print(f"   → Price is {percentage:.1f}% of target, waiting...")
            
            await asyncio.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print(f"\n\n⏹ Monitoring stopped by user")
        print(f"Total checks performed: {check_count}")


if __name__ == "__main__":
    asyncio.run(monitor_and_execute())

