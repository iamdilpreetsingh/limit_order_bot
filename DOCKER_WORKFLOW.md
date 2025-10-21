# 🐳 Complete Docker Workflow - Step by Step

This guide explains the complete workflow from development to production deployment.

---

## 🎯 Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Development    │  →   │  Test Locally    │  →   │  Deploy to EC2  │
│  (Your Machine) │      │  (Docker)        │      │  (Production)   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

---

## Phase 1: Development (Your Machine)

### 1.1 Code Structure

**Main Branch** (public-facing code):

```
titan_builder_script/
├── limit_order_script.py    # Trading bot
├── Dockerfile               # Image definition
├── docker-compose.yml       # Container orchestration
├── deploy_to_ec2.sh        # Deployment automation
├── requirements.txt         # Dependencies
└── .gitignore              # Ignore configs/
```

**Configs Branch** (orphan, separate history):

```
configs/
├── config_1.py
├── config_2.py
└── config_3.py
```

### 1.2 Git Branch Setup

```bash
# Main branch (code)
git checkout main
git add Dockerfile docker-compose.yml limit_order_script.py
git commit -m "Add Docker support"
git push origin main

# Configs branch (orphan)
git checkout --orphan configs
git rm -rf .
git add configs/
git commit -m "Initial configs"
git push origin configs

# Switch back
git checkout main
```

**Result:** Two independent branches with no shared history!

---

## Phase 2: Local Testing with Docker

### 2.1 Pull Configs Locally

```bash
# In your project directory
mkdir -p configs
cd configs

# Clone orphan branch into configs/
git init
git remote add origin <your-repo-url>
git fetch origin configs
git checkout configs

cd ..
```

### 2.2 Build Docker Image

```bash
# Build the image
docker-compose build

# What happens:
# 1. Docker reads Dockerfile
# 2. Downloads Python 3.13 base image
# 3. Installs requirements.txt dependencies
# 4. Copies limit_order_script.py
# 5. Creates image: ~500MB
```

**Docker Image = Blueprint (like a VM snapshot)**

### 2.3 Start Containers

```bash
# Start all containers defined in docker-compose.yml
docker-compose up -d

# This creates 3 containers:
# - titan-trader-1 (with config_1.py)
# - titan-trader-2 (with config_2.py)
# - titan-trader-3 (with config_3.py)
```

**Docker Container = Running instance of image**

### 2.4 Monitor

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# View specific container
docker-compose logs -f trader-1

# Check resource usage
docker stats
```

### 2.5 Test & Iterate

```bash
# Make changes to limit_order_script.py
# Rebuild and restart
docker-compose up -d --build

# Update config
# Just restart (no rebuild needed)
docker-compose restart
```

### 2.6 Stop Testing

```bash
# Stop containers
docker-compose stop

# Or stop and remove
docker-compose down
```

---

## Phase 3: Deploy to EC2

### 3.1 Prerequisites

- [ ] AWS account
- [ ] EC2 instance launched (t3.micro, Ubuntu 20.04)
- [ ] SSH key pair downloaded
- [ ] Security group allows SSH (port 22)
- [ ] IAM role with Secrets Manager permissions attached

### 3.2 Configure Deployment Script

Edit `deploy_to_ec2.sh`:

```bash
EC2_HOST="52.123.456.789"  # Your EC2 public IP
EC2_USER="ubuntu"
SSH_KEY="~/.ssh/my-key.pem"
REPO_URL="https://github.com/yourusername/repo.git"
CONFIGS_BRANCH="configs"
```

### 3.3 Run Deployment

```bash
chmod +x deploy_to_ec2.sh
./deploy_to_ec2.sh
```

**What the script does:**

1. ✅ SSH into EC2
2. ✅ Install Docker + Docker Compose
3. ✅ Install Git
4. ✅ Clone main branch → `~/titan_trading_bot/`
5. ✅ Clone configs branch → `~/titan_trading_bot/configs/`
6. ✅ Build Docker image on EC2
7. ✅ Start all containers with `docker-compose up -d`

### 3.4 Verify Deployment

```bash
# SSH into EC2
ssh -i ~/.ssh/my-key.pem ubuntu@52.123.456.789

# Check containers
cd ~/titan_trading_bot
docker-compose ps

# Should see:
# NAME              STATUS
# titan-trader-1    Up
# titan-trader-2    Up
# titan-trader-3    Up

# View logs
docker-compose logs -f
```

---

## Phase 4: Production Operations

### 4.1 Monitoring

```bash
# SSH into EC2
ssh -i ~/.ssh/my-key.pem ubuntu@your-ec2-ip

# View all logs
docker-compose logs -f

# View specific trader
docker-compose logs -f trader-1

# Check resource usage
docker stats

# Check disk space
df -h
```

### 4.2 Updates

**Update Code:**

```bash
# On your machine
git add limit_order_script.py
git commit -m "Fix bug"
git push origin main

# On EC2
cd ~/titan_trading_bot
git pull origin main
docker-compose up -d --build  # Rebuild image
```

**Update Config:**

```bash
# On your machine (in configs/)
cd configs
git add config_1.py
git commit -m "Update target price"
git push origin configs

# On EC2
cd ~/titan_trading_bot/configs
git pull origin configs
cd ..
docker-compose restart trader-1  # Just restart
```

### 4.3 Scaling

**Add a 4th trader:**

1. Create `config_4.py` in configs branch
2. Edit `docker-compose.yml` on main branch:

```yaml
trader-4:
  build: .
  container_name: titan-trader-4
  restart: unless-stopped
  environment:
    - CONFIG_FILE=/app/configs/config_4.py
  volumes:
    - ./configs:/app/configs:ro
  networks:
    - trading-network
```

3. Deploy:

```bash
git push origin main
# On EC2
git pull origin main
docker-compose up -d trader-4
```

### 4.4 Troubleshooting

```bash
# Container not starting?
docker-compose logs trader-1

# Container using too much memory?
docker stats

# Need to enter container?
docker exec -it titan-trader-1 /bin/bash

# Start fresh?
docker-compose down
docker-compose up -d --build
```

---

## 🔄 Daily Workflow

### Morning Check

```bash
ssh -i ~/.ssh/key.pem ubuntu@your-ec2-ip
cd ~/titan_trading_bot

# Quick status
docker-compose ps

# Any errors?
docker-compose logs --tail=50

# Resource usage OK?
docker stats --no-stream
```

### Make Updates

```bash
# 1. Local: Edit code/configs
# 2. Local: git commit + push
# 3. EC2: git pull + restart/rebuild
```

### Evening Check

```bash
# Check logs for completed trades
docker-compose logs | grep "SUCCESS"

# Check if any containers restarted
docker-compose ps
```

---

## 🎓 Docker Concepts Recap

| Concept                | What It Is              | Example                       |
| ---------------------- | ----------------------- | ----------------------------- |
| **Dockerfile**         | Recipe to build image   | "Install Python, copy script" |
| **Image**              | Snapshot/template       | Ubuntu + Python + your code   |
| **Container**          | Running instance        | Your bot executing trades     |
| **docker-compose.yml** | Orchestrator            | Manages 3 traders at once     |
| **Volume**             | Shared folder           | Mount configs/ into container |
| **Network**            | Container communication | Traders share network         |

---

## 📊 Cost Breakdown

### AWS Costs (Monthly Estimate)

| Resource            | Cost           |
| ------------------- | -------------- |
| EC2 t3.micro (24/7) | ~$7.50         |
| Storage (20GB)      | ~$2.00         |
| Data Transfer       | ~$0.50         |
| **Total**           | **~$10/month** |

**Compare to:**

- 3 separate EC2 instances = ~$22.50/month
- VPS alternatives = $15-20/month

**Docker saves you money!** 💰

---

## 🛡️ Security Best Practices

1. ✅ **Never commit private keys** (use AWS Secrets Manager)
2. ✅ **Keep configs in orphan branch** (separate from code)
3. ✅ **Use read-only volumes** (`:ro` flag)
4. ✅ **Limit container resources** (prevents memory overflow)
5. ✅ **Regular security updates** (`sudo apt update && sudo apt upgrade`)
6. ✅ **Monitor logs** (catch suspicious activity)

---

## 📞 Getting Help

### Quick Checks

1. **Container not starting?**

   - Check logs: `docker-compose logs trader-1`
   - Check config file exists: `ls -la configs/`

2. **Out of memory?**

   - Check usage: `docker stats`
   - Reduce number of containers

3. **Can't connect to EC2?**
   - Check security group
   - Verify SSH key permissions: `chmod 400 key.pem`

### Resources

- [Docker Documentation](https://docs.docker.com)
- [AWS EC2 Guide](https://docs.aws.amazon.com/ec2)
- [Docker Compose Reference](https://docs.docker.com/compose)

---

## 🎯 Summary

```
┌─────────────────────────────────────────────────────────┐
│  1. Code in main branch                                 │
│  2. Configs in orphan branch                            │
│  3. Test locally with docker-compose                    │
│  4. Deploy to EC2 with deploy_to_ec2.sh                 │
│  5. Monitor with docker-compose logs                    │
│  6. Update: git pull + restart/rebuild                  │
└─────────────────────────────────────────────────────────┘
```

**That's it!** You now have a production-ready, scalable trading bot infrastructure! 🚀

---

**Happy Trading! 💰**
