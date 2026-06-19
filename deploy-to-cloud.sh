#!/bin/bash
# 🚀 Hi Mart 云服务器部署 - 快速启动脚本
# 在云服务器上运行此脚本以完成部署

set -e

# 配置
SERVER_IP="64.181.193.238"
DOMAIN="mail.aitepid.crabdance.com"
PROJECT_DIR="/home/ubuntu/himart"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🚀 Hi Mart 云服务器部署启动"
echo "服务器: $SERVER_IP"
echo "域名: $DOMAIN"
echo "项目目录: $PROJECT_DIR"
echo ""

# 检查是否是 root 用户
if [ "$EUID" -eq 0 ]; then
   echo "⚠️ 不要以 root 身份运行此脚本"
   exit 1
fi

# 1. 系统更新
echo "【步骤 1/12】系统更新和依赖安装..."
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3.10 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx nodejs npm git curl wget

# 2. 创建项目目录
echo "【步骤 2/12】创建项目目录..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 3. 克隆代码（假设已有 git 仓库）
echo "【步骤 3/12】拉取最新代码..."
if [ ! -d ".git" ]; then
    echo "⚠️ 请手动上传或 clone 代码到 $PROJECT_DIR"
    exit 1
else
    git pull origin main
fi

# 4. 配置 PostgreSQL
echo "【步骤 4/12】配置数据库..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql << EOF
CREATE DATABASE IF NOT EXISTS himart_db;
CREATE USER IF NOT EXISTS himart WITH PASSWORD 'himart123';
ALTER ROLE himart SET client_encoding TO 'utf8';
ALTER ROLE himart SET default_transaction_isolation TO 'read committed';
ALTER ROLE himart SET default_transaction_deferrable TO on;
ALTER ROLE himart SET default_transaction_level TO 'read committed';
ALTER ROLE himart SET timezone TO 'Africa/Nairobi';
GRANT ALL PRIVILEGES ON DATABASE himart_db TO himart;
EOF

# 5. 配置 Redis
echo "【步骤 5/12】配置缓存服务..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 6. 后端部署
echo "【步骤 6/12】部署后端..."
cd "$BACKEND_DIR"

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt --no-cache-dir

# 创建 .env 文件
cat > .env << 'ENVEOF'
DEBUG=False
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=mail.aitepid.crabdance.com,64.181.193.238,localhost

DB_NAME=himart_db
DB_USER=himart
DB_PASSWORD=himart123
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

STRIPE_PUBLIC_KEY=pk_test_
STRIPE_SECRET_KEY=sk_test_

MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_ENVIRONMENT=sandbox
ENVEOF

# 数据库迁移
python manage.py migrate

# 创建超级用户
echo "创建管理员账户..."
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print("✓ 管理员账户创建成功 (admin/admin123456)")
else:
    print("⚠️ 管理员账户已存在")
PYEOF

# 收集静态文件
python manage.py collectstatic --noinput

deactivate

# 7. 前端部署
echo "【步骤 7/12】部署前端..."
cd "$FRONTEND_DIR"

# 安装依赖
npm ci

# 构建
npm run build

# 8. 配置 Gunicorn
echo "【步骤 8/12】配置应用服务器..."
cd "$BACKEND_DIR"

cat > gunicorn_config.py << 'GUNIEOF'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
GUNIEOF

# 9. 配置 Nginx
echo "【步骤 9/12】配置反向代理..."
sudo tee /etc/nginx/sites-available/himart > /dev/null << 'NGINXEOF'
upstream django_backend {
    server 127.0.0.1:8000;
}

# 速率限制
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name mail.aitepid.crabdance.com *.aitepid.crabdance.com 64.181.193.238;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS 服务
server {
    listen 443 ssl http2;
    server_name mail.aitepid.crabdance.com *.aitepid.crabdance.com;

    # SSL 证书（需要先生成）
    ssl_certificate /etc/letsencrypt/live/mail.aitepid.crabdance.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mail.aitepid.crabdance.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_comp_level 6;
    gzip_min_length 1024;

    # 前端静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /home/ubuntu/himart/frontend/dist;
        expires 365d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API 代理
    location /api {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_valid 200 10m;

        limit_req zone=api burst=50 nodelay;
    }

    # 前端页面
    location / {
        root /home/ubuntu/himart/frontend/dist;
        try_files $uri $uri/ /index.html;

        # 不缓存 HTML
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/himart /etc/nginx/sites-enabled/himart
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# 10. 配置 Supervisor（进程管理）
echo "【步骤 10/12】配置进程管理..."
sudo tee /etc/supervisor/conf.d/himart.conf > /dev/null << 'SUPEOF'
[program:himart-backend]
directory=/home/ubuntu/himart/backend
command=/home/ubuntu/himart/backend/venv/bin/gunicorn config.wsgi:application --config gunicorn_config.py
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/himart-backend.log
stderr_logfile=/var/log/supervisor/himart-backend-error.log
user=ubuntu
environment=PATH="/home/ubuntu/himart/backend/venv/bin"

[group:himart]
programs=himart-backend
priority=999
SUPEOF

sudo systemctl restart supervisor

# 11. 配置 SSL 证书（使用 Let's Encrypt）
echo "【步骤 11/12】配置 SSL 证书..."
sudo apt-get install -y certbot python3-certbot-nginx

sudo certbot certonly --nginx \
    -d mail.aitepid.crabdance.com \
    --email admin@example.com \
    --agree-tos \
    --no-eff-email \
    --non-interactive || echo "⚠️ SSL 证书配置可能需要手动处理"

# 12. 启动服务
echo "【步骤 12/12】启动所有服务..."
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl restart supervisor

# 验证
echo ""
echo "🔍 验证部署..."
sleep 3

if curl -sf http://localhost:8000/api/products/ > /dev/null; then
    echo "✅ 后端 API 正常"
else
    echo "❌ 后端 API 异常"
fi

if curl -sf http://localhost/ > /dev/null; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   🎉 部署完成！服务已启动              ║"
echo "╠════════════════════════════════════════╣"
echo "║ 前端地址: https://mail.aitepid.crabdance.com"
echo "║ API 地址: https://mail.aitepid.crabdance.com/api"
echo "║ 管理后台: https://mail.aitepid.crabdance.com/admin"
echo "║ 用户名: admin"
echo "║ 密码: admin123456"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📝 查看日志:"
echo "  tail -f /var/log/supervisor/himart-backend.log"
echo "  tail -f /var/log/nginx/error.log"
echo ""
echo "🔧 常用命令:"
echo "  sudo supervisorctl status          # 查看进程状态"
echo "  sudo supervisorctl restart himart  # 重启服务"
echo "  sudo systemctl restart nginx       # 重启 Nginx"
echo ""
