#!/bin/bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
SERVER_IP="64.181.193.238"
SSH_KEY="$HOME/.ssh/ssh-key-2026-03-17.key"
SSH_USER="ubuntu"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  第一阶段功能部署脚本                      ║${NC}"
echo -e "${BLUE}║  域名: mail.aitepid.crabdance.com          ║${NC}"
echo -e "${BLUE}║  IP:   $SERVER_IP                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

# 步骤计数
STEP=0
TOTAL_STEPS=8

print_step() {
  STEP=$((STEP + 1))
  echo -e "${BLUE}[步骤 $STEP/$TOTAL_STEPS]${NC} $1"
}

print_success() {
  echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
  echo -e "${RED}[✗]${NC} $1"
}

# 第1步：检查本地代码
print_step "检查本地代码"
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
  print_error "未找到 backend 或 frontend 目录"
  exit 1
fi
print_success "代码目录存在"

# 第2步：git 提交
print_step "提交代码变更"
git add -A
git commit -m "feat: 实现第一阶段功能（购物车、订单、优惠券系统）" || print_success "代码已最新"
print_success "代码已提交"

# 第3步：连接到服务器
print_step "连接到服务器"
echo -e "${YELLOW}正在测试SSH连接...${NC}"

ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "echo 'SSH连接正常'" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  print_success "SSH连接成功"
else
  print_error "无法连接到服务器"
  exit 1
fi

# 第4步：更新后端代码
print_step "更新后端代码和执行迁移"

ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << 'REMOTE_COMMANDS'
set -e

cd ~/himart/backend

echo "📦 收集后端更新..."
git pull origin main

echo "🔧 安装依赖..."
source venv/bin/activate
pip install -q -r requirements.txt

echo "🗄️ 执行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

echo "✅ 后端迁移完成"
REMOTE_COMMANDS

print_success "后端已更新和迁移"

# 第5步：构建前端
print_step "构建前端"
cd frontend

echo -e "${YELLOW}安装前端依赖...${NC}"
npm install -q 2>/dev/null || echo "依赖已最新"

echo -e "${YELLOW}构建前端应用...${NC}"
npm run build

print_success "前端构建完成"
cd ..

# 第6步：上传前端构建
print_step "上传前端构建到服务器"

scp -i "$SSH_KEY" -r frontend/dist/* "$SSH_USER@$SERVER_IP:~/himart/frontend/dist/" > /dev/null 2>&1

print_success "前端文件已上传"

# 第7步：重启服务
print_step "重启应用服务"

ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << 'REMOTE_COMMANDS'
echo "♻️ 重启后端服务..."
sudo supervisorctl restart himart-backend

echo "♻️ 重启前端服务..."
sudo supervisorctl restart himart-frontend

echo "⏳ 等待服务启动..."
sleep 3

echo "📊 检查服务状态..."
sudo supervisorctl status himart:*

echo "✅ 服务已重启"
REMOTE_COMMANDS

print_success "应用已重启"

# 第8步：验证部署
print_step "验证部署"

echo -e "${YELLOW}检查后端API...${NC}"
BACKEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://64.181.193.238/api/products/)
if [ "$BACKEND_CHECK" = "200" ]; then
  print_success "后端API正常 (HTTP $BACKEND_CHECK)"
else
  print_error "后端API异常 (HTTP $BACKEND_CHECK)"
fi

echo -e "${YELLOW}检查前端应用...${NC}"
FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://64.181.193.238/)
if [ "$FRONTEND_CHECK" = "200" ]; then
  print_success "前端应用正常 (HTTP $FRONTEND_CHECK)"
else
  print_error "前端应用异常 (HTTP $FRONTEND_CHECK)"
fi

# 完成
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 部署完成！${NC}"
echo -e "${BLUE}║  ${NC}"
echo -e "${BLUE}║  📍 访问地址:${NC}"
echo -e "${BLUE}║     主应用: http://64.181.193.238${NC}"
echo -e "${BLUE}║     API: http://64.181.193.238/api${NC}"
echo -e "${BLUE}║     文档: http://64.181.193.238/api/schema/${NC}"
echo -e "${BLUE}║     管理后台: http://64.181.193.238/admin${NC}"
echo -e "${BLUE}║  ${NC}"
echo -e "${BLUE}║  📚 新功能:${NC}"
echo -e "${BLUE}║     ✓ 购物车系统 (/api/cart/)${NC}"
echo -e "${BLUE}║     ✓ 订单管理 (/api/orders/)${NC}"
echo -e "${BLUE}║     ✓ 优惠券系统 (/api/promotions/)${NC}"
echo -e "${BLUE}║  ${NC}"
echo -e "${BLUE}║  🔍 查看日志:${NC}"
echo -e "${BLUE}║     ssh -i \"$SSH_KEY\" $SSH_USER@$SERVER_IP${NC}"
echo -e "${BLUE}║     sudo tail -f /var/log/supervisor/himart-backend.log${NC}"
echo -e "${BLUE}║  ${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
