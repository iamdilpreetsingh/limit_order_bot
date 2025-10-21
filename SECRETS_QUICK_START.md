# 🔐 Quick Start: AWS Secrets Manager

## 🎯 3-Minute Setup

---

## 1️⃣ **Create the Secret (2 minutes)**

### AWS Console → Secrets Manager → Store a new secret

| Field           | Value                          |
| --------------- | ------------------------------ |
| **Secret type** | Other type of secret           |
| **Key**         | `PRIVATE_KEY`                  |
| **Value**       | `your_wallet_private_key_here` |
| **Secret name** | `limit-order-bot/wallet-key`   |

**Click:** Next → Next → Store

✅ **Done!** Copy the ARN shown.

---

## 2️⃣ **Create IAM Policy (30 seconds)**

### IAM Console → Policies → Create policy → JSON tab

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

**Name:** `LimitOrderBotSecretsAccess`

**Click:** Create policy

✅ **Done!**

---

## 3️⃣ **Create IAM Role (30 seconds)**

### IAM Console → Roles → Create role

| Step               | Action                              |
| ------------------ | ----------------------------------- |
| **Trusted entity** | AWS service → EC2                   |
| **Policy**         | Select `LimitOrderBotSecretsAccess` |
| **Role name**      | `LimitOrderBotRole`                 |

**Click:** Create role

✅ **Done!**

---

## 4️⃣ **Attach Role to EC2 (15 seconds)**

### EC2 Console → Instances → Select your instance

**Actions** → **Security** → **Modify IAM role** → Select `LimitOrderBotRole` → **Update**

✅ **Done!**

---

## 5️⃣ **Test It (15 seconds)**

### SSH into your EC2:

```bash
aws secretsmanager get-secret-value \
  --secret-id limit-order-bot/wallet-key \
  --region us-east-1
```

**See your private key?** ✅ **Success!**

---

## 🎉 You're Ready!

Your bot will now:

- ✅ Automatically fetch the private key from AWS
- ✅ Never expose it in code or logs
- ✅ Keep your funds safe

**Next:** Upload bot files and start trading! 🚀
