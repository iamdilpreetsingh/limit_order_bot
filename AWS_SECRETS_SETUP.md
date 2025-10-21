# 🔐 AWS Secrets Manager Setup Guide

## ⚠️ CRITICAL: Protect Your Private Key!

**NEVER** hardcode your private key in config files! This guide shows you how to store it securely in AWS Secrets Manager.

---

## 📋 Setup Steps

### **Step 1: Create Secret in AWS Secrets Manager**

1. **Open AWS Console** → Search for **"Secrets Manager"**
2. Click **"Store a new secret"**

3. **Configure the secret:**

   - **Secret type:** Other type of secret
   - **Key/value pairs:**
     - Key: `PRIVATE_KEY`
     - Value: `your_actual_private_key_here` (paste your wallet's private key)
   - Click **Next**

4. **Name your secret:**

   - **Secret name:** `limit-order-bot/wallet-key`
   - **Description:** Private key for limit order trading bot
   - Click **Next** → **Next** → **Store**

5. **Copy the Secret ARN:**
   - You'll see something like:
     ```
     arn:aws:secretsmanager:us-east-1:123456789012:secret:limit-order-bot/wallet-key-AbCdEf
     ```
   - **Save this ARN** - you'll need it in the next step!

---

### **Step 2: Create IAM Policy for Secrets Access**

1. **Go to IAM Console** → **Policies** → **Create policy**

2. **Click the JSON tab** and paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:limit-order-bot/*"
    }
  ]
}
```

3. **Name the policy:**
   - Policy name: `LimitOrderBotSecretsAccess`
   - Description: Allows EC2 to read limit order bot secrets
   - Click **Create policy**

---

### **Step 3: Create IAM Role for EC2**

1. **Go to IAM Console** → **Roles** → **Create role**

2. **Select trusted entity:**

   - **Trusted entity type:** AWS service
   - **Use case:** EC2
   - Click **Next**

3. **Attach permissions policy:**

   - Search for `LimitOrderBotSecretsAccess`
   - Check the box next to it
   - Click **Next**

4. **Name the role:**
   - Role name: `LimitOrderBotRole`
   - Description: Role for limit order bot EC2 instance
   - Click **Create role**

---

### **Step 4: Attach IAM Role to Your EC2 Instance**

1. **Go to EC2 Console** → **Instances**
2. **Select your instance** (the one you created earlier)
3. Click **Actions** → **Security** → **Modify IAM role**
4. **Select:** `LimitOrderBotRole`
5. Click **Update IAM role**

---

## ✅ Verification

### **Test on EC2 Instance:**

```bash
# SSH into your instance
ssh -i limit_order_bot.pem ubuntu@YOUR_EC2_IP

# Install AWS CLI (if not already installed)
sudo apt install awscli -y

# Test secret retrieval
aws secretsmanager get-secret-value \
  --secret-id limit-order-bot/wallet-key \
  --region us-east-1
```

**Expected output:**

```json
{
  "ARN": "arn:aws:secretsmanager:us-east-1:...",
  "Name": "limit-order-bot/wallet-key",
  "SecretString": "{\"PRIVATE_KEY\":\"your_key_here\"}"
}
```

---

## 🐍 Bot Configuration

### **Updated `limit_order_multi.py`:**

✅ **Already done!** The bot now:

- Fetches `PRIVATE_KEY` from AWS Secrets Manager automatically
- Shows clear error messages if secret retrieval fails
- Never stores the private key in code

### **Updated Config Files:**

✅ **Already done!** Config files (like `config_1.py`) now:

- **DO NOT** contain `PRIVATE_KEY` anymore
- Have a comment explaining the key is in Secrets Manager

---

## 📦 Required Python Package

The bot needs `boto3` to access AWS Secrets Manager:

```bash
# On your EC2 instance:
source venv/bin/activate
pip install boto3
```

**Updated requirements.txt:**

```
web3
eth-account
requests
pythereum
boto3
```

---

## 🔒 Security Best Practices

### ✅ DO:

- Store private keys in AWS Secrets Manager
- Use IAM roles with least-privilege permissions
- Rotate your private key periodically
- Enable CloudTrail to audit secret access

### ❌ DON'T:

- Hardcode private keys in code or config files
- Commit private keys to Git
- Share private keys via email/Slack/etc
- Use the same private key for multiple bots (if possible)

---

## 💰 Pricing

**AWS Secrets Manager costs:**

- $0.40 per secret per month
- $0.05 per 10,000 API calls

**For 1 secret with occasional access:**

- ~$0.40/month (practically free!)

---

## 🆘 Troubleshooting

### Error: "UnrecognizedClientException"

**Fix:** Your EC2 region doesn't match the secret region

- Make sure your secret is in the same region as your EC2
- Or update `region_name` in the bot script

### Error: "AccessDeniedException"

**Fix:** IAM role is not attached or doesn't have permission

- Verify IAM role is attached to EC2 instance
- Check the policy allows `secretsmanager:GetSecretValue`

### Error: "ResourceNotFoundException"

**Fix:** Secret name is wrong

- Verify the secret is named exactly: `limit-order-bot/wallet-key`
- Check you're in the correct AWS region

---

## 🎉 You're Done!

Your private key is now:

- ✅ Encrypted at rest in AWS
- ✅ Never stored in code
- ✅ Accessible only to your EC2 instance
- ✅ Auditable via CloudTrail

**You can now safely upload your bot files to the server!**
