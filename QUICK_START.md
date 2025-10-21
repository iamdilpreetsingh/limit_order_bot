# ⚡ Quick Start - Multi-Instance Trading

Run 10 simultaneous limit orders in under 2 minutes!

---

## 🎯 Step-by-Step (3 Simple Steps)

### 1️⃣ Create Configs (1 min)

```bash
cd configs/

# Copy template for each trading pair
cp config_1.py config_4.py
cp config_1.py config_5.py
# ... up to config_10.py

# Edit each file with your token addresses
nano config_4.py
```

**Edit these values:**

```python
BUY_TOKEN = "0x..."           # Your token address
SELL_AMOUNT = 100             # How much to sell
TARGET_PRICE = 500            # Minimum tokens to receive
BUY_TOKEN_DECIMALS = 18       # Check on Etherscan!
```

### 2️⃣ Start All (10 seconds)

**Option A: Bash (Mac/Linux)**

```bash
./launcher.sh start
```

**Option B: Python (All platforms)**

```bash
python3 launcher.py start
```

### 3️⃣ Monitor (anytime)

```bash
# Check status
./launcher.sh status

# View live logs
./launcher.sh logs

# Stop all
./launcher.sh stop
```

---

## 📊 What You'll See

### Starting:

```
==========================================
  Limit Order Multi-Instance Launcher
==========================================

✓  Starting instance: config_1
   PID: 12345
   Log: logs/config_1.log

✓  Starting instance: config_2
   PID: 12346
   Log: logs/config_2.log

Started 2 instances
```

### Status Check:

```
==========================================
  Instance Status
==========================================

✓ RUNNING  config_1 (PID: 12345)
✓ RUNNING  config_2 (PID: 12346)

Summary: 2 running, 0 stopped
```

### Live Logs:

```
[2025-10-20 18:30:15] Check #42: Current price = 98.64 BEST for 60 USDT
   → Price is 109.6% of target, waiting...

🎯 TARGET PRICE MET!
   Current: 98.64 BEST
   Target: 90 BEST
   Executing order NOW...

✅ Bundle submitted to Titan Builder!

🎉 SUCCESS! Your trade was EXECUTED on-chain!
```

---

## 🔧 All Commands

| Command                 | What it does           |
| ----------------------- | ---------------------- |
| `./launcher.sh start`   | Start all trading bots |
| `./launcher.sh stop`    | Stop all trading bots  |
| `./launcher.sh status`  | Show which are running |
| `./launcher.sh logs`    | Watch all logs live    |
| `./launcher.sh restart` | Restart everything     |

---

## 💡 Pro Tips

### Tip 1: Different Gas Prices

High priority trade:

```python
GAS_PRICE_GWEI = 100  # Fast inclusion
```

Low priority trade:

```python
GAS_PRICE_GWEI = 20   # Cheaper, slower
```

### Tip 2: Check Balances First

Make sure you have enough:

```
Total USDT = Sum of all SELL_AMOUNT
Total ETH = 0.01 ETH per instance (for gas)
```

### Tip 3: Test with Small Amounts

First time? Start with small amounts:

```python
SELL_AMOUNT = 10  # Test with $10 first
```

### Tip 4: Monitor One Instance

Watch just one bot:

```bash
tail -f logs/config_1.log
```

---

## ⚠️ Common Issues

### Issue: "No config files found"

**Solution:** Create config files in `configs/` folder:

```bash
cd configs/
ls config_*.py  # Should see config_1.py, config_2.py, etc.
```

### Issue: "Insufficient balance"

**Solution:** Check your wallet has enough:

- Tokens to sell (USDT, etc.)
- ETH for gas (~0.01 ETH per instance)

### Issue: "Instance already running"

**Solution:** Stop first, then start:

```bash
./launcher.sh stop
./launcher.sh start
```

### Issue: Bundle not executing

**Solution:** Increase gas price in config:

```python
GAS_PRICE_GWEI = 50  # or higher
```

---

## 📈 Example: 10 Trading Pairs

```
configs/config_1.py   →  60 USDT  → 90 BEST
configs/config_2.py   →  100 USDT → 2000 CHEX
configs/config_3.py   →  50 USDT  → 100 TokenA
configs/config_4.py   →  75 USDT  → 200 TokenB
configs/config_5.py   →  80 USDT  → 150 TokenC
configs/config_6.py   →  90 USDT  → 300 TokenD
configs/config_7.py   →  60 USDT  → 120 TokenE
configs/config_8.py   →  100 USDT → 250 TokenF
configs/config_9.py   →  50 USDT  → 80 TokenG
configs/config_10.py  →  70 USDT  → 180 TokenH
---
Total: 735 USDT needed in wallet
```

Start all at once:

```bash
./launcher.sh start
```

All 10 bots now monitoring 24/7! 🚀

---

## 🎉 You're Done!

Your multi-instance trading system is running!

**What happens next:**

1. ✅ Scripts monitor prices every 2 seconds
2. ✅ When target price met → Automatically executes
3. ✅ Bundle tracking confirms execution
4. ✅ You get notified in logs

**Relax and let the bots work!** ☕

---

## 📚 Need More Help?

- Full guide: `MULTI_INSTANCE_GUIDE.md`
- Original script: `limit_order_script.py`
- Multi-instance script: `limit_order_multi.py`
- Config examples: `configs/` folder

---

**Happy Trading!** 🎯
