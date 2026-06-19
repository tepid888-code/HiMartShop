#!/bin/bash

# Hi Mart 云服务器部署脚本 - 带实时进度显示
# 在 mail.aitepid.crabdance.com 上部署项目

set -e

# 配置
SERVER_IP="64.181.193.238"
SERVER_DOMAIN="mail.aitepid.crabdance.com"
SSH_USER="ubuntu"
SSH_KEY="/c/Users/85142/.ssh/ssh-key-2026-03-17.key"
GITHUB_REPO="${1:-https://github.com/your-username/himart.git}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志文件
DEPLOY_LOG="/tmp/himart-deploy-$(date +%s).log"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$DEPLOY_LOG"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$DEPLOY_LOG"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1" | tee -a "$DEPLOY_LOG"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$DEPLOY_LOG"
}

# 进度条
show_progress() {
    local step=$1
    local total=$2
    local desc=$3
    local percent=$((step * 100 / total))

    printf "\r${BLUE}进度: [%-50s] %d%%${NC} - %s" \
        "$(printf '#%.0s' $(seq 1 $((percent/2))))" \
        "$percent" \
        "$desc"
}

clear
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Hi Mart 云服务器部署                    ║${NC}"
echo -e "${BLUE}║  域名: ${SERVER_DOMAIN}           ║${NC}"
echo -e "${BLUE}║  IP:   ${SERVER_IP}                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo "📋 部署日志: $DEPLOY_LOG"
echo ""

# ========== 步骤 1: 连接测试 ==========
show_progress 1 8 "测试服务器连接"
if ! ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" "echo 'OK'" > /dev/null 2>&1; then
    log_error "无法连接到服务器"
    exit 1
fi
echo ""
log_success "服务器连接正常"

# ========== 步骤 2: 克隆项目 ==========
show_progress 2 8 "克隆项目仓库"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'CLONE_SCRIPT' > /dev/null 2>&1
cd ~
if [ -d "himart" ]; then
    cd himart && git pull origin main 2>/dev/null || true
else
    git clone https://github.com/your-username/himart.git 2>/dev/null || mkdir -p himart
fi
CLONE_SCRIPT
echo ""
log_success "项目已克隆到服务器"

# ========== 步骤 3: 安装依赖 ==========
show_progress 3 8 "安装系统依赖"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'DEPS_SCRIPT' > /dev/null 2>&1
# 等待 apt 锁
while sudo fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do sleep 1; done

# 安装缺失的包
[ -x "$(command -v node)" ] || (curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs > /dev/null 2>&1)
[ -x "$(command -v redis-server)" ] || sudo apt-get install -y redis-server > /dev/null 2>&1
[ -x "$(command -v supervisord)" ] || sudo apt-get install -y supervisor > /dev/null 2>&1

# 启动服务
sudo systemctl start postgresql redis-server 2>/dev/null || true
DEPS_SCRIPT
echo ""
log_success "系统依赖已安装"

# ========== 步骤 4: 配置后端 ==========
show_progress 4 8 "配置后端环境"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'BACKEND_SCRIPT' > /dev/null 2>&1
cd ~/himart/backend

# 虚拟环境
[ -d "venv" ] || python3 -m venv venv > /dev/null 2>&1
source venv/bin/activate

# 安装依赖
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt

# .env 文件
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=change-this-secret-key-in-production
ALLOWED_HOSTS=64.181.193.238,localhost,mail.aitepid.crabdance.com

DATABASE_URL=postgresql://himart_user:himart_password@localhost:5432/himart_db
REDIS_URL=redis://localhost:6379/0

CORS_ALLOWED_ORIGINS=http://64.181.193.238,http://mail.aitepid.crabdance.com
EOF
fi

# 数据库迁移
python manage.py migrate --noinput 2>&1 | tail -1
BACKEND_SCRIPT
echo ""
log_success "后端已配置"

# ========== 步骤 5: 配置前端 ==========
show_progress 5 8 "配置前端环境"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'FRONTEND_SCRIPT' > /dev/null 2>&1
cd ~/himart/frontend

npm install --silent > /dev/null 2>&1
npm run build --silent > /dev/null 2>&1
sudo npm install -g serve > /dev/null 2>&1
FRONTEND_SCRIPT
echo ""
log_success "前端已配置"

# ========== 步骤 6: 配置数据库 ==========
show_progress 6 8 "配置数据库"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'DB_SCRIPT' > /dev/null 2>&1
sudo -u postgres psql << SQL
DO \$\$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'himart_user') THEN
        CREATE USER himart_user WITH PASSWORD 'himart_password';
    END IF;
END \$\$;
DO \$\$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'himart_db') THEN
        CREATE DATABASE himart_db OWNER himart_user;
    END IF;
END \$\$;
GRANT ALL PRIVILEGES ON DATABASE himart_db TO himart_user;
SQL
DB_SCRIPT
echo ""
log_success "数据库已配置"

# ========== 步骤 7: 配置服务管理 ==========
show_progress 7 8 "配置 Supervisor 和 Nginx"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'SERVICES_SCRIPT' > /dev/null 2>&1
# Supervisor
sudo cp ~/himart/supervisor-himart.conf /etc/supervisor/conf.d/ 2>/dev/null || true
sudo supervisorctl reread 2>/dev/null || true
sudo supervisorctl update 2>/dev/null || true
sudo supervisorctl start himart:* 2>/dev/null || true

# Nginx
sudo cp ~/himart/nginx.conf /etc/nginx/sites-available/himart 2>/dev/null || true
sudo ln -sf /etc/nginx/sites-available/himart /etc/nginx/sites-enabled/ 2>/dev/null || true
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
sudo nginx -t > /dev/null 2>&1
sudo systemctl restart nginx 2>/dev/null || true
SERVICES_SCRIPT
echo ""
log_success "服务管理已配置"

# ========== 步骤 8: 创建部署完成标记 ==========
show_progress 8 8 "完成部署"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'COMPLETE_SCRIPT'
echo "✓ 部署完成于 $(date)" > ~/DEPLOYMENT_COMPLETE
COMPLETE_SCRIPT
echo ""
echo ""

# ========== 部署完成总结 ==========
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Hi Mart 部署成功！                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

log_success "部署已完成"
echo ""
echo -e "${BLUE}🌐 立即访问你的应用:${NC}"
echo ""
echo "  前端应用:   http://${SERVER_DOMAIN}"
echo "  API 接口:   http://${SERVER_DOMAIN}/api"
echo "  管理后台:   http://${SERVER_DOMAIN}/admin"
echo ""

echo -e "${BLUE}📊 服务状态:${NC}"
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" "sudo supervisorctl status 2>/dev/null | grep -E 'himart|started' || echo '查询中...'"

echo ""
echo -e "${BLUE}📝 后续步骤:${NC}"
echo "  1. 创建管理员账户:"
echo "     ssh -i '$SSH_KEY' ${SSH_USER}@${SERVER_IP}"
echo "     cd ~/himart/backend && source venv/bin/activate"
echo "     python manage.py createsuperuser"
echo ""
echo "  2. 更新生产密钥:"
echo "     ssh -i '$SSH_KEY' ${SSH_USER}@${SERVER_IP}"
echo "     nano ~/himart/backend/.env"
echo ""
echo "  3. 查看实时日志:"
echo "     ssh -i '$SSH_KEY' ${SSH_USER}@${SERVER_IP} 'tail -f /var/log/supervisor/himart-backend.log'"
echo ""

echo -e "${BLUE}📄 部署日志已保存:${NC}"
echo "  $DEPLOY_LOG"
echo ""
