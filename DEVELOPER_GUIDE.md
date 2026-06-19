# Hi Mart Platform - 开发者快速参考

## 🚀 快速开始

### 安装依赖
```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 启动开发环境
```bash
# 后端 (Django)
cd backend
python manage.py migrate
python manage.py runserver

# 前端 (Vue + Vite)
cd frontend
npm run dev
```

### 启动 Redis (缓存)
```bash
# Docker 方式
docker run -d -p 6379:6379 redis:7-alpine

# 或本地安装
redis-server
```

---

## ✅ 运行测试

### 后端单元测试
```bash
cd backend

# 运行所有测试
pytest

# 运行特定模块测试
pytest apps/products/tests.py
pytest apps/payment/tests.py

# 生成覆盖率报告 (HTML)
pytest --cov=apps --cov-report=html
# 打开 htmlcov/index.html 查看

# 显示覆盖率百分比
pytest --cov=apps --cov-report=term-missing
```

### 运行特定测试类或方法
```bash
# 运行特定测试类
pytest apps/products/tests.py::TestProductViewSet

# 运行特定测试方法
pytest apps/products/tests.py::TestProductViewSet::test_list_products

# 显示详细信息
pytest -v

# 显示打印输出
pytest -s
```

### 前端测试 (Vitest)
```bash
cd frontend

# 运行所有测试
npm run test

# 监视模式 (自动重新运行)
npm run test:watch

# 生成覆盖率报告
npm run test:coverage
```

---

## 📊 性能基准测试

### 运行基准测试
```bash
cd backend
python benchmark.py
```

### 输出示例
```
============================================================
Hi Mart 平台性能基准测试
============================================================

[产品列表 API 基准测试]
✓ 平均响应时间: 145.32ms
  最快: 120.45ms | 最慢: 178.90ms

[缓存效果测试]
✓ 首次请求: 145.32ms
✓ 缓存命中: 8.45ms
✓ 性能提升: 94.2%
```

---

## 🔧 API 端点测试

### 使用 curl 测试 API
```bash
# 获取产品列表
curl http://localhost:8000/api/products/

# 获取产品详情
curl http://localhost:8000/api/products/1/

# 搜索产品
curl "http://localhost:8000/api/products/?search=iphone"

# 过滤产品
curl "http://localhost:8000/api/products/?category=1&min_price=100&max_price=5000"

# 获取用户信息 (需要认证)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/users/me/
```

### 使用 Postman/Insomnia 测试
1. 导入 API 集合 (在 docs/ 目录中)
2. 设置环境变量 (base_url, token 等)
3. 运行请求

---

## 📁 项目结构

```
.
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── users/             # 用户认证模块
│   │   ├── products/          # 产品模块
│   │   ├── orders/            # 订单模块
│   │   ├── payment/           # 支付模块
│   │   └── common/            # 公共工具 (缓存, 权限等)
│   ├── config/                # Django 设置
│   ├── manage.py              # Django CLI
│   ├── pytest.ini             # Pytest 配置
│   ├── conftest.py            # 测试 fixtures
│   ├── benchmark.py           # 性能测试脚本
│   └── requirements.txt       # Python 依赖
│
├── frontend/                  # Vue 3 + Vite 前端
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── components/       # 可复用组件
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── api/              # API 客户端
│   │   └── main.ts           # 入口文件
│   ├── index.html            # HTML 模板
│   ├── vite.config.ts        # Vite 配置
│   └── package.json          # Node 依赖
│
├── .github/
│   └── workflows/            # GitHub Actions CI/CD
│       ├── backend-tests.yml
│       ├── frontend-tests.yml
│       └── deploy.yml
│
└── docker-compose.yml        # Docker 编排
```

---

## 🔐 认证和权限

### 获取 JWT Token
```bash
# 注册
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'

# 登录
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'

# 响应包含 access 和 refresh token
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 使用 Token 调用 API
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/users/me/
```

---

## 📈 缓存管理

### 查看缓存统计
```bash
# 连接 Redis
redis-cli

# 查看所有缓存键
KEYS *

# 查看特定键
GET products:list:*

# 查看缓存统计
INFO stats

# 清除所有缓存
FLUSHALL
```

### 缓存超时配置
```python
# backend/config/settings.py 中的缓存配置:

产品列表:  5分钟   (300秒)
产品详情:  10分钟  (600秒)
分类:      1小时   (3600秒)
收藏:      30分钟  (1800秒)
```

---

## 📋 通用调试技巧

### 查看数据库查询
```python
# Django Shell
python manage.py shell

from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # 执行查询
    products = Product.objects.all()
    
# 查看查询数
print(f"查询数: {len(context)}")

# 查看每个查询
for query in context:
    print(query['sql'])
```

### 查看 API 请求日志
```bash
# 启用详细日志
export DEBUG=True
python manage.py runserver --verbosity=2
```

### 查看 Frontend 错误
打开浏览器开发者工具 (F12):
- **Console**: JavaScript 错误
- **Network**: 网络请求
- **Application**: 存储空间、缓存
- **Vue DevTools**: 组件状态 (需要安装扩展)

---

## 🐛 常见问题解决

### "找不到模块" 错误
```bash
# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 或后端
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 数据库连接错误
```bash
# 检查 PostgreSQL 是否运行
psql -U postgres -d himart

# 检查 .env 文件配置
cat .env  # 检查 DATABASE_URL

# 运行迁移
python manage.py migrate
```

### Redis 连接错误
```bash
# 检查 Redis 是否运行
redis-cli ping  # 应返回 PONG

# 查看 Redis 配置
cat .env  # 检查 REDIS_URL

# 测试连接
redis-cli -h localhost -p 6379
```

### 缓存不生效
```bash
# 清除所有缓存
redis-cli FLUSHALL

# 检查缓存键
redis-cli KEYS '*'

# 验证缓存值
redis-cli GET 'products:list:*'
```

---

## 📚 相关文档

- [API 文档](./docs/API.md) - 完整 API 参考
- [部署指南](./docs/DEPLOYMENT.md) - 生产部署步骤
- [测试文档](./docs/TESTING.md) - 测试策略和最佳实践
- [架构设计](./docs/ARCHITECTURE.md) - 系统架构说明

---

## 💡 开发建议

### 提交代码前检查清单
- [ ] 运行 linter (`npm run lint`, `flake8 apps/`)
- [ ] 运行测试 (`pytest`, `npm run test`)
- [ ] 更新类型定义 (`npm run type-check`)
- [ ] 检查代码覆盖率
- [ ] 提交信息清晰明确

### PR 审查标准
- 代码质量: 清晰、可读、可维护
- 测试覆盖: 新功能有单元测试
- 性能: 无明显性能退化
- 文档: API 文档已更新
- 安全: 遵循安全最佳实践

---

## 📞 获取帮助

- **文档**: 查看 `docs/` 目录
- **问题**: 在 GitHub Issues 提交
- **讨论**: 在 Discussions 区域交流
- **贡献**: 遵循 CONTRIBUTING.md 指南

---

**最后更新:** 2026-06-19  
**版本:** 1.0
