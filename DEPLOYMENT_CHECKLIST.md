# 🚀 Hi Mart 生产部署检查清单

**部署日期**: 2026-06-19  
**环境**: Oracle Cloud Ubuntu 24.04  
**服务器地址**: http://64.181.193.238

---

## 📋 部署前准备

### 环境配置检查

- [ ] **Python 版本**: Python 3.10+ 已安装
  ```bash
  python3 --version
  ```

- [ ] **数据库**: PostgreSQL 13+ 已安装并运行
  ```bash
  psql --version
  sudo systemctl status postgresql
  ```

- [ ] **缓存**: Redis 已安装并运行
  ```bash
  redis-cli --version
  redis-cli ping  # 应返回 PONG
  ```

- [ ] **Node.js**: Node.js 18+ 已安装
  ```bash
  node --version
  npm --version
  ```

- [ ] **Web 服务器**: Nginx 已安装
  ```bash
  nginx -v
  ```

- [ ] **进程管理**: Supervisor 已安装
  ```bash
  supervisord --version
  ```

---

## 🔐 安全配置检查

- [ ] **密钥管理**
  - [ ] `SECRET_KEY` 已更新为强随机字符串
  - [ ] `DEBUG = False` 在生产环境
  - [ ] `ALLOWED_HOSTS` 配置正确
  ```python
  ALLOWED_HOSTS = ['mail.aitepid.crabdance.com', '64.181.193.238']
  ```

- [ ] **HTTPS/SSL**
  - [ ] SSL 证书已获得
  - [ ] 证书文件位置: `/etc/ssl/certs/`
  - [ ] 私钥位置: `/etc/ssl/private/`
  ```bash
  ls -la /etc/ssl/certs/cert.pem
  ls -la /etc/ssl/private/key.pem
  ```

- [ ] **安全头部**
  ```python
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  SECURE_BROWSER_XSS_FILTER = True
  X_FRAME_OPTIONS = 'DENY'
  SECURE_CONTENT_SECURITY_POLICY = {
      'default-src': ("'self'",),
  }
  ```

- [ ] **CORS 配置**
  ```python
  CORS_ALLOWED_ORIGINS = [
      'https://mail.aitepid.crabdance.com',
      'http://64.181.193.238',
  ]
  ```

- [ ] **数据库凭证**
  - [ ] 已更改默认密码
  - [ ] 使用环境变量存储敏感信息
  ```bash
  echo "DB_PASSWORD=strong_password_here" >> ~/.env
  ```

---

## 📦 依赖检查

### 后端依赖

- [ ] **安装 Python 包**
  ```bash
  cd ~/himart/backend
  pip install -r requirements.txt --no-cache-dir
  ```

- [ ] **验证关键包**
  ```bash
  pip list | grep -E 'Django|djangorestframework|psycopg2|redis|gunicorn'
  ```

### 前端依赖

- [ ] **安装 npm 包**
  ```bash
  cd ~/himart/frontend
  npm ci  # 使用 ci 代替 install 以获得确定的版本
  ```

- [ ] **构建前端**
  ```bash
  npm run build
  ```

- [ ] **验证构建输出**
  ```bash
  ls -la dist/
  du -sh dist/  # 检查大小
  ```

---

## 🗄️ 数据库准备

- [ ] **数据库创建**
  ```bash
  sudo -u postgres createdb himart_db
  sudo -u postgres createuser himart
  sudo -u postgres psql
  # 在 psql 中执行:
  # ALTER USER himart WITH PASSWORD 'secure_password';
  # GRANT ALL PRIVILEGES ON DATABASE himart_db TO himart;
  ```

- [ ] **数据库迁移**
  ```bash
  cd ~/himart/backend
  python manage.py migrate
  ```

- [ ] **创建超级用户**
  ```bash
  python manage.py createsuperuser
  # 输入用户名、邮箱、密码
  ```

- [ ] **加载初始数据**（可选）
  ```bash
  python manage.py loaddata initial_data.json
  ```

- [ ] **创建索引**
  ```bash
  python manage.py sqlsequencereset apps.* | python manage.py dbshell
  ```

---

## 🔧 应用程序配置

### 后端配置

- [ ] **创建 .env 文件**
  ```bash
  cat > ~/himart/backend/.env << EOF
  DEBUG=False
  SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
  ALLOWED_HOSTS=mail.aitepid.crabdance.com,64.181.193.238
  
  DB_NAME=himart_db
  DB_USER=himart
  DB_PASSWORD=secure_password
  DB_HOST=localhost
  DB_PORT=5432
  
  REDIS_URL=redis://localhost:6379/0
  
  STRIPE_PUBLIC_KEY=pk_test_...
  STRIPE_SECRET_KEY=sk_test_...
  
  MPESA_CONSUMER_KEY=...
  MPESA_CONSUMER_SECRET=...
  EOF
  chmod 600 ~/himart/backend/.env
  ```

- [ ] **静态文件收集**
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] **检查静态文件**
  ```bash
  ls -la staticfiles/
  ```

### 前端配置

- [ ] **API 端点配置**
  ```typescript
  // frontend/src/api/client.ts
  const API_BASE = process.env.VITE_API_URL || 'https://api.example.com'
  ```

- [ ] **构建环境变量**
  ```bash
  cat > ~/himart/frontend/.env.production << EOF
  VITE_API_URL=https://mail.aitepid.crabdance.com/api
  EOF
  ```

---

## 🌐 Web 服务器配置

### Nginx 配置

- [ ] **创建 Nginx 配置**
  ```bash
  sudo cp nginx.conf /etc/nginx/sites-available/himart
  sudo ln -s /etc/nginx/sites-available/himart /etc/nginx/sites-enabled/
  ```

- [ ] **测试配置**
  ```bash
  sudo nginx -t
  ```

- [ ] **启动 Nginx**
  ```bash
  sudo systemctl start nginx
  sudo systemctl enable nginx  # 开机自启
  ```

- [ ] **验证 Nginx**
  ```bash
  sudo systemctl status nginx
  ```

---

## 👥 进程管理配置

### Supervisor 配置

- [ ] **创建 Supervisor 配置**
  ```bash
  sudo cat > /etc/supervisor/conf.d/himart.conf << EOF
  [program:himart-backend]
  directory=/home/ubuntu/himart/backend
  command=gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 4 --timeout 120
  autostart=true
  autorestart=true
  redirect_stderr=true
  stdout_logfile=/var/log/supervisor/himart-backend.log
  user=ubuntu
  environment=PATH="/home/ubuntu/himart/backend/venv/bin"
  
  [group:himart]
  programs=himart-backend
  EOF
  ```

- [ ] **更新 Supervisor**
  ```bash
  sudo supervisorctl reread
  sudo supervisorctl update
  ```

- [ ] **启动服务**
  ```bash
  sudo supervisorctl start himart:*
  ```

- [ ] **验证服务**
  ```bash
  sudo supervisorctl status
  ```

---

## 📊 监控和日志

- [ ] **配置日志轮换**
  ```bash
  sudo cat > /etc/logrotate.d/himart << EOF
  /var/log/supervisor/himart-*.log {
      daily
      missingok
      rotate 14
      compress
      delaycompress
      notifempty
      copytruncate
  }
  EOF
  ```

- [ ] **启用监控脚本**
  ```bash
  chmod +x ~/himart/monitoring.sh
  sudo crontab -e
  # 添加: */5 * * * * ~/himart/monitoring.sh >> /var/log/himart-monitor.log
  ```

- [ ] **测试监控**
  ```bash
  curl http://localhost:8000/api/products/
  tail -f /var/log/supervisor/himart-backend.log
  ```

---

## 🔄 备份配置

- [ ] **数据库备份脚本**
  ```bash
  cat > ~/himart/backup-db.sh << EOF
  #!/bin/bash
  BACKUP_DIR="/var/backups/himart"
  mkdir -p $BACKUP_DIR
  pg_dump -U himart himart_db | gzip > $BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sql.gz
  find $BACKUP_DIR -mtime +7 -delete  # 删除 7 天前的备份
  EOF
  chmod +x ~/himart/backup-db.sh
  ```

- [ ] **安排定时备份**
  ```bash
  crontab -e
  # 添加: 0 2 * * * ~/himart/backup-db.sh
  ```

- [ ] **测试备份**
  ```bash
  ~/himart/backup-db.sh
  ls -la /var/backups/himart/
  ```

---

## ✅ 功能测试

- [ ] **后端 API 测试**
  ```bash
  curl -s https://mail.aitepid.crabdance.com/api/schema/ | head -20
  curl -s https://mail.aitepid.crabdance.com/api/products/ | python -m json.tool
  ```

- [ ] **前端加载测试**
  ```bash
  curl -s https://mail.aitepid.crabdance.com/ | grep -q '<title>' && echo "✓ Frontend OK"
  ```

- [ ] **完整端到端测试**
  ```bash
  cd ~/himart/backend
  python e2e_tests.py --production
  ```

- [ ] **性能基准测试**
  ```bash
  python performance_benchmark.py
  ```

---

## 🔍 最终检查

- [ ] **DNS 解析**
  ```bash
  nslookup mail.aitepid.crabdance.com
  ```

- [ ] **SSL 证书验证**
  ```bash
  openssl s_client -connect mail.aitepid.crabdance.com:443
  ```

- [ ] **HTTP → HTTPS 重定向**
  ```bash
  curl -I http://mail.aitepid.crabdance.com
  # 应该返回 301 重定向到 HTTPS
  ```

- [ ] **API 响应时间**
  ```bash
  time curl -s https://mail.aitepid.crabdance.com/api/products/ > /dev/null
  # 应该 < 200ms
  ```

- [ ] **错误日志检查**
  ```bash
  sudo tail -50 /var/log/supervisor/himart-backend.log
  sudo tail -50 /var/log/nginx/error.log
  ```

---

## 🎉 部署完成

部署成功指标：

- ✓ 所有服务正在运行
- ✓ 前端和 API 可以访问
- ✓ SSL 有效且重定向正常
- ✓ 数据库连接正常
- ✓ 缓存服务正常
- ✓ 日志正在记录
- ✓ 备份已配置
- ✓ 监控已启用

---

## 📞 部署后操作

### 立即操作

1. **监控系统状态**
   ```bash
   watch -n 5 'sudo supervisorctl status'
   tail -f /var/log/supervisor/himart-backend.log
   ```

2. **设置监控告警**
   - 配置 Prometheus/Grafana
   - 设置邮件告警

3. **性能基准测试**
   ```bash
   python performance_benchmark.py > baseline.txt
   ```

### 定期维护

- 每周检查备份
- 每月更新依赖包
- 每月审查日志
- 每季度性能评估

### 故障排查

常见问题：
- API 502 错误 → 检查 Gunicorn/Supervisor
- 数据库连接错误 → 检查 PostgreSQL 服务
- 静态文件 404 → 运行 `collectstatic`
- 缓存问题 → 清空 Redis

---

**部署状态**: ⏳ 待执行  
**负责人**: DevOps Team  
**最后更新**: 2026-06-19
