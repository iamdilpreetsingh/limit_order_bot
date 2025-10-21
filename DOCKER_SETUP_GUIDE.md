# 🐳 Docker Deployment Guide - Titan Trading Bot

This guide walks you through deploying multiple trading bot instances using Docker on AWS EC2.

---

## 📚 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Setup Orphan Branch (Configs)](#setup-orphan-branch-configs)
4. [Local Testing](#local-testing)
5. [Deploy to EC2](#deploy-to-ec2)
6. [Managing Containers](#managing-containers)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│         EC2 t3.micro Instance           │
│  ┌───────────────────────────────────┐  │
│  │  Docker Engine                    │  │
│  │  ┌─────────────┐  ┌────────────┐ │  │
│  │  │ Container 1 │  │Container 2 │ │  │
│  │  │  config_1   │  │  config_2  │ │  │
│  │  └─────────────┘  └────────────┘ │  │
│  │  ┌─────────────┐                 │  │
│  │  │ Container 3 │                 │  │
│  │  │  config_3   │                 │  │
│  │  └─────────────┘                 │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Benefits:**

- ✅ One EC2 instance = lower cost
- ✅ Isolated containers per trading strategy
- ✅ Easy scaling (add more containers)
- ✅ Automatic restarts on crashes
- ✅ Centralized logging

---

## ✅ Prerequisites

### On Your Local Machine:

- [ ] Git installed
- [ ] Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- [ ] Docker Compose installed (comes with Docker Desktop)
- [ ] SSH key for EC2 access

### On AWS:

- [ ] EC2 t3.micro instance running (Ubuntu 20.04+ or Amazon Linux 2)
- [ ] Security Group allows SSH (port 22)
- [ ] IAM role attached with Secrets Manager permissions
- [ ] AWS Secrets Manager configured with your wallet key

---

## 🔐 Setup Orphan Branch (Configs)

**Orphan branch = separate Git history, perfect for sensitive configs!**

### Step 1: Create Orphan Branch

```bash
# Navigate to your repo
cd /Users/dilpreet/Local/titan_builder_script

# Create orphan branch (no history, clean slate)
git checkout --orphan configs

# Remove all files from staging (we start fresh)
git rm -rf .

# Only keep config files
git add configs/
git add -f configs/config_1.py
git add -f configs/config_2.py
git add -f configs/config_3.py

# Optionally add a README for the configs branch
echo "# Trading Bot Configurations" > README.md
echo "This branch contains private trading configurations." >> README.md
git add README.md

# Commit
git commit -m "Initial configs"

# Push to remote (creates new branch)
git push origin configs

# Switch back to main branch
git checkout main
```

### Step 2: Verify Orphan Branch

```bash
# Check branches
git branch -a

# Should see:
# * main
#   remotes/origin/configs
#   remotes/origin/main

# Verify configs branch has no shared history
git log --oneline --graph --all --decorate
```

### Step 3: Keep Main Branch Clean

In your `main` branch, add configs to `.gitignore`:

```bash
# On main branch
echo "configs/" >> .gitignore
git add .gitignore
git commit -m "Ignore configs directory"
git push origin main
```

**Result:**

- Main branch = code + Dockerfile + docker-compose.yml
- Configs branch = only config files (separate history)

---

## 🧪 Local Testing

Before deploying to EC2, test locally!

### Step 1: Pull Configs Locally

```bash
# In your project directory
mkdir -p configs
cd configs

# Initialize git in configs folder
git init
git remote add origin <your-repo-url>
git fetch origin configs
git checkout configs

cd ..
```

### Step 2: Build Docker Image

```bash
# Build the image
docker-compose build

# This creates an image with:
# - Python 3.13
# - All dependencies from requirements.txt
# - Your trading script
```

### Step 3: Start Containers

```bash
# Start all containers in background (-d = detached)
docker-compose up -d

# View status
docker-compose ps

# Expected output:
# NAME              IMAGE         STATUS        PORTS
# titan-trader-1    ...           Up 2 seconds
# titan-trader-2    ...           Up 2 seconds
# titan-trader-3    ...           Up 2 seconds
```

### Step 4: View Logs

```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f trader-1

# Last 100 lines
docker-compose logs --tail=100 trader-1
```

### Step 5: Stop Containers

```bash
# Stop all
docker-compose stop

# Stop specific
docker-compose stop trader-1

# Stop and remove containers
docker-compose down
```

---

## 🚀 Deploy to EC2

### Step 1: Launch EC2 Instance

1. **Go to AWS Console** → EC2
2. **Launch Instance**
   - AMI: Ubuntu Server 20.04 LTS
   - Instance Type: t3.micro
   - Storage: 20 GB GP3
   - Security Group: Allow SSH (port 22) from your IP
3. **Create/Select Key Pair** (download `.pem` file)
4. **Attach IAM Role** with Secrets Manager permissions

### Step 2: Configure Deployment Script

Edit `deploy_to_ec2.sh`:

```bash
# Open in editor
nano deploy_to_ec2.sh

# Update these values:
EC2_HOST="your-ec2-public-ip"
EC2_USER="ubuntu"
SSH_KEY="~/.ssh/your-key.pem"
REPO_URL="https://github.com/yourusername/your-repo.git"
```

### Step 3: Run Deployment

```bash
# Make executable (if not already)
chmod +x deploy_to_ec2.sh

# Deploy!
./deploy_to_ec2.sh
```

The script will:

1. ✅ Install Docker on EC2
2. ✅ Install Git
3. ✅ Clone main repo
4. ✅ Clone configs from orphan branch
5. ✅ Build Docker image
6. ✅ Start all containers

### Step 4: Verify Deployment

```bash
# SSH into EC2
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip

# Check containers
docker-compose ps

# View logs
docker-compose logs -f
```

---

## 🛠️ Managing Containers

### Common Commands (Run on EC2)

```bash
# SSH into EC2 first
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip
cd ~/titan_trading_bot

# View container status
docker-compose ps

# View all logs
docker-compose logs -f

# View specific container logs
docker-compose logs -f trader-1

# Restart all containers
docker-compose restart

# Restart specific container
docker-compose restart trader-1

# Stop all containers
docker-compose stop

# Start all containers
docker-compose start

# Stop and remove containers (keeps data)
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Rebuild image (after code changes)
docker-compose build

# Rebuild and restart
docker-compose up -d --build
```

### View Container Resource Usage

```bash
# Real-time stats
docker stats

# Shows CPU, memory, network for each container
```

### Access Container Shell (for debugging)

```bash
# Enter container
docker exec -it titan-trader-1 /bin/bash

# Inside container, you can:
# - Check files: ls -la
# - View env variables: env
# - Run Python: python
# - Exit: exit
```

---

## 🔄 Updating Code or Configs

### Update Main Script

```bash
# On your local machine
git add limit_order_script.py
git commit -m "Update trading logic"
git push origin main

# On EC2
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip
cd ~/titan_trading_bot
git pull origin main
docker-compose up -d --build  # Rebuild and restart
```

### Update Configs

```bash
# On your local machine (in configs directory)
cd configs
git add config_1.py
git commit -m "Update config 1"
git push origin configs

# On EC2
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip
cd ~/titan_trading_bot/configs
git pull origin configs
cd ..
docker-compose restart  # Just restart, no rebuild needed
```

---

## 🚨 Troubleshooting

### Container Keeps Restarting

```bash
# Check logs
docker-compose logs trader-1

# Common issues:
# - Config file not found → Check CONFIG_FILE path
# - AWS credentials missing → Configure aws cli
# - Python error → Check requirements.txt
```

### Out of Memory

```bash
# Check memory usage
free -h

# Solution: Reduce number of containers or upgrade EC2 instance
```

### Can't Connect to EC2

```bash
# Check security group allows your IP
# Check SSH key permissions
chmod 400 ~/.ssh/your-key.pem
```

### Docker Build Fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Container Logs Not Showing

```bash
# Check if container is running
docker-compose ps

# If exited, check exit code
docker-compose ps -a

# View last exit logs
docker logs titan-trader-1
```

---

## 📊 Monitoring

### View Logs in Real-Time

```bash
# Follow all logs
docker-compose logs -f

# Follow specific trader
docker-compose logs -f trader-1
```

### Check Container Health

```bash
# List running containers
docker ps

# Container stats (CPU, RAM, Network)
docker stats
```

### Set Up Alerts (Optional)

Consider using:

- **AWS CloudWatch** for EC2 monitoring
- **Docker monitoring tools** like Portainer
- **Log aggregation** with ELK stack

---

## 🎓 Docker Concepts Recap

| Concept                | Analogy             | Purpose                     |
| ---------------------- | ------------------- | --------------------------- |
| **Image**              | Blueprint           | Template for containers     |
| **Container**          | Running instance    | Isolated process            |
| **Dockerfile**         | Recipe              | Instructions to build image |
| **docker-compose.yml** | Orchestra conductor | Manages multiple containers |
| **Volume**             | External hard drive | Persistent storage          |
| **Network**            | Private LAN         | Container communication     |

---

## 📞 Need Help?

- Docker docs: https://docs.docker.com
- Docker Compose docs: https://docs.docker.com/compose
- AWS EC2 docs: https://docs.aws.amazon.com/ec2

---

**Happy Trading! 🚀**
