#!/bin/bash

# Hi Mart 平台部署脚本 - Oracle 云服务器
# 用途: 完整部署 Django + Vue 应用到 Ubuntu 服务器
# 使用: bash deploy-to-oracle.sh

set -e

# ========== 配置 ==========
SERVER_IP="64.181.193.238"
SSH_USER="ubuntu"
SSH_KEY="$HOME/.ssh/id_rsa"  # 你的 SSH 密钥路径（需要替换为实际路径）

PROJECT_NAME="himart"
PROJECT_DIR="/home/${SSH_USER}/${PROJECT_NAME}"
APP_PORT_BACKEND=8000
APP_PORT_FRONTEND=3000

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Hi Mart 部署到 Oracle 云${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# ========== 步骤 1: 测试连接 ==========
echo -e "${YELLOW}[1/8] 测试服务器连接...${NC}"
if ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" "echo 'Connection OK'"; then
    echo -e "${GREEN}✓ 服务器连接成功${NC}"
else
    echo -e "${RED}✗ 无法连接到服务器${NC}"
    echo "请检查:"
    echo "  - IP 地址是否正确: $SERVER_IP"
    echo "  - SSH 密钥路径是否正确: $SSH_KEY"
    echo "  - SSH 用户名是否正确: $SSH_USER"
    exit 1
fi

echo ""

# ========== 步骤 2: 更新系统 ==========
echo -e "${YELLOW}[2/8] 更新系统包...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'EOF'
    set -e
    sudo apt-get update
    sudo apt-get upgrade -y
    echo "✓ 系统更新完成"
EOF

echo ""

# ========== 步骤 3: 安装依赖 ==========
echo -e "${YELLOW}[3/8] 安装系统依赖...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'EOF'
    set -e
    sudo apt-get install -y \
        python3-pip python3-venv python3-dev \
        nodejs npm \
        postgresql postgresql-contrib \
        redis-server \
        git curl wget \
        build-essential libssl-dev libffi-dev

    echo "✓ 依赖安装完成"
EOF

echo ""

# ========== 步骤 4: 克隆项目 ==========
echo -e "${YELLOW}[4/8] 克隆项目仓库...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'EOF'
    set -e

    # 检查项目是否已存在
    if [ -d "himart" ]; then
        echo "更新现有项目..."
        cd himart
        git pull origin main
    else
        echo "克隆新项目..."
        git clone https://github.com/your-username/himart.git
        cd himart
    fi

    echo "✓ 项目已准备"
EOF

echo ""

# ========== 步骤 5: 配置后端 ==========
echo -e "${YELLOW}[5/8] 配置后端环境...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'EOF'
    set -e
    cd himart/backend

    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    source venv/bin/activate

    # 升级 pip
    pip install --upgrade pip setuptools wheel

    # 安装依赖
    pip install -r requirements.txt

    # 创建 .env 文件
    if [ ! -f ".env" ]; then
        cat > .env << 'ENVEOF'
DEBUG=False
SECRET_KEY=your-secret-key-change-this-in-production
ALLOWED_HOSTS=64.181.193.238,localhost,127.0.0.1

# 数据库
DATABASE_URL=postgresql://himart_user:himart_password@localhost:5432/himart_db

# Redis
REDIS_URL=redis://localhost:6379/0

# 第三方服务 (可选)
MPESA_CONSUMER_KEY=your_mpesa_key
MPESA_CONSUMER_SECRET=your_mpesa_secret
STRIPE_API_KEY=your_stripe_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret
ENVEOF
        echo "⚠ .env 文件已创建，请更新生产配置"
    fi

    # 迁移数据库
    python manage.py migrate

    # 创建超级用户 (可选)
    # python manage.py createsuperuser

    echo "✓ 后端配置完成"
EOF

echo ""

# ========== 步骤 6: 配置前端 ==========
echo -e "${YELLOW}[6/8] 配置前端环境...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'EOF'
    set -e
    cd himart/frontend

    # 安装依赖
    npm install

    # 创建 .env 文件
    if [ ! -f ".env" ]; then
        cat > .env << 'ENVEOF'
VITE_API_URL=http://64.181.193.238:8000/api
ENVEOF
        echo "⚠ .env 文件已创建，请验证 API 地址"
    fi

    # 构建
    npm run build

    echo "✓ 前端构建完成"
EOF

echo ""

# ========== 步骤 7: 配置数据库 ==========
echo -e "${YELLOW}[7/8] 配置 PostgreSQL 数据库...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'EOF'
    set -e

    # 启动 PostgreSQL
    sudo systemctl restart postgresql

    # 创建数据库和用户
    sudo -u postgres psql << DBEOF
        -- 创建用户
        CREATE USER IF NOT EXISTS himart_user WITH PASSWORD 'himart_password';

        -- 创建数据库
        CREATE DATABASE IF NOT EXISTS himart_db OWNER himart_user;

        -- 授予权限
        GRANT ALL PRIVILEGES ON DATABASE himart_db TO himart_user;

        \c himart_db
        GRANT ALL PRIVILEGES ON SCHEMA public TO himart_user;
DBEOF

    echo "✓ 数据库配置完成"
EOF

echo ""

# ========== 步骤 8: 启动服务 ==========
echo -e "${YELLOW}[8/8] 启动应用服务...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'EOF'
    set -e
    cd himart

    # 启动 Redis
    sudo systemctl restart redis-server

    # 后台启动 Django
    cd backend
    source venv/bin/activate
    nohup python manage.py runserver 0.0.0.0:8000 > /tmp/django.log 2>&1 &
    echo $! > /tmp/django.pid

    # 后台启动前端 (使用 PM2 或 Supervisor 更好)
    cd ../frontend
    # npm run build 已在前面执行
    # 可以使用 serve 或 nginx 提供静态文件
    npm install -g serve
    nohup serve -s dist -l 3000 > /tmp/frontend.log 2>&1 &
    echo $! > /tmp/frontend.pid

    sleep 2
    echo "✓ 应用服务已启动"
    echo ""
    echo "日志位置:"
    echo "  Django: tail -f /tmp/django.log"
    echo "  Frontend: tail -f /tmp/frontend.log"
EOF

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ 部署完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "访问应用:"
echo -e "  前端: ${YELLOW}http://${SERVER_IP}:3000${NC}"
echo -e "  后端 API: ${YELLOW}http://${SERVER_IP}:8000/api${NC}"
echo -e "  管理后台: ${YELLOW}http://${SERVER_IP}:8000/admin${NC}"
echo ""
echo "下一步:"
echo "  1. 更新 backend/.env 中的生产配置和密钥"
echo "  2. 创建管理员账户: python manage.py createsuperuser"
echo "  3. 配置 Nginx 作为反向代理"
echo "  4. 配置 SSL 证书 (Let's Encrypt)"
echo "  5. 配置 Supervisor/PM2 管理进程"
echo ""
echo "服务器信息:"
echo "  IP: $SERVER_IP"
echo "  SSH: ssh -i $SSH_KEY ${SSH_USER}@${SERVER_IP}"
echo ""
