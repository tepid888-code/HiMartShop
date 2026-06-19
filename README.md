# Hi Mart - E-Commerce Platform for Kenya

Hi Mart是一个完整的电商平台项目，为肯尼亚的线下商场提供在线购物解决方案。项目采用现代化的技术栈，包括Django REST API后端和Vue 3前端。

## 项目架构

```
webshop/
├── backend/          # Django REST API
├── frontend/         # Vue 3 SPA
└── docker-compose.yml
```

## 技术栈

### 后端 (Backend)
- **Django 5.0** - Web框架
- **Django REST Framework** - REST API开发
- **PostgreSQL** - 数据库
- **Redis** - 缓存和会话
- **Stripe** - 国际支付
- **M-Pesa Daraja API** - 肯尼亚本地支付

### 前端 (Frontend)
- **Vue 3** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP客户端
- **Tailwind CSS** - 样式框架

## 功能特性

### 用户功能
- 用户注册和身份验证
- 个人资料管理
- 地址管理（多个地址）
- 收藏夹（Wishlist）

### 产品功能
- 产品分类浏览
- 产品搜索和过滤
- 产品详情页面
- 产品评价和评论
- 库存管理（按店铺）

### 购物功能
- 购物车管理
- 订单创建和管理
- 订单追踪
- 订单状态历史

### 支付功能
- M-Pesa支付集成
- Stripe信用卡支付
- 货到付款选项
- 退款管理

### 多店铺功能
- 支持多个店铺（Hi Mart分店）
- 店铺管理员权限
- 按店铺的库存管理
- 店铺评分和统计

## 快速开始

### 前置要求
- Docker和Docker Compose
- 或者本地安装：
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - Redis 7+

### 使用Docker启动

```bash
# 复制环境配置文件
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 启动所有服务
docker-compose up -d

# 初始化数据库
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser

# 访问应用
# 前端: http://localhost:5173
# 后端: http://localhost:8000
# Admin: http://localhost:8000/admin
# API文档: http://localhost:8000/api/docs/
```

### 本地开发

#### 后端设置
```bash
# 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库等

# 运行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

#### 前端设置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local

# 启动开发服务器
npm run dev
```

## API文档

启动后端后，访问 `http://localhost:8000/api/docs/` 查看完整的API文档。

### 主要API端点

```
/api/users/          - 用户管理
/api/products/       - 产品管理
/api/orders/         - 订单管理
/api/payment/        - 支付管理
/api/stores/         - 店铺管理
```

## 环境变量配置

### 后端 (.env)
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
DEBUG=True

# 支付
MPESA_CONSUMER_KEY=...
MPESA_CONSUMER_SECRET=...
STRIPE_PUBLIC_KEY=...
STRIPE_SECRET_KEY=...

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 前端 (.env.local)
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_STRIPE_PUBLIC_KEY=...
```

## 项目结构详解

### 后端应用

- **users** - 用户管理、认证、个人资料
- **products** - 产品目录、分类、库存
- **orders** - 订单管理和订单历史
- **payment** - 支付处理和退款
- **stores** - 多店铺管理
- **common** - 通用工具和配置

### 前端结构

```
frontend/src/
├── components/       - 可复用组件
├── pages/           - 页面组件
├── stores/          - Pinia状态管理
├── api/             - API客户端
├── router/          - 路由配置
└── assets/          - 静态资源
```

## 开发指南

### 添加新的API端点

1. 在对应应用的 `models.py` 中定义模型
2. 在 `serializers.py` 中创建序列化器
3. 在 `views.py` 中实现视图
4. 在 `urls.py` 中注册路由

### 前端页面开发

1. 在 `src/pages/` 中创建新的Vue组件
2. 在 `src/router/index.ts` 中添加路由
3. 使用Pinia store管理状态
4. 使用API client调用后端

## 测试

### 后端测试
```bash
cd backend
python manage.py test
```

### 前端测试
```bash
cd frontend
npm run test
```

## 部署

### 生产环境构建

后端：
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
gunicorn config.wsgi:application
```

前端：
```bash
cd frontend
npm install
npm run build
# 将dist/文件夹部署到Web服务器
```

## 支付集成

### M-Pesa (Daraja)
- 使用STK Push流程
- 支持肯尼亚电话号码格式
- 实时支付确认通过webhook

### Stripe
- 支持国际信用卡
- 3D Secure验证
- 完整的支付管理面板

## 常见问题

### 数据库连接错误
检查PostgreSQL是否正在运行，确认连接字符串正确。

### CORS错误
确保在 `backend/.env` 中的 `CORS_ALLOWED_ORIGINS` 包含前端的URL。

### M-Pesa测试
使用沙箱环境进行测试：
- 设置 `MPESA_ENVIRONMENT=sandbox`
- 使用沙箱测试凭据

## 贡献

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用MIT许可证。详见 LICENSE 文件。

## 联系方式

如有问题或建议，请联系项目维护者。

---

**最后更新**: 2026年6月
**版本**: 1.0.0
