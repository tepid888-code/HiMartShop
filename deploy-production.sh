#!/bin/bash
# 🚀 Hi Mart 生产部署脚本
# 用法: chmod +x deploy-production.sh && ./deploy-production.sh

set -e  # 任何错误都会退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/home/ubuntu/himart"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKUP_DIR="/var/backups/himart"
LOG_FILE="/var/log/deployment.log"

echo -e "${GREEN}🚀 Hi Mart 生产部署脚本${NC}\n"

# 日志记录函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 成功提示
success() {
    echo -e "${GREEN}✓ $1${NC}"
    log "✓ $1"
}

# 错误提示
error() {
    echo -e "${RED}✗ $1${NC}"
    log "✗ $1"
    exit 1
}

# 信息提示
info() {
    echo -e "${YELLOW}ℹ $1${NC}"
    log "ℹ $1"
}

# 1. 环境检查
echo -e "\n${YELLOW}【步骤 1/10】环境检查${NC}"

# 检查项目目录
if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
    error "项目目录不存在"
fi
success "项目目录存在"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    error "Python3 未安装"
fi
success "Python3 已安装: $(python3 --version)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    error "Node.js 未安装"
fi
success "Node.js 已安装: $(node --version)"

# 检查 PostgreSQL
if ! command -v psql &> /dev/null; then
    error "PostgreSQL 未安装"
fi
success "PostgreSQL 已安装: $(psql --version)"

# 检查 Redis
if ! redis-cli ping &> /dev/null; then
    error "Redis 未运行"
fi
success "Redis 正在运行"

# 2. 备份
echo -e "\n${YELLOW}【步骤 2/10】创建备份${NC}"

mkdir -p "$BACKUP_DIR"

# 备份数据库
info "备份数据库..."
pg_dump -U himart himart_db | gzip > "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
success "数据库备份完成"

# 备份代码
info "备份代码..."
tar -czf "$BACKUP_DIR/code_backup_$(date +%Y%m%d_%H%M%S).tar.gz" "$PROJECT_DIR" \
    --exclude="$BACKEND_DIR/venv" \
    --exclude="$FRONTEND_DIR/node_modules" \
    --exclude="$FRONTEND_DIR/dist"
success "代码备份完成"

# 3. 停止服务
echo -e "\n${YELLOW}【步骤 3/10】停止服务${NC}"

info "停止 Supervisor 服务..."
sudo supervisorctl stop himart:* || true
sleep 2
success "Supervisor 服务已停止"

info "停止 Nginx..."
sudo systemctl stop nginx || true
sleep 2
success "Nginx 已停止"

# 4. 更新后端代码
echo -e "\n${YELLOW}【步骤 4/10】更新后端代码${NC}"

cd "$BACKEND_DIR"

info "获取最新代码..."
git fetch origin
git reset --hard origin/main
success "代码更新完成"

# 5. 后端依赖
echo -e "\n${YELLOW}【步骤 5/10】安装后端依赖${NC}"

info "安装 Python 包..."
pip install -r requirements.txt --no-cache-dir -q
success "Python 包安装完成"

# 6. 数据库迁移
echo -e "\n${YELLOW}【步骤 6/10】执行数据库迁移${NC}"

info "运行迁移..."
python manage.py migrate
success "数据库迁移完成"

info "收集静态文件..."
python manage.py collectstatic --noinput -q
success "静态文件收集完成"

# 7. 更新前端
echo -e "\n${YELLOW}【步骤 7/10】更新前端代码${NC}"

cd "$FRONTEND_DIR"

info "获取最新代码..."
git fetch origin
git reset --hard origin/main
success "代码更新完成"

# 8. 前端构建
echo -e "\n${YELLOW}【步骤 8/10】构建前端${NC}"

info "安装 npm 依赖..."
npm ci -q
success "npm 依赖安装完成"

info "构建前端..."
npm run build
success "前端构建完成"

# 9. 启动服务
echo -e "\n${YELLOW}【步骤 9/10】启动服务${NC}"

info "启动 Nginx..."
sudo systemctl start nginx
success "Nginx 已启动"

info "等待 2 秒..."
sleep 2

info "启动 Supervisor..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start himart:*
success "Supervisor 已启动"

# 10. 验证
echo -e "\n${YELLOW}【步骤 10/10】验证部署${NC}"

# 等待服务启动
info "等待服务启动..."
sleep 5

# 检查后端
info "检查后端服务..."
if curl -sf http://localhost:8000/api/schema/ > /dev/null; then
    success "后端服务正常"
else
    error "后端服务异常"
fi

# 检查前端
info "检查前端服务..."
if curl -sf http://localhost/ > /dev/null; then
    success "前端服务正常"
else
    error "前端服务异常"
fi

# 检查数据库
info "检查数据库连接..."
if python manage.py dbshell <<< "SELECT 1;" &> /dev/null; then
    success "数据库连接正常"
else
    error "数据库连接异常"
fi

# 最终总结
echo -e "\n${GREEN}═════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}═════════════════════════════════════${NC}\n"

echo "📊 部署信息:"
echo "  项目地址: https://mail.aitepid.crabdance.com"
echo "  API 地址: https://mail.aitepid.crabdance.com/api"
echo "  管理后台: https://mail.aitepid.crabdance.com/admin"
echo "  部署时间: $(date)"
echo "  部署日志: $LOG_FILE"
echo ""

echo "✅ 部署成功！系统已上线。"
echo ""

success "部署完成，所有服务正在运行"
