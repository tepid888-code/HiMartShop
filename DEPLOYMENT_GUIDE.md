# Oracle 云服务器部署指南

## 📋 前提条件

- Oracle 云 Ubuntu 20.04/22.04 LTS 实例
- SSH 密钥对已配置
- 服务器 IP: `64.181.193.238`
- SSH 用户: `ubuntu`

---

## 🚀 快速部署（推荐）

### 方案 A：使用自动部署脚本（最快）

```bash
# 1. 修改脚本中的 SSH 密钥路径
vi deploy-to-oracle.sh
# 修改: SSH_KEY="$HOME/.ssh/your-key.pem"

# 2. 赋予执行权限
chmod +x deploy-to-oracle.sh

# 3. 运行部署脚本
./deploy-to-oracle.sh
```

**脚本做了什么:**
- ✅ 更新系统包
- ✅ 安装 Python、Node.js、PostgreSQL、Redis
- ✅ 克隆项目仓库
- ✅ 配置虚拟环境
- ✅ 运行数据库迁移
- ✅ 构建前端
- ✅ 启动服务

**预计时间:** 10-15 分钟

---

## 📝 手动部署步骤

### 1️⃣ 连接到服务器

```bash
ssh -i ~/.ssh/your-key.pem ubuntu@64.181.193.238
```

### 2️⃣ 更新系统

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3️⃣ 安装依赖

```bash
# Python 和开发工具
sudo apt-get install -y \
    python3-pip python3-venv python3-dev \
    build-essential libssl-dev libffi-dev

# Node.js
sudo apt-get install -y nodejs npm

# 数据库
sudo apt-get install -y postgresql postgresql-contrib

# 缓存
sudo apt-get install -y redis-server

# 其他
sudo apt-get install -y git curl wget
```

### 4️⃣ 克隆项目

```bash
cd ~
git clone https://github.com/your-username/himart.git
cd himart
```

### 5️⃣ 配置后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-change-this
ALLOWED_HOSTS=64.181.193.238,localhost,127.0.0.1

DATABASE_URL=postgresql://himart_user:himart_password@localhost:5432/himart_db
REDIS_URL=redis://localhost:6379/0

# 可选的第三方服务
# MPESA_CONSUMER_KEY=xxx
# STRIPE_API_KEY=xxx
EOF

# 运行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 6️⃣ 配置前端

```bash
cd ../frontend

# 安装依赖
npm install

# 创建 .env 文件
cat > .env << 'EOF'
VITE_API_URL=http://64.181.193.238:8000/api
EOF

# 构建
npm run build
```

### 7️⃣ 配置数据库

```bash
# 启动 PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库用户和数据库
sudo -u postgres psql << 'EOF'
CREATE USER himart_user WITH PASSWORD 'himart_password';
CREATE DATABASE himart_db OWNER himart_user;
GRANT ALL PRIVILEGES ON DATABASE himart_db TO himart_user;
\c himart_db
GRANT ALL PRIVILEGES ON SCHEMA public TO himart_user;
EOF
```

### 8️⃣ 配置 Nginx

```bash
# 安装 Nginx
sudo apt-get install -y nginx

# 复制配置文件
sudo cp nginx.conf /etc/nginx/sites-available/himart

# 启用配置
sudo ln -s /etc/nginx/sites-available/himart /etc/nginx/sites-enabled/

# 删除默认配置
sudo rm /etc/nginx/sites-enabled/default

# 检查配置
sudo nginx -t

# 启动 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 9️⃣ 配置进程管理 (Supervisor)

```bash
# 安装 Supervisor
sudo apt-get install -y supervisor

# 复制配置
sudo cp supervisor-himart.conf /etc/supervisor/conf.d/

# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start himart:*

# 查看状态
sudo supervisorctl status
```

### 🔟 启动 Redis

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

---

## ✅ 验证部署

### 检查服务状态

```bash
# 检查进程
sudo supervisorctl status

# 检查 Nginx
sudo systemctl status nginx

# 检查 PostgreSQL
sudo systemctl status postgresql

# 检查 Redis
sudo systemctl status redis-server
```

### 测试 API

```bash
# 测试后端 API
curl http://64.181.193.238:8000/api/products/

# 测试管理后台
curl http://64.181.193.238:8000/admin/

# 测试前端
curl http://64.181.193.238:80/
```

### 访问应用

```
🌐 前端: http://64.181.193.238
🔗 后端 API: http://64.181.193.238/api
👨‍💼 管理后台: http://64.181.193.238/admin
```

---

## 🔒 配置 HTTPS (SSL)

### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot certonly --nginx -d 64.181.193.238

# 或使用域名
sudo certbot certonly --nginx -d yourdomain.com

# 修改 Nginx 配置启用 HTTPS
sudo vi /etc/nginx/sites-available/himart
# 取消注释 HTTPS 部分

# 重启 Nginx
sudo systemctl restart nginx

# 自动续期证书
sudo systemctl enable certbot.timer
```

### 在 nginx.conf 中更新证书路径

```nginx
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

---

## 📊 查看日志

```bash
# Supervisor 后端日志
sudo tail -f /var/log/supervisor/himart-backend.log

# Supervisor 前端日志
sudo tail -f /var/log/supervisor/himart-frontend.log

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 系统日志
sudo journalctl -f
```

---

## 🐛 故障排查

### 后端无法启动

```bash
# 检查错误
sudo supervisorctl tail himart-backend -f

# 手动运行检查
cd ~/himart/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# 常见原因:
# - 数据库连接失败 → 检查 DATABASE_URL
# - Redis 连接失败 → sudo systemctl start redis-server
# - 端口被占用 → sudo lsof -i :8000
```

### 前端无法访问

```bash
# 检查 serve 是否运行
ps aux | grep serve

# 检查构建是否成功
cd ~/himart/frontend
ls -la dist/

# 重新构建
npm run build

# 手动启动
npx serve -s dist -l 3000
```

### 数据库连接错误

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 测试连接
psql -U himart_user -d himart_db -h localhost

# 查看数据库日志
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Nginx 配置错误

```bash
# 检查配置语法
sudo nginx -t

# 查看 Nginx 错误
sudo tail -f /var/log/nginx/error.log

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 🔄 更新部署

### 拉取最新代码

```bash
cd ~/himart
git pull origin main
```

### 更新后端

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate

# 重启后端
sudo supervisorctl restart himart-backend
```

### 更新前端

```bash
cd frontend
npm install
npm run build

# Supervisor 会自动重启
```

---

## 📈 性能优化

### 1. 启用 Gzip 压缩

在 nginx.conf 中添加:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 2. 增加 Nginx 工作进程

```bash
# 检查 CPU 核心数
nproc

# 修改 nginx.conf
sudo vi /etc/nginx/nginx.conf
# worker_processes auto;
```

### 3. 调整 PostgreSQL

```bash
# 获取服务器内存
free -h

# 编辑 PostgreSQL 配置
sudo vi /etc/postgresql/*/main/postgresql.conf

# 关键参数 (示例 4GB 内存):
# shared_buffers = 1GB
# effective_cache_size = 3GB
# maintenance_work_mem = 256MB
# checkpoint_completion_target = 0.9
# wal_buffers = 16MB
```

### 4. Redis 优化

```bash
# 查看 Redis 配置
redis-cli CONFIG GET "*"

# 监控 Redis
redis-cli MONITOR

# 清理内存
redis-cli FLUSHDB
```

---

## 🔐 安全建议

### 1. 防火墙配置

```bash
# 安装 UFW
sudo apt-get install -y ufw

# 开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# 启用防火墙
sudo ufw enable
```

### 2. SSH 安全加固

```bash
# 禁用密码登录
sudo vi /etc/ssh/sshd_config
# PasswordAuthentication no

# 重启 SSH
sudo systemctl restart ssh
```

### 3. 更新密钥

```bash
# 生成新的 Django SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 更新 .env
vi ~/himart/backend/.env
```

### 4. 定期备份

```bash
# 备份数据库
pg_dump -U himart_user -d himart_db > himart_backup_$(date +%Y%m%d).sql

# 备份上传到云存储
# 配置定时任务...
```

---

## 📞 常用命令速查表

```bash
# 服务管理
sudo systemctl start|stop|restart|status nginx
sudo systemctl start|stop|restart|status postgresql
sudo systemctl start|stop|restart|status redis-server
sudo supervisorctl start|stop|restart|status himart:*

# 进程检查
ps aux | grep python
ps aux | grep node
sudo lsof -i :8000
sudo lsof -i :3000
sudo lsof -i :80

# 日志查看
tail -f /var/log/supervisor/himart-backend.log
tail -f /var/log/supervisor/himart-frontend.log
sudo tail -f /var/log/nginx/error.log

# 数据库操作
psql -U himart_user -d himart_db
python manage.py shell

# 代码更新
cd ~/himart && git pull origin main
```

---

## ✨ 预期结果

部署成功后，你应该能够访问:

```
✓ 前端应用: http://64.181.193.238
✓ API 文档: http://64.181.193.238/api/schema/
✓ 管理后台: http://64.181.193.238/admin
✓ 产品列表: http://64.181.193.238/api/products/
```

---

**部署日期:** 2026-06-19  
**系统:** Ubuntu 20.04/22.04 LTS  
**监控:** Nginx + Supervisor + PostgreSQL + Redis
