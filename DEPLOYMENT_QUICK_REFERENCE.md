# 🚀 Oracle 云部署 - 快速参考

**服务器:** Ubuntu 20.04/22.04 LTS  
**IP:** `64.181.193.238`  
**用户:** `ubuntu`  

---

## ⚡ 最快部署方式 (5 分钟)

### 1. 准备 SSH 密钥

```bash
# 本地机器上，确保有 SSH 密钥
ls -la ~/.ssh/id_rsa
```

### 2. 运行自动部署脚本

```bash
# 修改脚本中的 SSH_KEY 路径
nano deploy-to-oracle.sh  # 改 SSH_KEY 变量

# 赋予执行权限并运行
chmod +x deploy-to-oracle.sh
./deploy-to-oracle.sh
```

**脚本会自动:**
- ✅ 更新系统
- ✅ 安装 Python/Node/DB/Redis
- ✅ 克隆项目
- ✅ 配置虚拟环境
- ✅ 运行数据库迁移
- ✅ 构建前端
- ✅ 启动所有服务

---

## 🔧 手动部署步骤 (30 分钟)

### 连接服务器

```bash
ssh -i ~/.ssh/your-key.pem ubuntu@64.181.193.238
```

### 安装依赖

```bash
sudo apt-get update && sudo apt-get install -y \
  python3-pip python3-venv nodejs npm postgresql redis-server \
  build-essential libssl-dev libffi-dev git curl wget nginx supervisor
```

### 后端配置

```bash
cd ~ && git clone https://github.com/your-username/himart.git
cd himart/backend

# 虚拟环境
python3 -m venv venv && source venv/bin/activate

# 依赖和迁移
pip install -r requirements.txt
cp ../backend/.env.example .env
python manage.py migrate

# 创建管理员 (可选)
python manage.py createsuperuser
```

### 前端配置

```bash
cd ../frontend
npm install
npm run build
npm install -g serve
```

### 数据库设置

```bash
sudo -u postgres psql << EOF
  CREATE USER himart_user WITH PASSWORD 'himart_password';
  CREATE DATABASE himart_db OWNER himart_user;
  GRANT ALL PRIVILEGES ON DATABASE himart_db TO himart_user;
EOF
```

### Nginx 配置

```bash
sudo cp nginx.conf /etc/nginx/sites-available/himart
sudo ln -s /etc/nginx/sites-available/himart /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

### Supervisor 配置

```bash
sudo cp supervisor-himart.conf /etc/supervisor/conf.d/
sudo supervisorctl reread && sudo supervisorctl update
sudo supervisorctl start himart:*
```

### 启动服务

```bash
# Redis
sudo systemctl start redis-server

# 验证
sudo supervisorctl status
curl http://localhost:8000/api/products/
```

---

## ✅ 验证部署

```bash
# 检查应用是否运行
curl http://64.181.193.238/
curl http://64.181.193.238/api/products/
curl http://64.181.193.238/admin/

# 检查进程
sudo supervisorctl status

# 查看日志
sudo tail -f /var/log/supervisor/himart-backend.log
sudo tail -f /var/log/supervisor/himart-frontend.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📍 访问应用

| 地址 | 说明 |
|-----|------|
| `http://64.181.193.238` | 前端应用 |
| `http://64.181.193.238/api` | 后端 API |
| `http://64.181.193.238/admin` | Django 管理后台 |

---

## 🔒 配置 HTTPS (必做)

```bash
# 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot certonly --nginx -d yourdomain.com

# 修改 nginx.conf 启用 HTTPS
sudo vi /etc/nginx/sites-available/himart
# 取消注释 HTTPS 部分，更新证书路径

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 🐛 常见问题

### 后端启动失败

```bash
# 查看错误
sudo supervisorctl tail himart-backend -f

# 常见原因和解决:
# 1. 数据库连接失败
#    → 检查 .env 中的 DATABASE_URL
#    → sudo systemctl status postgresql

# 2. Redis 连接失败
#    → sudo systemctl start redis-server

# 3. 端口被占用
#    → sudo lsof -i :8000
```

### 前端无法访问

```bash
# 检查 serve 进程
ps aux | grep serve

# 检查构建
ls -la ~/himart/frontend/dist/

# 查看日志
sudo tail -f /var/log/supervisor/himart-frontend.log
```

---

## 📊 关键文件位置

```
/home/ubuntu/himart/              # 项目根目录
├── backend/
│   ├── .env                      # 生产配置 (需要修改)
│   └── venv/bin/python           # Python 解释器
├── frontend/
│   └── dist/                     # 构建输出

/etc/nginx/sites-available/himart    # Nginx 配置
/etc/supervisor/conf.d/himart.conf   # Supervisor 配置

/var/log/supervisor/                 # 日志目录
```

---

## 🔄 更新部署

```bash
cd ~/himart

# 拉取最新代码
git pull origin main

# 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
sudo supervisorctl restart himart-backend

# 更新前端
cd ../frontend
npm install
npm run build
sudo supervisorctl restart himart-frontend
```

---

## 📈 性能优化

```bash
# 1. 启用 Gzip
sudo vi /etc/nginx/nginx.conf
# 修改 gzip on;

# 2. 增加 worker 进程
# worker_processes auto;

# 3. PostgreSQL 优化
sudo vi /etc/postgresql/*/main/postgresql.conf
# shared_buffers = 1GB
# effective_cache_size = 3GB

# 4. Redis 监控
redis-cli MONITOR
```

---

## 📞 快速命令

```bash
# SSH 连接
ssh -i ~/.ssh/your-key.pem ubuntu@64.181.193.238

# 查看日志
sudo tail -f /var/log/supervisor/himart-backend.log

# 重启服务
sudo supervisorctl restart himart:*

# 查看进程状态
ps aux | grep python
ps aux | grep node

# 检查端口
sudo netstat -tlnp | grep -E ':8000|:3000|:80|:443'

# 清理缓存
redis-cli FLUSHALL
```

---

## 🎯 预期结果

部署成功后:

```
✓ 前端应用: http://64.181.193.238
✓ 后端 API: http://64.181.193.238/api
✓ 管理后台: http://64.181.193.238/admin
✓ 数据库: PostgreSQL 运行中
✓ 缓存: Redis 运行中
✓ 所有进程: Supervisor 管理
```

---

**部署日期:** 2026-06-19  
**配置文件:** 已提供所有配置文件  
**支持:** 查看 DEPLOYMENT_GUIDE.md 获取详细说明
