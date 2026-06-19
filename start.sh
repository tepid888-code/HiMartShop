#!/bin/bash

# Hi Mart 快速启动脚本
# 用途: 本地开发和生产环境快速启动

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ========== 配置 ==========
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
ENVIRONMENT="${1:-dev}"  # dev 或 production

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Hi Mart 快速启动脚本${NC}"
echo -e "${BLUE}环境: $ENVIRONMENT${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# ========== 函数定义 ==========

start_redis() {
    echo -e "${YELLOW}[*] 启动 Redis...${NC}"
    if command -v redis-server &> /dev/null; then
        redis-server --daemonize yes
        echo -e "${GREEN}✓ Redis 已启动${NC}"
    else
        echo -e "${RED}✗ Redis 未安装${NC}"
        return 1
    fi
}

start_backend() {
    echo -e "${YELLOW}[*] 启动后端服务...${NC}"
    cd "$BACKEND_DIR"

    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 检查依赖
    if ! python -c "import django" 2>/dev/null; then
        echo "安装依赖..."
        pip install -q -r requirements.txt
    fi

    # 运行迁移
    echo "运行数据库迁移..."
    python manage.py migrate --noinput 2>/dev/null || true

    # 启动服务器
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "启动 gunicorn (生产环境)..."
        pip install -q gunicorn
        gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --daemon
    else
        echo "启动 Django 开发服务器..."
        python manage.py runserver 0.0.0.0:8000 &
    fi

    echo -e "${GREEN}✓ 后端已启动 (http://localhost:8000)${NC}"
    cd "$PROJECT_DIR"
}

start_frontend() {
    echo -e "${YELLOW}[*] 启动前端服务...${NC}"
    cd "$FRONTEND_DIR"

    # 检查依赖
    if [ ! -d "node_modules" ]; then
        echo "安装 npm 依赖..."
        npm install -q
    fi

    # 创建 .env 文件
    if [ ! -f ".env" ]; then
        echo "创建 .env 文件..."
        cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000/api
EOF
    fi

    # 启动服务器
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "构建前端 (生产环境)..."
        npm run build -q
        echo "启动生产服务器..."
        npm install -g -q serve
        serve -s dist -l 3000 &
    else
        echo "启动 Vite 开发服务器..."
        npm run dev &
    fi

    echo -e "${GREEN}✓ 前端已启动 (http://localhost:3000 或 http://localhost:5173)${NC}"
    cd "$PROJECT_DIR"
}

stop_services() {
    echo -e "${YELLOW}[*] 停止所有服务...${NC}"

    # 停止 Django
    if command -v pgrep &> /dev/null; then
        pgrep -f "runserver" && pkill -f "runserver" && echo "✓ 已停止 Django" || true
        pgrep -f "gunicorn" && pkill -f "gunicorn" && echo "✓ 已停止 Gunicorn" || true
    fi

    # 停止 Node 进程
    if command -v pgrep &> /dev/null; then
        pgrep -f "serve" && pkill -f "serve" && echo "✓ 已停止前端服务器" || true
        pgrep -f "vite" && pkill -f "vite" && echo "✓ 已停止 Vite" || true
    fi

    # 停止 Redis
    redis-cli shutdown 2>/dev/null && echo "✓ 已停止 Redis" || true

    echo -e "${GREEN}✓ 所有服务已停止${NC}"
}

show_status() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}服务状态${NC}"
    echo -e "${BLUE}================================${NC}"

    # 检查后端
    if curl -s http://localhost:8000/api/products/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 后端 API: http://localhost:8000/api${NC}"
    else
        echo -e "${RED}✗ 后端 API 未运行${NC}"
    fi

    # 检查前端
    if curl -s http://localhost:3000 > /dev/null 2>&1 || \
       curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 前端: http://localhost:3000 或 http://localhost:5173${NC}"
    else
        echo -e "${RED}✗ 前端未运行${NC}"
    fi

    # 检查 Redis
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis: 运行中${NC}"
    else
        echo -e "${RED}✗ Redis 未运行${NC}"
    fi

    # 检查数据库
    if cd "$BACKEND_DIR" && source venv/bin/activate 2>/dev/null && \
       python manage.py dbshell --no-input < /dev/null > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 数据库: 连接成功${NC}"
    else
        echo -e "${RED}✗ 数据库: 连接失败${NC}"
    fi
}

show_help() {
    cat << EOF
用法: $0 [命令] [环境]

命令:
  start        启动所有服务 (默认)
  stop         停止所有服务
  status       显示服务状态
  backend      仅启动后端
  frontend     仅启动前端
  redis        仅启动 Redis
  logs         显示日志
  shell        进入 Django shell
  help         显示此帮助信息

环境:
  dev          开发环境 (默认)
  production   生产环境

示例:
  $0                    # 开发环境启动所有服务
  $0 start production   # 生产环境启动
  $0 stop              # 停止所有服务
  $0 status            # 查看服务状态
EOF
}

# ========== 主逻辑 ==========

case "${2:-start}" in
    start)
        start_redis
        start_backend
        start_frontend
        echo ""
        echo -e "${GREEN}================================${NC}"
        echo -e "${GREEN}✓ 所有服务已启动${NC}"
        echo -e "${GREEN}================================${NC}"
        echo ""
        show_status
        echo ""
        echo "提示: 运行 '$0 stop' 来停止所有服务"
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    backend)
        start_redis
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    redis)
        start_redis
        ;;
    logs)
        echo "后端日志:"
        tail -f "$BACKEND_DIR"/debug.log 2>/dev/null || echo "未找到日志文件"
        ;;
    shell)
        cd "$BACKEND_DIR"
        source venv/bin/activate
        python manage.py shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $2${NC}"
        show_help
        exit 1
        ;;
esac
