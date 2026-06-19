# 🚀 云服务器部署操作指南

**目标服务器**: 64.181.193.238  
**域名**: mail.aitepid.crabdance.com  
**操作系统**: Ubuntu 24.04  
**预计耗时**: 20-30 分钟

---

## 📋 部署前准备

### 1. 准备上传文件

将以下文件上传到云服务器的临时目录：

```bash
# 本地执行：上传项目文件到服务器
scp -r c:\app\GitCANG\NewWEB\webshop ubuntu@64.181.193.238:/tmp/himart-upload
```

**需要上传的文件**:
- ✅ backend/ (完整后端目录)
- ✅ frontend/ (完整前端目录)
- ✅ deploy-to-cloud.sh (部署脚本)

### 2. SSH 连接信息

```bash
# 连接命令
ssh ubuntu@64.181.193.238

# 使用密钥连接（如果有）
ssh -i your-key.pem ubuntu@64.181.193.238
```

---

## 🔧 第一步：连接到服务器

### 方法 1: 使用 SSH（推荐）

**Windows 用户**（使用 PowerShell 或 WSL）:
```powershell
ssh ubuntu@64.181.193.238
# 输入密码
```

**Mac/Linux 用户**:
```bash
ssh ubuntu@64.181.193.238
```

### 方法 2: 使用 PuTTY（Windows）

1. 下载 PuTTY: https://www.putty.org
2. 主机名: 64.181.193.238
3. 用户名: ubuntu
4. 连接

---

## 📤 第二步：上传项目文件

连接后，创建项目目录：

```bash
# 创建目录
mkdir -p /home/ubuntu/himart
cd /home/ubuntu

# 如果还没上传，本地执行这条命令上传：
# scp -r ./webshop ubuntu@64.181.193.238:/home/ubuntu/himart/
```

验证文件：
```bash
ls -la /home/ubuntu/himart/
# 应该看到: backend/, frontend/, deploy-to-cloud.sh 等
```

---

## 🚀 第三步：运行部署脚本

连接到服务器后，在 `/home/ubuntu` 目录执行：

```bash
# 进入项目目录
cd /home/ubuntu/himart

# 给脚本执行权限
chmod +x deploy-to-cloud.sh

# 运行部署脚本
./deploy-to-cloud.sh
```

**脚本会自动进行**:
- ✅ 系统更新和依赖安装
- ✅ 数据库创建和配置
- ✅ 后端部署和迁移
- ✅ 前端构建
- ✅ Nginx 配置
- ✅ SSL 证书配置
- ✅ Supervisor 进程管理
- ✅ 服务启动和验证

---

## 📊 部署进度监控

部署过程中，您会看到类似的输出：

```
【步骤 1/12】系统更新和依赖安装...
✓ 完成

【步骤 2/12】创建项目目录...
✓ 完成

【步骤 3/12】拉取最新代码...
✓ 完成
...
```

---

## ✅ 部署完成验证

部署完成后，脚本会输出：

```
🎉 部署完成！服务已启动
╔════════════════════════════════════════╗
║ 前端地址: https://mail.aitepid.crabdance.com
║ API 地址: https://mail.aitepid.crabdance.com/api
║ 管理后台: https://mail.aitepid.crabdance.com/admin
║ 用户名: admin
║ 密码: admin123456
╚════════════════════════════════════════╝
```

### 验证各项服务

```bash
# 1. 检查后端服务
curl http://localhost:8000/api/products/

# 2. 检查数据库连接
sudo -u ubuntu /home/ubuntu/himart/backend/venv/bin/python -c \
  "import django; django.setup(); from django.db import connection; connection.ensure_connection()"

# 3. 检查 Supervisor 状态
sudo supervisorctl status

# 4. 查看 Nginx 日志
sudo tail -20 /var/log/nginx/error.log

# 5. 查看后端日志
sudo tail -50 /var/log/supervisor/himart-backend.log
```

---

## 🌐 访问应用

部署成功后，您可以访问：

### 用户端
- **URL**: https://mail.aitepid.crabdance.com
- **功能**: 产品浏览、购物、订单、支付

### 管理后台
- **URL**: https://mail.aitepid.crabdance.com/admin
- **用户名**: admin
- **密码**: admin123456

### API 文档
- **URL**: https://mail.aitepid.crabdance.com/api/schema/
- **格式**: OpenAPI 3.0 / Swagger

---

## 🔧 常见问题排查

### 问题 1: SSL 证书生成失败

**症状**: 访问 HTTPS 时证书错误

**解决**:
```bash
# 手动生成证书
sudo certbot certonly --standalone \
  -d mail.aitepid.crabdance.com \
  -d *.aitepid.crabdance.com

# 更新 Nginx 配置中的证书路径
sudo vim /etc/nginx/sites-available/himart

# 重启 Nginx
sudo systemctl restart nginx
```

### 问题 2: 后端连接失败 (502 Bad Gateway)

**症状**: 访问 API 时 502 错误

**排查**:
```bash
# 1. 检查 Supervisor 进程
sudo supervisorctl status himart

# 2. 如果进程挂了，重启
sudo supervisorctl restart himart:*

# 3. 查看错误日志
sudo tail -100 /var/log/supervisor/himart-backend-error.log

# 4. 检查数据库连接
cd /home/ubuntu/himart/backend
source venv/bin/activate
python manage.py dbshell
\q
```

### 问题 3: 数据库连接错误

**症状**: 502 错误，日志显示数据库连接失败

**解决**:
```bash
# 1. 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 2. 检查 .env 文件中的数据库配置
cat /home/ubuntu/himart/backend/.env | grep DB_

# 3. 手动测试连接
psql -U himart -d himart_db -h localhost

# 4. 如果失败，重新创建用户
sudo -u postgres psql << EOF
DROP DATABASE himart_db;
DROP USER himart;
CREATE DATABASE himart_db;
CREATE USER himart WITH PASSWORD 'himart123';
GRANT ALL PRIVILEGES ON DATABASE himart_db TO himart;
EOF

# 5. 重新运行迁移
cd /home/ubuntu/himart/backend
source venv/bin/activate
python manage.py migrate
```

### 问题 4: 前端页面无法加载

**症状**: 访问首页时显示 404

**解决**:
```bash
# 1. 检查前端构建文件
ls -la /home/ubuntu/himart/frontend/dist/

# 2. 如果为空，重新构建
cd /home/ubuntu/himart/frontend
npm ci
npm run build

# 3. 检查 Nginx 配置
sudo cat /etc/nginx/sites-available/himart | grep -A5 "location /"

# 4. 重启 Nginx
sudo systemctl restart nginx
```

### 问题 5: Redis 连接失败

**症状**: 缓存功能不工作

**解决**:
```bash
# 1. 检查 Redis 状态
redis-cli ping
# 应该返回 PONG

# 2. 如果失败，重启 Redis
sudo systemctl restart redis-server

# 3. 检查 Redis 配置
redis-cli CONFIG GET maxmemory
redis-cli CONFIG GET "*bind*"
```

---

## 🔄 部署后更新

当需要更新应用时：

```bash
# 1. 连接到服务器
ssh ubuntu@64.181.193.238

# 2. 进入项目目录
cd /home/ubuntu/himart

# 3. 拉取最新代码
git pull origin main

# 4. 后端更新
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
deactivate

# 5. 前端更新
cd ../frontend
npm ci
npm run build

# 6. 重启服务
sudo supervisorctl restart himart:*
sudo systemctl restart nginx
```

---

## 📊 监控和维护

### 查看服务状态

```bash
# Supervisor 进程状态
sudo supervisorctl status

# Nginx 状态
sudo systemctl status nginx

# 系统资源
free -h        # 内存
df -h          # 磁盘
top -bn1       # CPU

# 网络连接
netstat -tuln | grep LISTEN
```

### 查看日志

```bash
# 后端日志
tail -f /var/log/supervisor/himart-backend.log

# Nginx 错误日志
tail -f /var/log/nginx/error.log

# Nginx 访问日志
tail -f /var/log/nginx/access.log

# 系统日志
journalctl -u nginx -f
journalctl -u postgresql -f
```

### 定期维护

```bash
# 数据库备份
pg_dump -U himart himart_db | gzip > /var/backups/db_$(date +%Y%m%d).sql.gz

# 清理日志
sudo journalctl --vacuum=time=30d

# 检查磁盘使用
du -sh /home/ubuntu/himart/*
du -sh /var/log/*

# 更新系统
sudo apt-get update && sudo apt-get upgrade -y
```

---

## 🔐 安全检查

部署后立即进行安全检查：

```bash
# 1. 更改管理员密码
python manage.py changepassword admin

# 2. 检查 HTTPS 有效性
curl -I https://mail.aitepid.crabdance.com

# 3. 检查安全头
curl -I https://mail.aitepid.crabdance.com | grep -i "Strict\|X-Content"

# 4. 禁用 DEBUG 模式（应该已禁用）
grep DEBUG /home/ubuntu/himart/backend/.env

# 5. 检查密钥安全性
head -1 /home/ubuntu/himart/backend/.env | wc -c
# 应该 > 50 字符
```

---

## ✅ 部署检查清单

部署完成后检查：

- [ ] 前端页面可访问（HTTPS）
- [ ] API 端点可访问
- [ ] 管理后台可登录
- [ ] 数据库连接正常
- [ ] Redis 缓存工作
- [ ] SSL 证书有效
- [ ] 日志正常记录
- [ ] 性能指标正常
- [ ] 备份已配置
- [ ] 监控已启用

---

## 📞 快速参考

### 紧急停止

```bash
# 停止所有服务
sudo supervisorctl stop himart:*
sudo systemctl stop nginx
```

### 紧急启动

```bash
# 启动所有服务
sudo systemctl start nginx
sudo supervisorctl start himart:*
```

### 完全重启

```bash
# 重启所有服务
sudo supervisorctl restart himart:*
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

---

## 🎉 成功！

如果看到以下内容，说明部署成功：

✅ 前端页面加载正常  
✅ API 返回 200 状态码  
✅ 管理后台可登录  
✅ 数据库有数据  
✅ 缓存工作正常  

---

**部署日期**: 2026-06-19  
**版本**: v1.0 Production  
**状态**: 生产就绪 ✅

---

## 🆘 需要帮助？

1. 查看日志文件
2. 检查常见问题章节
3. 验证服务状态
4. 查看服务器资源使用情况

**重要**: 保存此指南以备将来参考！
