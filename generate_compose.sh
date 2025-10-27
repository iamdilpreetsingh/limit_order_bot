#!/bin/bash

# ========================================
# Auto-Generate docker-compose.yml
# ========================================
# This script automatically creates docker-compose.yml
# based on the number of config_*.py files in configs/

echo "🔧 Generating docker-compose.yml from configs..."

# Start docker-compose file
cat > docker-compose.yml <<'HEADER'
version: '3.8'

services:
HEADER

# Find all config files and create services
config_count=0
for config in configs/config_*.py; do
  if [ -f "$config" ]; then
    config_count=$((config_count + 1))
    # Extract number from config_N.py
    config_name=$(basename "$config" .py)
    trader_num=$(echo "$config_name" | sed 's/config_//')
    
    echo "  ✓ Found: $config_name → Creating trader-$trader_num"
    
    # Add service to docker-compose.yml
    cat >> docker-compose.yml <<EOF
  # ========================================
  # Trading Bot Instance $trader_num ($config_name.py)
  # ========================================
  trader-$trader_num:
    build: .
    container_name: titan-trader-$trader_num
    restart: unless-stopped
    environment:
      - CONFIG_FILE=/app/configs/$config_name.py
      - AWS_DEFAULT_REGION=eu-north-1
    volumes:
      - ./configs:/app/configs:ro
    networks:
      - trading-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

EOF
  fi
done

# Add networks section
cat >> docker-compose.yml <<'FOOTER'
# ========================================
# Network Configuration
# ========================================
networks:
  trading-network:
    driver: bridge
FOOTER

echo ""
echo "✅ Generated docker-compose.yml with $config_count trader(s)"
echo ""
echo "📋 Services created:"
for config in configs/config_*.py; do
  if [ -f "$config" ]; then
    config_name=$(basename "$config" .py)
    trader_num=$(echo "$config_name" | sed 's/config_//')
    echo "   - trader-$trader_num → $config_name.py"
  fi
done
echo ""
echo "🚀 Ready to deploy! Run: docker-compose up -d"

