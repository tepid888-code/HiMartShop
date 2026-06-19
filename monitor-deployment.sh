#!/bin/bash

# 实时监控部署进度
# 用法: bash monitor-deployment.sh

SERVER_IP="64.181.193.238"
SERVER_DOMAIN="mail.aitepid.crabdance.com"
SSH_USER="ubuntu"
SSH_KEY="/c/Users/85142/.ssh/ssh-key-2026-03-17.key"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Hi Mart 部署进度实时监控                  ║${NC}"
echo -e "${BLUE}║  服务器: ${SERVER_DOMAIN}           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# 显示菜单
show_menu() {
    echo -e "${YELLOW}选择监控项目:${NC}"
    echo "  1) 查看总体部署进度"
    echo "  2) 查看后端日志"
    echo "  3) 查看前端日志"
    echo "  4) 查看 Nginx 日志"
    echo "  5) 查看服务状态"
    echo "  6) 访问进度仪表板"
    echo "  7) 创建管理员账户"
    echo "  8) 连接到服务器"
    echo "  9) 退出"
    echo ""
}

# 1. 部署进度
show_progress() {
    echo -e "${BLUE}📊 检查部署进度...${NC}"
    ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'PROGRESS'
echo "部署状态检查:"
echo ""

# 检查各个组件
echo "✓ 系统检查:"
echo "  - Python: $(python3 --version 2>&1 | cut -d' ' -f2)"
echo "  - Node.js: $(node --version 2>&1)"
echo "  - PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "  - Redis: $(sudo systemctl is-active redis-server)"
echo "  - Nginx: $(sudo systemctl is-active nginx)"
echo ""

echo "✓ 项目文件:"
[ -d ~/himart/backend ] && echo "  - 后端: ✓" || echo "  - 后端: ✗"
[ -d ~/himart/frontend ] && echo "  - 前端: ✓" || echo "  - 前端: ✗"
echo ""

echo "✓ 服务进程:"
sudo supervisorctl status 2>/dev/null | head -10 || echo "  查询中..."
echo ""

echo "✓ 网络状态:"
echo "  - HTTP (80): $(sudo netstat -tlnp 2>/dev/null | grep -q ':80 ' && echo '✓' || echo '✗')"
echo "  - Django (8000): $(sudo netstat -tlnp 2>/dev/null | grep -q ':8000 ' && echo '✓' || echo '✗')"
echo "  - Node (3000): $(sudo netstat -tlnp 2>/dev/null | grep -q ':3000 ' && echo '✓' || echo '✗')"
echo ""
PROGRESS
}

# 2. 后端日志
show_backend_logs() {
    echo -e "${BLUE}📝 后端日志 (最近 20 行):${NC}"
    ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" "sudo tail -n 20 /var/log/supervisor/himart-backend.log 2>/dev/null || echo '日志文件未找到'"
}

# 3. 前端日志
show_frontend_logs() {
    echo -e "${BLUE}📝 前端日志 (最近 20 行):${NC}"
    ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" "sudo tail -n 20 /var/log/supervisor/himart-frontend.log 2>/dev/null || echo '日志文件未找到'"
}

# 4. Nginx 日志
show_nginx_logs() {
    echo -e "${BLUE}📝 Nginx 错误日志 (最近 20 行):${NC}"
    ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" "sudo tail -n 20 /var/log/nginx/error.log 2>/dev/null || echo '日志文件未找到'"
}

# 5. 服务状态
show_service_status() {
    echo -e "${BLUE}⚙️  服务状态详细信息:${NC}"
    ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << 'STATUS'
echo "系统服务:"
echo ""
sudo systemctl status nginx --no-pager | grep -E "Active|Loaded"
sudo systemctl status postgresql --no-pager | grep -E "Active|Loaded"
sudo systemctl status redis-server --no-pager | grep -E "Active|Loaded"
echo ""
echo "应用进程:"
sudo supervisorctl status
echo ""
echo "资源使用:"
free -h | head -2
df -h / | tail -1
STATUS
}

# 6. 访问仪表板
open_dashboard() {
    echo -e "${GREEN}🌐 打开部署进度仪表板...${NC}"
    echo "URL: http://${SERVER_DOMAIN}/deploy-status.html"
    echo ""
    # 尝试在默认浏览器中打开（如果支持）
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://${SERVER_DOMAIN}/deploy-status.html"
    elif command -v open &> /dev/null; then
        open "http://${SERVER_DOMAIN}/deploy-status.html"
    else
        echo "请在浏览器中手动访问上述 URL"
    fi
}

# 7. 创建管理员
create_admin() {
    echo -e "${YELLOW}创建管理员账户${NC}"
    read -p "用户名: " username
    read -p "邮箱: " email
    read -sp "密码: " password
    echo ""

    ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}" << ADMIN
cd ~/himart/backend
source venv/bin/activate
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('$username', '$email', '$password')
print('✓ 管理员账户已创建')
EOF
ADMIN
}

# 8. 连接服务器
connect_server() {
    echo -e "${BLUE}📡 连接到服务器...${NC}"
    ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER_IP}"
}

# 主循环
while true; do
    show_menu
    read -p "选择 [1-9]: " choice

    case $choice in
        1) show_progress ;;
        2) show_backend_logs ;;
        3) show_frontend_logs ;;
        4) show_nginx_logs ;;
        5) show_service_status ;;
        6) open_dashboard ;;
        7) create_admin ;;
        8) connect_server ;;
        9) echo -e "${GREEN}再见！${NC}"; exit 0 ;;
        *) echo -e "${RED}无效选择${NC}" ;;
    esac

    echo ""
    read -p "按 Enter 继续..."
    clear
done
