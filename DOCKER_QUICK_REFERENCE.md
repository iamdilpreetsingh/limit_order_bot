# 🐳 Docker Quick Reference Card

Quick commands for managing your Titan Trading Bot containers.

---

## 🚀 Deployment

```bash
# Test locally first
docker-compose up -d

# Deploy to EC2
./deploy_to_ec2.sh
```

---

## 📊 Monitoring

```bash
# View all container status
docker-compose ps

# View all logs (live)
docker-compose logs -f

# View specific container logs
docker-compose logs -f trader-1

# Last 100 lines
docker-compose logs --tail=100 trader-1

# Resource usage (CPU, RAM, Network)
docker stats
```

---

## 🎮 Control

```bash
# Start all containers
docker-compose start

# Stop all containers
docker-compose stop

# Restart all containers
docker-compose restart

# Restart specific container
docker-compose restart trader-1

# Stop and remove containers
docker-compose down

# Force rebuild and restart
docker-compose up -d --build
```

---

## 🔧 Debugging

```bash
# Enter container shell
docker exec -it titan-trader-1 /bin/bash

# Inside container:
ls -la              # List files
env                 # View environment variables
python              # Run Python
exit                # Exit container

# View container details
docker inspect titan-trader-1

# Check Docker disk usage
docker system df
```

---

## 🧹 Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything unused
docker system prune -a

# Remove volumes (WARNING: deletes data)
docker volume prune
```

---

## 🔄 Updates

### Update Main Script

```bash
# On local machine
git add limit_order_script.py
git commit -m "Update trading logic"
git push origin main

# On EC2
ssh -i ~/.ssh/key.pem ubuntu@your-ec2-ip
cd ~/titan_trading_bot
git pull origin main
docker-compose up -d --build
```

### Update Configs

```bash
# On local machine (in configs/)
cd configs
git add config_1.py
git commit -m "Update config"
git push origin configs

# On EC2
ssh -i ~/.ssh/key.pem ubuntu@your-ec2-ip
cd ~/titan_trading_bot/configs
git pull origin configs
cd ..
docker-compose restart
```

---

## 🆘 Common Issues

### Container won't start

```bash
docker-compose logs trader-1  # Check logs
docker-compose ps             # Check status
```

### Out of disk space

```bash
docker system prune -a        # Clean up
df -h                         # Check disk usage
```

### Config not loading

```bash
# Verify config file exists
docker exec -it titan-trader-1 ls -la /app/configs/

# Check environment variable
docker exec -it titan-trader-1 env | grep CONFIG_FILE
```

### Memory issues

```bash
docker stats                  # Check resource usage
free -h                       # Check system memory
```

---

## 📝 Docker Compose Syntax

### Add a new trader

Edit `docker-compose.yml`:

```yaml
trader-4:
  build: .
  container_name: titan-trader-4
  restart: unless-stopped
  environment:
    - CONFIG_FILE=/app/configs/config_4.py
    - AWS_DEFAULT_REGION=us-east-1
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
        cpus: "0.5"
        memory: 256M
```

Then:

```bash
docker-compose up -d trader-4
```

---

## 🌐 Useful Links

- [Docker Documentation](https://docs.docker.com)
- [Docker Compose Docs](https://docs.docker.com/compose)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 💡 Pro Tips

1. **Always check logs first** when something goes wrong
2. **Use `docker stats`** to monitor resource usage
3. **Restart containers** after config changes
4. **Rebuild images** after code changes
5. **Keep configs in orphan branch** for security
6. **Test locally** before deploying to EC2

---

**Happy Trading! 🚀**
