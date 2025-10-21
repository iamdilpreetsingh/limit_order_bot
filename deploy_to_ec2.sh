#!/bin/bash

# ========================================
# EC2 Deployment Script for Titan Trading Bot
# ========================================
# This script helps deploy the Docker containers to EC2
# 
# Usage:
#   ./deploy_to_ec2.sh
#
# Prerequisites:
#   - EC2 instance running (Ubuntu 20.04+ or Amazon Linux 2)
#   - SSH access configured
#   - AWS credentials configured on EC2 (for Secrets Manager)

set -e  # Exit on any error

# ========================================
# Configuration - EDIT THESE VALUES
# ========================================

EC2_HOST="56.228.22.180"           # Your EC2 public IP or hostname
EC2_USER="ubuntu"                         # SSH user (ubuntu for Ubuntu, ec2-user for Amazon Linux)
SSH_KEY="~/.ssh/limit_order_bot.pem"            # Path to your SSH private key
REPO_URL="https://github.com/iamdilpreetsingh/limit_order_bot"             # Your GitHub repo URL
CONFIGS_BRANCH="configs"                  # Orphan branch with configs

# ========================================
# Colors for output
# ========================================
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=========================================="
echo "  Titan Trading Bot - EC2 Deployment"
echo "=========================================="
echo -e "${NC}"

# ========================================
# Step 1: Install Docker on EC2
# ========================================
echo -e "${GREEN}[1/6] Installing Docker on EC2...${NC}"

ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
    # Update system
    sudo apt-get update
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Add user to docker group (no need for sudo)
        sudo usermod -aG docker $USER
        echo "✅ Docker installed successfully"
    else
        echo "✅ Docker already installed"
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "Installing Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo "✅ Docker Compose installed successfully"
    else
        echo "✅ Docker Compose already installed"
    fi
EOF

echo -e "${GREEN}✅ Docker installation complete${NC}\n"

# ========================================
# Step 2: Install Git
# ========================================
echo -e "${GREEN}[2/6] Installing Git...${NC}"

ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
    if ! command -v git &> /dev/null; then
        sudo apt-get install -y git
        echo "✅ Git installed"
    else
        echo "✅ Git already installed"
    fi
EOF

echo -e "${GREEN}✅ Git installation complete${NC}\n"

# ========================================
# Step 3: Clone Main Repository
# ========================================
echo -e "${GREEN}[3/6] Cloning main repository...${NC}"

ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << EOF
    # Remove old directory if exists
    rm -rf ~/titan_trading_bot
    
    # Clone main branch
    git clone $REPO_URL ~/titan_trading_bot
    
    cd ~/titan_trading_bot
    echo "✅ Main repository cloned"
EOF

echo -e "${GREEN}✅ Repository cloned${NC}\n"

# ========================================
# Step 4: Clone Configs (Orphan Branch)
# ========================================
echo -e "${GREEN}[4/6] Cloning configs from orphan branch...${NC}"

ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << EOF
    cd ~/titan_trading_bot
    
    # Create configs directory
    mkdir -p configs
    
    # Clone configs from orphan branch
    cd configs
    git init
    git remote add origin $REPO_URL
    git fetch origin $CONFIGS_BRANCH
    git checkout $CONFIGS_BRANCH
    
    echo "✅ Configs loaded from orphan branch"
EOF

echo -e "${GREEN}✅ Configs loaded${NC}\n"

# ========================================
# Step 5: Configure AWS Credentials (if not already configured)
# ========================================
echo -e "${YELLOW}[5/6] AWS Configuration${NC}"
echo -e "${YELLOW}⚠️  Make sure AWS credentials are configured on EC2${NC}"
echo -e "${YELLOW}    Run this on EC2: aws configure${NC}"
echo -e "${YELLOW}    Or attach an IAM role with Secrets Manager permissions${NC}\n"

# ========================================
# Step 6: Build and Run Docker Containers
# ========================================
echo -e "${GREEN}[6/6] Building and starting Docker containers...${NC}"

ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
    cd ~/titan_trading_bot
    
    # Build Docker image
    echo "Building Docker image..."
    docker-compose build
    
    # Start all containers in detached mode
    echo "Starting containers..."
    docker-compose up -d
    
    echo ""
    echo "✅ All containers are running!"
    echo ""
    echo "Container status:"
    docker-compose ps
EOF

echo -e "${GREEN}=========================================="
echo -e "  🎉 Deployment Complete!"
echo -e "==========================================${NC}\n"

echo -e "${BLUE}Useful commands to run on EC2:${NC}"
echo -e "  ${YELLOW}View logs:${NC}           docker-compose logs -f"
echo -e "  ${YELLOW}View logs (specific):${NC} docker-compose logs -f trader-1"
echo -e "  ${YELLOW}Stop containers:${NC}      docker-compose stop"
echo -e "  ${YELLOW}Restart containers:${NC}   docker-compose restart"
echo -e "  ${YELLOW}Check status:${NC}         docker-compose ps"
echo -e "  ${YELLOW}Stop and remove:${NC}      docker-compose down"
echo ""

echo -e "${BLUE}To SSH into EC2:${NC}"
echo -e "  ssh -i $SSH_KEY $EC2_USER@$EC2_HOST"
echo ""

