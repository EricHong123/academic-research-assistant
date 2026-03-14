# 生产环境部署指南 | Production Deployment Guide

## 中文

### 1. 服务器要求

| 配置 | 最低 | 推荐 |
|------|------|------|
| CPU | 2 核 | 4+ 核 |
| 内存 | 4 GB | 8+ GB |
| 磁盘 | 20 GB | 50+ GB |
| 系统 | Ubuntu 20.04+ | Ubuntu 22.04+ |

### 2. 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 安装 Redis
sudo apt install -y redis-server

# 安装 PostgreSQL (可选)
sudo apt install -y postgresql postgresql-contrib
```

### 3. 项目部署

```bash
# 创建用户
sudo useradd -m -s /bin/bash ara
sudo usermod -aG sudo ara

# 切换到项目目录
cd /var/www

# 克隆项目
sudo git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant

# 创建虚拟环境
sudo python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -e ".[dev]"

# 设置权限
sudo chown -R ara:ara /var/www/academic-research-assistant
```

### 4. 环境变量配置

```bash
# 创建生产环境配置
sudo nano /var/www/academic-research-assistant/.env
```

```env
# ========== 应用配置 ==========
APP_NAME=Academic Research Assistant
DEBUG=false
LOG_LEVEL=WARNING

# ========== 数据库 ==========
DATABASE_URL=postgresql://ara_user:your-strong-password@localhost:5432/ara_db

# ========== Redis ==========
REDIS_URL=redis://localhost:6379/0

# ========== LLM (选择一个) ==========
# MiniMax (推荐国内)
MINIMAX_API_KEY=your-minimax-key
MINIMAX_BASE_URL=https://api.minimax.chat/v1

# 或 OpenAI
# OPENAI_API_KEY=sk-...

# ========== JWT 安全 ==========
JWT_SECRET_KEY=生成一个随机密钥
# 生成: openssl rand -base64 32

# ========== API 密钥 ==========
PUBMED_API_KEY=...
WOS_API_KEY=...
SCOPUS_API_KEY=...
```

### 5. 数据库设置

```bash
# 创建数据库
sudo -u postgres psql

# 在 PostgreSQL 中执行:
CREATE USER ara_user WITH PASSWORD 'your-strong-password';
CREATE DATABASE ara_db OWNER ara_user;
GRANT ALL PRIVILEGES ON DATABASE ara_db TO ara_user;
\q
```

### 6. Redis 配置

```bash
# 配置 Redis
sudo nano /etc/redis/redis.conf

# 修改以下配置:
# bind 127.0.0.1
# requirepass your-redis-password
# maxmemory 256mb
# maxmemory-policy allkeys-lru

# 重启 Redis
sudo systemctl restart redis
```

### 7. Systemd 服务配置

```bash
# 创建后端服务
sudo nano /etc/systemd/system/ara-api.service
```

```ini
[Unit]
Description=Academic Research Assistant API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ara
Group=ara
WorkingDirectory=/var/www/academic-research-assistant
Environment="PATH=/var/www/academic-research-assistant/venv/bin"
EnvironmentFile=/var/www/academic-research-assistant/.env
ExecStart=/var/www/academic-research-assistant/venv/bin/python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable ara-api
sudo systemctl start ara-api
```

### 8. Nginx 反向代理

```bash
# 安装 Nginx
sudo apt install -y nginx

# 创建配置
sudo nano /etc/nginx/sites-available/ara
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # SSL 配置 (需要先配置 HTTPS)
    # listen 443 ssl http2;
    # ssl_certificate /etc/ssl/certs/your-cert.crt;
    # ssl_certificate_key /etc/ssl/private/your-key.key;

    # 前端静态文件
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }

    # API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/ara /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9. SSL/HTTPS 配置

```bash
# 使用 Certbot 获取免费 SSL 证书
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 10. 防火墙配置

```bash
# 配置防火墙
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 11. 监控和日志

```bash
# 查看日志
sudo journalctl -u ara-api -f

# 查看 API 日志
tail -f /var/log/ara/api.log
```

### 12. Docker 部署 (推荐)

```bash
# 克隆项目
git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant

# 创建生产环境配置
cp .env.example .env
nano .env

# 启动所有服务
docker-compose -f docker-compose.yml up -d
```

---

## English

### 1. Server Requirements

| Config | Minimum | Recommended |
|--------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 20 GB | 50+ GB |
| OS | Ubuntu 20.04+ | Ubuntu 22.04+ |

### 2. Environment Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install Redis
sudo apt install -y redis-server

# Install PostgreSQL (optional)
sudo apt install -y postgresql postgresql-contrib
```

### 3. Deploy Application

```bash
# Create user
sudo useradd -m -s /bin/bash ara
sudo usermod -aG sudo ara

# Navigate to project directory
cd /var/www

# Clone project
sudo git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant

# Create virtual environment
sudo python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Set permissions
sudo chown -R ara:ara /var/www/academic-research-assistant
```

### 4. Environment Variables

```env
# Application
DEBUG=false
LOG_LEVEL=WARNING

# Database
DATABASE_URL=postgresql://ara_user:your-password@localhost:5432/ara_db

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM (choose one)
MINIMAX_API_KEY=your-key
# or OPENAI_API_KEY=sk-...

# JWT
JWT_SECRET_KEY=$(openssl rand -base64 32)
```

### 5. Database Setup

```bash
sudo -u postgres psql
CREATE USER ara_user WITH PASSWORD 'your-password';
CREATE DATABASE ara_db OWNER ara_user;
GRANT ALL PRIVILEGES ON DATABASE ara_db TO ara_user;
\q
```

### 6. Service Configuration

```bash
# Create systemd service
sudo nano /etc/systemd/system/ara-api.service
```

```ini
[Unit]
Description=Academic Research Assistant API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ara
Group=ara
WorkingDirectory=/var/www/academic-research-assistant
Environment="PATH=/var/www/academic-research-assistant/venv/bin"
ExecStart=/var/www/academic-research-assistant/venv/bin/python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable ara-api
sudo systemctl start ara-api
```

### 7. Nginx Configuration

```bash
sudo apt install -y nginx

sudo nano /etc/nginx/sites-available/ara
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ara /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### 8. SSL/HTTPS

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 9. Docker Deployment (Recommended)

```bash
git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant

cp .env.example .env
# Edit .env with production settings

docker-compose up -d
```

### 10. Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (ufw)
- [ ] Set up log monitoring
- [ ] Configure backup strategy
- [ ] Enable fail2ban
- [ ] Regular security updates

### 11. Monitoring

```bash
# Check service status
sudo systemctl status ara-api

# View logs
sudo journalctl -u ara-api -f

# Check resources
htop
```

---

## 快速部署脚本

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting deployment..."

# Variables
DOMAIN=$1
DB_PASSWORD=$(openssl rand -base64 16)
REDIS_PASSWORD=$(openssl rand -base64 16)
JWT_SECRET=$(openssl rand -base64 32)

# Update
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv redis-server nginx certbot

# Clone
cd /var/www
sudo git clone https://github.com/EricHong123/academic-research-assistant.git
cd academic-research-assistant

# Virtual environment
sudo python3.11 -m venv venv
source venv/bin/activate
pip install -e .

# Create .env
cat > .env << EOF
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://ara:$DB_PASSWORD@localhost:5432/ara_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=$JWT_SECRET
MINIMAX_API_KEY=your-key-here
EOF

# Set permissions
sudo chown -R $USER:$USER /var/www/academic-research-assistant

echo "Deployment complete!"
echo "Next steps:"
echo "1. Configure your LLM API key in .env"
echo "2. Run: sudo systemctl start ara-api"
echo "3. Configure Nginx for domain: $DOMAIN"
```

使用: `bash deploy.sh your-domain.com`
