# ✅ Deployment Checklist for AWS

## 🎯 Complete This Before Uploading Files

---

## Part 1: AWS Secrets Manager (5 minutes)

### ☐ **Step 1: Create Secret**

- [ ] Open AWS Console → Secrets Manager
- [ ] Store new secret: `limit-order-bot/wallet-key`
- [ ] Add key: `PRIVATE_KEY` = `your_actual_private_key`
- [ ] Copy the Secret ARN

### ☐ **Step 2: Create IAM Policy**

- [ ] Open IAM Console → Policies
- [ ] Create policy: `LimitOrderBotSecretsAccess`
- [ ] Use JSON from `SECRETS_QUICK_START.md`

### ☐ **Step 3: Create IAM Role**

- [ ] Open IAM Console → Roles
- [ ] Create role: `LimitOrderBotRole`
- [ ] Attach trusted entity: EC2
- [ ] Attach policy: `LimitOrderBotSecretsAccess`

### ☐ **Step 4: Attach Role to EC2**

- [ ] EC2 Console → Select instance
- [ ] Actions → Security → Modify IAM role
- [ ] Select: `LimitOrderBotRole`

### ☐ **Step 5: Verify Secret Access**

```bash
# On EC2:
aws secretsmanager get-secret-value \
  --secret-id limit-order-bot/wallet-key \
  --region us-east-1
```

- [ ] Secret retrieved successfully ✅

---

## Part 2: EC2 Setup (10 minutes)

### ☐ **Step 1: Connect to EC2**

```bash
ssh -i limit_order_bot.pem ubuntu@YOUR_EC2_IP
```

### ☐ **Step 2: Install Python 3.11**

```bash
sudo apt update -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.11 python3.11-venv git -y
```

### ☐ **Step 3: Verify Installation**

```bash
python3.11 --version
# Should show: Python 3.11.x
```

### ☐ **Step 4: Install pip for Python 3.11**

```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.11 get-pip.py
python3.11 -m pip --version
# Should show: pip 24.x from ... (python 3.11)
```

---

## Part 3: Bot Deployment (15 minutes)

### ☐ **Step 1: Create Directory**

```bash
mkdir ~/limit-order-bot
cd ~/limit-order-bot
```

### ☐ **Step 2: Create Virtual Environment**

```bash
python3.11 -m venv venv
source venv/bin/activate
# You should see (venv) in prompt
```

### ☐ **Step 3: Upload Files from Local Machine**

**On your LOCAL computer (new terminal):**

```bash
cd /Users/dilpreet/Local/titan_builder_script/
scp -i limit_order_bot.pem -r \
  limit_order_multi.py \
  launcher.py \
  launcher.sh \
  configs/ \
  requirements.txt \
  ubuntu@YOUR_EC2_IP:~/limit-order-bot/
```

### ☐ **Step 4: Verify Files Uploaded**

**Back on EC2:**

```bash
ls -la ~/limit-order-bot/
# Should see: limit_order_multi.py, launcher.py, configs/, etc.
```

### ☐ **Step 5: Install Python Dependencies**

```bash
cd ~/limit-order-bot/
source venv/bin/activate
pip install -r requirements.txt
```

Expected packages:

- [ ] web3
- [ ] eth-account
- [ ] requests
- [ ] pythereum
- [ ] boto3

### ☐ **Step 6: Test Single Bot**

```bash
python limit_order_multi.py configs/config_1.py
```

Expected output:

```
🔐 Fetching private key from AWS Secrets Manager...
✅ Private key loaded securely!
============================================================
🎯 LIMIT ORDER MONITOR - TITAN BUILDER
============================================================
...
```

- [ ] Private key loaded successfully ✅
- [ ] No errors ✅
- [ ] Press `Ctrl+C` to stop test

---

## Part 4: Start Bots (5 minutes)

### ☐ **Option A: Using Python Launcher**

```bash
python launcher.py start
python launcher.py status
python launcher.py logs 1
```

### ☐ **Option B: Using Bash Launcher**

```bash
chmod +x launcher.sh
./launcher.sh start
./launcher.sh status
./launcher.sh logs 1
```

---

## Part 5: Keep Bots Running 24/7

### ☐ **Using `screen` (Simple)**

```bash
screen -S trading-bots
cd ~/limit-order-bot
python launcher.py start

# Detach: Ctrl+A, then D
# Reattach: screen -r trading-bots
```

### ☐ **Using `systemd` (Advanced - Auto-restart on reboot)**

See `MULTI_INSTANCE_GUIDE.md` for systemd setup.

---

## 🔒 Security Checklist

- [ ] Private key stored in AWS Secrets Manager (NOT in code)
- [ ] IAM role attached to EC2 with minimal permissions
- [ ] Config files do NOT contain private keys
- [ ] `.gitignore` excludes sensitive files (if using Git)
- [ ] SSH key file (`limit_order_bot.pem`) has 400 permissions

---

## 🎉 Final Verification

### ☐ **All Bots Running**

```bash
./launcher.sh status
```

Expected:

```
Bot #1 (config_1.py): RUNNING (PID: 12345)
Bot #2 (config_2.py): RUNNING (PID: 12346)
Bot #3 (config_3.py): RUNNING (PID: 12347)
```

### ☐ **Check Logs**

```bash
./launcher.sh logs 1
```

Expected:

```
🔐 Fetching private key from AWS Secrets Manager...
✅ Private key loaded securely!
[timestamp] Check #1: Current price = ...
```

### ☐ **Disconnect SSH**

```bash
exit
```

### ☐ **Reconnect and Verify Bots Still Running**

```bash
ssh -i limit_order_bot.pem ubuntu@YOUR_EC2_IP
cd ~/limit-order-bot
./launcher.sh status
# All bots should still be RUNNING
```

---

## 🆘 Troubleshooting

### Problem: "AccessDeniedException" from Secrets Manager

**Fix:** IAM role not attached or wrong region

- Verify role is attached to EC2
- Check secret exists in same region as EC2

### Problem: "ModuleNotFoundError: No module named 'boto3'"

**Fix:** Virtual environment not activated

```bash
cd ~/limit-order-bot
source venv/bin/activate
pip install boto3
```

### Problem: Bot says "PRIVATE_KEY not found in config"

**Fix:** Script trying to load from config file

- Make sure you're using the UPDATED `limit_order_multi.py`
- Re-upload files from your local machine

### Problem: Bots stop when I disconnect SSH

**Fix:** Use `screen` or `systemd`

```bash
screen -S trading-bots
cd ~/limit-order-bot
python launcher.py start
# Press Ctrl+A, then D to detach
```

---

## 📊 Monitoring Your Bots

### **Check Status:**

```bash
./launcher.sh status
```

### **View Live Logs:**

```bash
./launcher.sh logs 1  # Bot 1
./launcher.sh logs 2  # Bot 2
```

### **Stop All Bots:**

```bash
./launcher.sh stop
```

### **Restart All Bots:**

```bash
./launcher.sh restart
```

---

## 💰 AWS Costs (Approximate)

| Service             | Cost         |
| ------------------- | ------------ |
| **EC2 t2.micro**    | ~$8.50/month |
| **Secrets Manager** | ~$0.40/month |
| **Data transfer**   | < $1/month   |
| **Total**           | ~$10/month   |

**Free Tier:** First 12 months, EC2 t2.micro is FREE (750 hours/month)

---

## ✅ You're Done!

Your limit order bots are now:

- 🔐 Securely storing private keys in AWS
- ☁️ Running 24/7 on a cloud server
- 🔄 Monitoring multiple trading pairs simultaneously
- 📊 Logging all activity for review

**Happy Trading! 🚀**
