# 🚀 Multi-Instance Limit Order Guide

Run 10 (or more!) limit order monitors simultaneously for different tokens.

---

## 📁 File Structure

```
titan_builder_script/
├── limit_order_multi.py      # Multi-instance compatible script
├── launcher.sh                # Manages all instances
├── configs/
│   ├── config_1.py           # First trading pair
│   ├── config_2.py           # Second trading pair
│   ├── config_3.py           # Add more as needed...
│   └── ...
├── logs/                      # Auto-created log files
│   ├── config_1.log
│   ├── config_2.log
│   └── ...
└── pids/                      # Auto-created PID files
    ├── config_1.pid
    └── ...
```

---

## 🎯 Quick Start

### 1. Create Your Config Files

Copy the template for each trading pair:

```bash
cd configs/
cp config_1.py config_3.py
cp config_1.py config_4.py
# ... up to config_10.py or more
```

Edit each config file with your trading pairs:

```python
# config_3.py
SELL_TOKEN = "0x..."          # Your sell token
BUY_TOKEN = "0x..."           # Your buy token
SELL_AMOUNT = 100
TARGET_PRICE = 500
# ... etc
```

### 2. Start All Instances

```bash
./launcher.sh start
```

Output:

```
==========================================
  Limit Order Multi-Instance Launcher
==========================================

Starting all configured instances...

✓  Starting instance: config_1
   PID: 12345
   Log: logs/config_1.log

✓  Starting instance: config_2
   PID: 12346
   Log: logs/config_2.log

==========================================
Started 2 instances
```

### 3. Check Status

```bash
./launcher.sh status
```

Output:

```
==========================================
  Instance Status
==========================================

✓ RUNNING  config_1 (PID: 12345)
✓ RUNNING  config_2 (PID: 12346)

Summary: 2 running, 0 stopped
```

### 4. View Logs (All at Once!)

```bash
./launcher.sh logs
```

This will show live logs from ALL instances simultaneously.

### 5. Stop All Instances

```bash
./launcher.sh stop
```

---

## 📋 Complete Command Reference

| Command                 | Description                     |
| ----------------------- | ------------------------------- |
| `./launcher.sh start`   | Start all configured instances  |
| `./launcher.sh stop`    | Stop all running instances      |
| `./launcher.sh restart` | Restart all instances           |
| `./launcher.sh status`  | Show status of all instances    |
| `./launcher.sh logs`    | Tail all log files in real-time |

---

## 📊 Managing Individual Instances

### Start One Instance Manually

```bash
python3 limit_order_multi.py configs/config_1.py
```

### View One Log File

```bash
tail -f logs/config_1.log
```

### Stop One Instance

```bash
# Find the PID
cat pids/config_1.pid

# Kill it
kill <PID>

# Or use the launcher
# (modify launcher.sh to accept config name)
```

---

## 💰 Important: Wallet Balance

**All instances use the SAME wallet (same private key).**

Make sure you have enough balance for ALL trades:

```
Total USDT needed = Sum of all SELL_AMOUNT in configs
Total ETH needed  = (Number of instances) × Gas costs
```

Example:

```
Config 1: 60 USDT
Config 2: 100 USDT
Config 3: 50 USDT
---
Total: 210 USDT needed in wallet
```

---

## 🔧 Advanced Configuration

### Run Different Configs from Different Wallets

Edit each config file to use different `PRIVATE_KEY`:

```python
# config_1.py
PRIVATE_KEY = "wallet1_key_here..."

# config_2.py
PRIVATE_KEY = "wallet2_key_here..."
```

### Adjust Check Intervals

For high-frequency monitoring:

```python
CHECK_INTERVAL = 1  # Check every 1 second
```

For low-frequency (battery saver):

```python
CHECK_INTERVAL = 10  # Check every 10 seconds
```

### Run More Than 10 Instances

Simply create more config files:

```bash
cp configs/config_1.py configs/config_11.py
cp configs/config_1.py configs/config_12.py
# ... etc
```

The launcher automatically detects ALL `config_*.py` files!

---

## 🐛 Troubleshooting

### Instance Won't Start

1. **Check if already running:**

   ```bash
   ./launcher.sh status
   ```

2. **Check the log file:**

   ```bash
   cat logs/config_1.log
   ```

3. **Common issues:**
   - Wrong token address
   - Insufficient balance
   - RPC endpoint down
   - Invalid private key

### Instance Stopped Unexpectedly

Check the log file for errors:

```bash
tail -n 50 logs/config_1.log
```

Common reasons:

- Max runtime exceeded
- Insufficient balance
- RPC connection lost
- Trade executed successfully

### Clean Up Stale PID Files

```bash
rm pids/*.pid
```

Then restart:

```bash
./launcher.sh start
```

---

## 📈 Performance

### Memory Usage (Per Instance)

- Each instance: ~25 MB RAM
- 10 instances: ~250 MB RAM
- Very lightweight! ✅

### CPU Usage (Per Instance)

- Each check: ~0.1 seconds
- Idle time: 95%+
- Can run 10+ instances on laptop ✅

### Network Usage

- Per instance: ~1 KB per check
- 10 instances: ~10 KB per check
- Minimal bandwidth! ✅

---

## 🎓 Example: Trading 10 Different Pairs

```bash
configs/
├── config_1.py   # USDT → BEST
├── config_2.py   # USDT → CHEX
├── config_3.py   # USDT → TokenA
├── config_4.py   # USDT → TokenB
├── config_5.py   # WETH → TokenC
├── config_6.py   # USDC → TokenD
├── config_7.py   # USDT → TokenE
├── config_8.py   # USDT → TokenF
├── config_9.py   # WETH → TokenG
└── config_10.py  # USDT → TokenH
```

Start all:

```bash
./launcher.sh start
```

Monitor all:

```bash
./launcher.sh status
./launcher.sh logs
```

---

## 🛡️ Security Tips

1. **Never commit config files with private keys to git:**

   ```bash
   echo "configs/*.py" >> .gitignore
   ```

2. **Use environment variables for keys:**

   ```python
   import os
   PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
   ```

3. **Set restrictive permissions:**
   ```bash
   chmod 600 configs/*.py
   ```

---

## 🎉 You're Ready!

Your multi-instance limit order system is now set up!

Key benefits:
✅ Monitor 10+ trading pairs simultaneously
✅ Each instance is independent
✅ Automatic bundle tracking
✅ Easy start/stop/monitor
✅ Lightweight and efficient
✅ All from one command!

Happy trading! 🚀
