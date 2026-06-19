# Hi Mart 项目安装指南

## 系统要求

- Docker和Docker Compose (推荐)
- 或以下条件用于本地开发:
  - Python 3.11+
  - Node.js 18+ 和 npm
  - PostgreSQL 15+
  - Redis 7+

## 方式1: 使用Docker (推荐用于快速启动)

### 步骤1: 准备环境文件

```bash
cd webshop

# 复制后端环境配置
cp backend/.env.example backend/.env

# 复制前端环境配置
cp frontend/.env.example frontend/.env
```

### 步骤2: 启动Docker容器

```bash
docker-compose up -d
```

这将启动以下服务:
- PostgreSQL 数据库
- Redis 缓存
- Django 后端 (http://localhost:8000)
- Vue 3 前端 (http://localhost:5173)

### 步骤3: 初始化数据库

```bash
# 运行数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户 (用于访问admin面板)
docker-compose exec backend python manage.py createsuperuser

# 创建演示数据 (可选)
docker-compose exec backend python manage.py shell
```

### 步骤4: 访问应用

- **前端**: http://localhost:5173
- **后端API**: http://localhost:8000/api
- **API文档**: http://localhost:8000/api/docs/
- **Admin面板**: http://localhost:8000/admin

---

## 方式2: 本地开发 (需要手动配置所有服务)

### 后端设置

#### 2.1 创建虚拟环境

```bash
cd backend
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.3 配置数据库

编辑 `backend/.env` 文件:

```env
DEBUG=True
DATABASE_URL=postgresql://himart:himart123@localhost:5432/himart_db
DB_NAME=himart_db
DB_USER=himart
DB_PASSWORD=himart123
DB_HOST=localhost
DB_PORT=5432
```

确保PostgreSQL正在运行并创建数据库:

```bash
# 使用psql
createdb himart_db
createuser -P himart  # 设置密码为 himart123
```

或使用pgAdmin等GUI工具。

#### 2.4 运行迁移

```bash
python manage.py migrate
```

#### 2.5 创建超级用户

```bash
python manage.py createsuperuser
```

输入:
- Username: admin
- Email: admin@example.com
- Password: (设置密码)

#### 2.6 启动后端服务器

```bash
python manage.py runserver
```

后端将在 http://localhost:8000 运行

#### 2.7 访问Admin面板

访问 http://localhost:8000/admin
使用刚创建的超级用户账户登录

### 前端设置

#### 2.1 进入前端目录

```bash
cd frontend
```

#### 2.2 安装依赖

```bash
npm install
```

#### 2.3 配置环境

创建 `frontend/.env.local` 文件:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Hi Mart
VITE_STRIPE_PUBLIC_KEY=pk_test_your_key_here
```

#### 2.4 启动开发服务器

```bash
npm run dev
```

前端将在 http://localhost:5173 运行

---

## 验证安装

### 后端检查

1. 访问 http://localhost:8000
   - 应该看到API根页面

2. 访问 http://localhost:8000/admin
   - 使用超级用户账户登录

3. 访问 http://localhost:8000/api/docs/
   - 查看完整的API文档

### 前端检查

1. 访问 http://localhost:5173
   - 应该看到 "Welcome to Hi Mart" 页面

2. 打开浏览器开发者工具 (F12)
   - 检查Console标签没有错误

---

## 环境变量配置详解

### 后端关键变量

| 变量 | 描述 | 示例 |
|------|------|------|
| `DEBUG` | 调试模式 | `True` (开发) / `False` (生产) |
| `SECRET_KEY` | Django密钥 | 自动生成的随机字符串 |
| `ALLOWED_HOSTS` | 允许的主机 | `localhost,127.0.0.1` |
| `DATABASE_URL` | 数据库连接 | `postgresql://user:pass@host/db` |
| `REDIS_URL` | Redis连接 | `redis://localhost:6379/0` |
| `MPESA_*` | M-Pesa凭据 | 从Safaricom获取 |
| `STRIPE_*` | Stripe凭据 | 从Stripe Dashboard获取 |

### 前端关键变量

| 变量 | 描述 | 示例 |
|------|------|------|
| `VITE_API_BASE_URL` | API基础URL | `http://localhost:8000/api` |
| `VITE_STRIPE_PUBLIC_KEY` | Stripe公钥 | `pk_test_...` |

---

## 常见问题解决

### 问题1: PostgreSQL连接错误

**症状**: `FATAL: Ident authentication failed for user "himart"`

**解决方案**:
1. 检查PostgreSQL是否运行
2. 验证用户和密码
3. 检查host和port是否正确

```bash
# 测试连接
psql -h localhost -U himart -d himart_db -c "SELECT 1"
```

### 问题2: Redis连接错误

**症状**: `ConnectionError: Error 111 connecting to localhost:6379`

**解决方案**:
```bash
# 检查Redis是否运行
redis-cli ping  # 应该返回 PONG

# 启动Redis (如果未运行)
redis-server
```

### 问题3: CORS错误在浏览器控制台

**症状**: `Access to XMLHttpRequest at 'http://localhost:8000/api/...' blocked by CORS`

**解决方案**:
在 `backend/.env` 中检查:
```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 问题4: 前端无法连接到后端API

**症状**: 网络请求失败或超时

**解决方案**:
1. 检查后端是否运行: http://localhost:8000
2. 检查 `VITE_API_BASE_URL` 是否正确
3. 检查防火墙设置

### 问题5: 迁移失败

**症状**: `django.db.utils.ProgrammingError: relation "auth_user" does not exist`

**解决方案**:
```bash
# 清除所有迁移并重新开始 (仅用于开发)
python manage.py migrate zero users  # 对每个应用重复
python manage.py migrate
```

---

## 项目初始化后的下一步

1. **创建演示产品**
   ```bash
   python manage.py shell
   ```
   
   ```python
   from apps.products.models import Category, Product
   from apps.stores.models import Store
   from apps.users.models import User
   
   # 创建用户和店铺...
   ```

2. **配置支付凭据**
   - 获取M-Pesa Daraja API凭据
   - 获取Stripe API密钥
   - 在 `.env` 中配置

3. **自定义品牌**
   - 更新前端的标志和颜色
   - 修改 `README.md` 和文档

4. **设置电子邮件**
   - 配置SMTP服务器用于发送邮件
   - 在 `.env` 中设置电子邮件凭据

---

## 有用的命令

### Django管理命令

```bash
# 创建新应用
python manage.py startapp myapp

# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 运行测试
python manage.py test

# 进入Django shell
python manage.py shell

# 导入数据
python manage.py loaddata fixture_file.json

# 导出数据
python manage.py dumpdata > data.json

# 清理缓存
python manage.py clear_cache

# 生成静态文件
python manage.py collectstatic
```

### NPM命令

```bash
# 开发服务器
npm run dev

# 生产构建
npm run build

# 预览构建
npm run preview

# 类型检查
npm run type-check

# 格式化代码
npm run format

# 运行linter
npm run lint
```

---

## 获取帮助

- 查看 `README.md` 获取完整文档
- 查看 API文档: http://localhost:8000/api/docs/
- 检查日志: `docker-compose logs backend` 或 `docker-compose logs frontend`
- 提出Issue或联系项目维护者

---

**祝您开发愉快! 🚀**
