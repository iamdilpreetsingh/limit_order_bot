# Titan Builder Scripts - Documentation

## 📋 Overview

This directory contains scripts for trading on Uniswap using Titan Builder for private transaction submission.

## 🚨 CRITICAL DIFFERENCES

### `script.py` - IMMEDIATE EXECUTION

**⚡ Executes trades RIGHT NOW!**

- Builds and signs transactions immediately
- Submits to Titan Builder for next block inclusion (~12 seconds)
- **Consumes gas whether it succeeds or fails**
- Use this when you want to execute a swap immediately

**Gas Cost:** Paid every time you run it, even if the trade fails!

---

### `limit_order_script.py` - WAIT FOR PRICE (RECOMMENDED)

**🎯 Only executes when your price target is met!**

- Monitors price every N seconds (configurable)
- Only submits bundle when price conditions are favorable
- **Only consumes gas when actually executing**
- Prevents wasting ETH on failed transactions

**Gas Cost:** Only paid once, when your target price is reached!

---

## 🔧 Configuration

### For Limit Orders (`limit_order_script.py`):

```python
# Key settings to configure:
TARGET_PRICE = 25000        # Get at least 25,000 CHEX for 100 USDT
CHECK_INTERVAL = 30         # Check price every 30 seconds
MAX_SLIPPAGE_PERCENT = 2    # Allow 2% slippage
GAS_PRICE_GWEI = 20         # Gas price (lower = cheaper, slower)
```

### How to Use:

1. **Edit the configuration** in `limit_order_script.py`:

   - Set your `TARGET_PRICE`
   - Set how often to check (`CHECK_INTERVAL`)
   - Set acceptable slippage

2. **Run the script**:

   ```bash
   python3 limit_order_script.py
   ```

3. **Monitor the output**:
   - It will check price every 30 seconds
   - Shows current price vs target
   - Automatically executes when target is met
   - Press Ctrl+C to stop monitoring

---

## 💡 How It Works

### Limit Order Flow:

1. **Monitoring Phase** (No gas cost):

   - Checks Uniswap price every N seconds
   - Compares current price to your target
   - Waits until conditions are met

2. **Execution Phase** (Gas cost incurred):

   - Price target reached!
   - Builds approve + swap transactions
   - Runs final simulation to ensure success
   - Submits bundle to Titan Builder
   - Bundle executes in next block

3. **Result**:
   - ✅ Bundle hash returned
   - 🎉 Your swap executes on-chain
   - 💰 You only paid gas once!

---

## ⚠️ Important Notes

### Why Your ETH Was Being "Exhausted":

The old `script.py` executes immediately every time you run it. If the transaction fails on-chain (due to liquidity, slippage, or other issues), you still pay gas fees!

**Problem:**

- Run script → Pay gas → Transaction fails → Lost ~$20 in gas
- Run again → Pay gas → Fails again → Lost another ~$20
- Result: ETH exhausted with no successful trades!

**Solution:**
Use `limit_order_script.py` which:

- Checks price off-chain (free)
- Only submits when conditions are optimal
- Simulates before submitting
- Only consumes gas on successful execution

### Gas Fees Explained:

- **Monitoring:** FREE (just reading blockchain data)
- **Simulation:** FREE (eth_call doesn't cost gas)
- **Execution:** COSTS GAS (~0.004-0.01 ETH)

You only pay gas when the bundle actually executes!

---

## 🛡️ Safety Features

The limit order script includes:

1. ✅ **Balance checks** - Verifies you have enough tokens and ETH
2. ✅ **Price monitoring** - Only executes at favorable prices
3. ✅ **Simulation** - Tests transaction before submission
4. ✅ **Slippage protection** - Won't execute if price moves unfavorably
5. ✅ **Allowance checking** - Only approves if needed (saves gas)

---

## 📊 Example Output

```
🎯 LIMIT ORDER MONITOR - TITAN BUILDER
============================================================
Account: 0x1234...
Selling: 100 USDT
Buying: CHEX
Target: At least 25000 CHEX
Checking every: 30 seconds
============================================================

[2025-10-19 15:30:00] Check #1: Current price = 22000 CHEX for 100 USDT
   → Price is 88.0% of target, waiting...

[2025-10-19 15:30:30] Check #2: Current price = 23500 CHEX for 100 USDT
   → Price is 94.0% of target, waiting...

[2025-10-19 15:31:00] Check #3: Current price = 25200 CHEX for 100 USDT

🎯 TARGET PRICE MET!
   Current: 25200 CHEX
   Target: 25000 CHEX
   Executing order NOW...

⚡ EXECUTING ORDER
============================================================
✓ Building swap transaction...
🔍 Final simulation check...
✓ Swap simulation: SUCCESS
📤 Sending bundle to Titan Builder...
✅ SUCCESS! Bundle submitted: {'bundleHash': '0x...'}

🎉 Your order is being executed!
```

---

## 🔐 Security

- Never share your `PRIVATE_KEY`
- Consider using environment variables instead of hardcoding keys
- Test with small amounts first
- Always verify contract addresses

---

## 📞 Support

If you encounter issues:

1. Check your ETH balance (need ~0.01 ETH for gas)
2. Verify token balance (need sufficient USDT)
3. Check if liquidity exists for your token pair
4. Try lowering your target price
5. Increase slippage tolerance

---

## 🎯 Recommendations

For most users, **use `limit_order_script.py`** because:

- ✅ Saves gas fees
- ✅ Better price execution
- ✅ Set and forget
- ✅ No manual monitoring needed
- ✅ Safety checks prevent failed transactions

Only use `script.py` if you need immediate execution regardless of price.
