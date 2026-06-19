#!/bin/bash

# Hi Mart 平台快速部署脚本 - Oracle 云
# 针对已预装 Python、PostgreSQL、Nginx 的环境优化

set -e

# 配置
SERVER_IP="64.181.193.238"
SSH_USER="ubuntu"
SSH_KEY="/c/Users/85142/.ssh/ssh-key-2026-03-17.key"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Hi Mart 部署到 Oracle 云 (Ubuntu)    ║${NC}"
echo -e "${BLUE}║  IP: ${SERVER_IP}              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# ========== 步骤 1: 系统更新和依赖安装 ==========
echo -e "${YELLOW}[1/7] 更新系统并安装依赖...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SSHEOF'
    set -e

    echo "更新包列表..."
    sudo apt-get update -qq

    echo "安装 Node.js..."
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi

    echo "安装 Redis..."
    if ! command -v redis-server &> /dev/null; then
        sudo apt-get install -y redis-server
    fi

    echo "安装其他依赖..."
    sudo apt-get install -y \
        python3-pip python3-venv python3-dev \
        git curl wget supervisor build-essential \
        libssl-dev libffi-dev

    # 启动服务
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    sudo systemctl start redis-server
    sudo systemctl enable redis-server

    echo "✓ 依赖安装完成"
SSHEOF

echo ""

# ========== 步骤 2: 克隆/更新项目 ==========
echo -e "${YELLOW}[2/7] 克隆项目仓库...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SSHEOF'
    set -e

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
SSHEOF

echo ""

# ========== 步骤 3: 配置后端 ==========
echo -e "${YELLOW}[3/7] 配置后端环境...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SSHEOF'
    set -e
    cd himart/backend

    # 虚拟环境
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
    fi

    source venv/bin/activate

    # 升级 pip
    pip install --quiet --upgrade pip setuptools wheel

    # 安装依赖
    echo "安装 Python 依赖..."
    pip install --quiet -r requirements.txt

    # 创建 .env 文件
    if [ ! -f ".env" ]; then
        echo "创建生产环境配置..."
        cat > .env << 'ENVEOF'
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=64.181.193.238,localhost,127.0.0.1

DATABASE_URL=postgresql://himart_user:himart_password@localhost:5432/himart_db
REDIS_URL=redis://localhost:6379/0

CORS_ALLOWED_ORIGINS=http://64.181.193.238,http://localhost
ENVEOF
    fi

    # 运行迁移
    echo "运行数据库迁移..."
    python manage.py migrate --noinput

    echo "✓ 后端配置完成"
SSHEOF

echo ""

# ========== 步骤 4: 配置数据库 ==========
echo -e "${YELLOW}[4/7] 配置 PostgreSQL 数据库...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SSHEOF'
    set -e

    sudo -u postgres psql << DBEOF
        -- 检查用户是否存在
        DO \$\$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'himart_user') THEN
                CREATE USER himart_user WITH PASSWORD 'himart_password';
            END IF;
        END \$\$;

        -- 检查数据库是否存在
        DO \$\$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'himart_db') THEN
                CREATE DATABASE himart_db OWNER himart_user;
            END IF;
        END \$\$;

        -- 授予权限
        GRANT ALL PRIVILEGES ON DATABASE himart_db TO himart_user;
        \c himart_db
        GRANT ALL PRIVILEGES ON SCHEMA public TO himart_user;
DBEOF

    echo "✓ 数据库配置完成"
SSHEOF

echo ""

# ========== 步骤 5: 配置前端 ==========
echo -e "${YELLOW}[5/7] 配置前端环境...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SSHEOF'
    set -e
    cd himart/frontend

    # 创建 .env 文件
    if [ ! -f ".env" ]; then
        cat > .env << 'ENVEOF'
VITE_API_URL=http://64.181.193.238/api
ENVEOF
    fi

    # 安装依赖并构建
    echo "安装 npm 依赖..."
    npm install --silent

    echo "构建前端..."
    npm run build

    # 安装 serve
    npm install -g serve

    echo "✓ 前端配置完成"
SSHEOF

echo ""

# ========== 步骤 6: 配置 Supervisor ==========
echo -e "${YELLOW}[6/7] 配置进程管理 (Supervisor)...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SSHEOF'
    set -e

    # 复制配置文件
    sudo cp ~/himart/supervisor-himart.conf /etc/supervisor/conf.d/

    # 重新加载配置
    sudo supervisorctl reread
    sudo supervisorctl update

    # 启动服务
    sudo supervisorctl start himart:*

    echo "✓ Supervisor 配置完成"
    echo ""
    echo "进程状态:"
    sudo supervisorctl status
SSHEOF

echo ""

# ========== 步骤 7: 配置 Nginx ==========
echo -e "${YELLOW}[7/7] 配置 Nginx 反向代理...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SSHEOF'
    set -e

    # 复制配置文件
    sudo cp ~/himart/nginx.conf /etc/nginx/sites-available/himart

    # 启用配置
    if [ -L /etc/nginx/sites-enabled/himart ]; then
        echo "配置已启用"
    else
        sudo ln -sf /etc/nginx/sites-available/himart /etc/nginx/sites-enabled/
    fi

    # 删除默认配置
    sudo rm -f /etc/nginx/sites-enabled/default

    # 检查配置
    sudo nginx -t

    # 重启 Nginx
    sudo systemctl restart nginx

    echo "✓ Nginx 配置完成"
SSHEOF

echo ""

# ========== 验证部署 ==========
echo -e "${YELLOW}[验证] 检查服务状态...${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SSHEOF'
    echo ""
    echo "=== 进程状态 ==="
    sudo supervisorctl status

    echo ""
    echo "=== 服务状态 ==="
    sudo systemctl status nginx --no-pager | grep -E "Active|Loaded"
    sudo systemctl status redis-server --no-pager | grep -E "Active|Loaded"
    sudo systemctl status postgresql --no-pager | grep -E "Active|Loaded"

    echo ""
    echo "=== 数据库检查 ==="
    psql -U himart_user -d himart_db -c "SELECT 1;" 2>/dev/null && echo "✓ 数据库连接正常" || echo "⚠ 数据库连接检查"
SSHEOF

echo ""
echo -e "${GREEN}╔═════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ 部署完成！                                  ║${NC}"
echo -e "${GREEN}╚═════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🌐 访问应用:${NC}"
echo -e "  前端应用:     http://64.181.193.238"
echo -e "  后端 API:     http://64.181.193.238/api"
echo -e "  管理后台:     http://64.181.193.238/admin"
echo ""
echo -e "${BLUE}📝 后续步骤:${NC}"
echo -e "  1. 创建管理员账户:"
echo -e "     ssh -i ${SSH_KEY} ${SSH_USER}@${SERVER_IP}"
echo -e "     cd himart/backend && source venv/bin/activate"
echo -e "     python manage.py createsuperuser"
echo ""
echo -e "  2. 更新生产密钥 (重要):"
echo -e "     vi ~/himart/backend/.env"
echo -e "     更新: SECRET_KEY, STRIPE_API_KEY, MPESA_KEYS"
echo ""
echo -e "  3. 配置 HTTPS (推荐):"
echo -e "     sudo apt-get install certbot python3-certbot-nginx"
echo -e "     sudo certbot certonly --nginx -d yourdomain.com"
echo ""
echo -e "${BLUE}🔍 查看日志:${NC}"
echo -e "  后端日志:     ssh -i ${SSH_KEY} ${SSH_USER}@${SERVER_IP} 'sudo tail -f /var/log/supervisor/himart-backend.log'"
echo -e "  前端日志:     ssh -i ${SSH_KEY} ${SSH_USER}@${SERVER_IP} 'sudo tail -f /var/log/supervisor/himart-frontend.log'"
echo -e "  Nginx 日志:   ssh -i ${SSH_KEY} ${SSH_USER}@${SERVER_IP} 'sudo tail -f /var/log/nginx/error.log'"
echo ""
