# 第一阶段后端实现 - 部署指南

## 📋 本阶段实现的功能

### 1. 产品管理系统 ✅
- 产品列表 (搜索、过滤、排序、分页)
- 产品详情页面
- 产品分类管理
- 产品图片管理

**API 端点:**
```
GET    /api/products/                    - 产品列表
GET    /api/products/{id}/               - 产品详情
GET    /api/products/categories/         - 分类列表
GET    /api/products/categories/{id}/    - 分类详情
```

### 2. 购物车系统 ✅
- 添加产品到购物车
- 更新购物车项目数量
- 删除购物车项目
- 清空购物车
- 实时计算购物车总价

**API 端点:**
```
GET    /api/cart/                        - 获取购物车
POST   /api/cart/add/                    - 添加到购物车
PATCH  /api/cart/update_item/            - 更新数量
DELETE /api/cart/remove_item/            - 移除商品
DELETE /api/cart/clear/                  - 清空购物车
```

### 3. 订单系统 ✅
- 从购物车创建订单
- 订单管理和追踪
- 订单状态流转
- 库存自动更新
- 取消订单和库存恢复

**API 端点:**
```
GET    /api/orders/                      - 订单列表
POST   /api/orders/                      - 创建订单
GET    /api/orders/{id}/                 - 订单详情
POST   /api/orders/from_cart/            - 从购物车创建
PATCH  /api/orders/{id}/cancel/          - 取消订单
GET    /api/orders/{id}/track/           - 追踪订单
```

### 4. 优惠券和促销系统 ✅
- 创建优惠券（百分比和固定金额）
- 优惠券有效性验证
- 优惠券使用限制
- 优惠券使用追踪

**API 端点:**
```
GET    /api/promotions/coupons/          - 获取优惠券列表
POST   /api/promotions/coupons/validate/ - 验证优惠券
POST   /api/promotions/coupons/apply/    - 应用优惠券
```

---

## 🚀 部署步骤

### 第一步：执行数据库迁移

在后端目录执行以下命令创建新表：

```bash
cd backend

# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate
```

**新创建的表：**
- `cart_cart` - 购物车表
- `cart_cartitem` - 购物车项目表
- `promotions_coupon` - 优惠券表
- `promotions_couponusage` - 优惠券使用记录表

### 第二步：测试 API

#### 2.1 测试产品 API
```bash
# 获取产品列表
curl http://localhost:8000/api/products/

# 搜索产品
curl "http://localhost:8000/api/products/?search=iphone"

# 按价格过滤
curl "http://localhost:8000/api/products/?min_price=100&max_price=5000"

# 按分类过滤
curl "http://localhost:8000/api/products/?category=1"
```

#### 2.2 测试购物车 API（需认证）
```bash
# 添加到购物车
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

# 获取购物车
curl http://localhost:8000/api/cart/ \
  -H "Authorization: Bearer <token>"

# 更新购物车项目
curl -X PATCH http://localhost:8000/api/cart/update_item/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "quantity": 5}'
```

#### 2.3 测试订单 API（需认证）
```bash
# 从购物车创建订单
curl -X POST http://localhost:8000/api/orders/from_cart/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Main St, Nairobi",
    "billing_address": "123 Main St, Nairobi"
  }'

# 获取订单列表
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <token>"

# 追踪订单
curl http://localhost:8000/api/orders/1/track/ \
  -H "Authorization: Bearer <token>"
```

#### 2.4 测试优惠券 API
```bash
# 获取优惠券列表
curl http://localhost:8000/api/promotions/coupons/

# 验证优惠券
curl -X POST http://localhost:8000/api/promotions/coupons/validate/ \
  -H "Content-Type: application/json" \
  -d '{"code": "SAVE10", "amount": 1000}'
```

### 第三步：创建测试数据

创建管理员账户：
```bash
python manage.py createsuperuser
```

通过 Django Admin 创建：
1. 产品分类
2. 店铺
3. 示例产品
4. 优惠券

访问: http://localhost:8000/admin

### 第四步：运行测试

```bash
# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test apps.cart
python manage.py test apps.promotions
python manage.py test apps.orders

# 查看覆盖率
coverage run --source='.' manage.py test
coverage report
```

---

## 📊 数据库变更总结

### 新增表

| 表名 | 描述 | 关键字段 |
|------|------|---------|
| `cart_cart` | 购物车 | user_id, created_at, updated_at |
| `cart_cartitem` | 购物车项目 | cart_id, product_id, quantity |
| `promotions_coupon` | 优惠券 | code, discount_type, discount_value, valid_from, valid_to |
| `promotions_couponusage` | 优惠券使用记录 | coupon_id, user_id, used_at |

### 修改的表

无直接修改，但以下表会有新的关系：
- `orders_order` - 支持优惠券集成
- `products_product` - 库存管理已完善

---

## 🔧 常见问题

### Q: 购物车为什么自动创建？
A: 当用户创建时，系统会自动创建一个购物车。这通过 Django signals 实现。

### Q: 优惠券如何应用到订单？
A: 当前版本优惠券在购物车阶段验证，后期可集成到订单创建流程。

### Q: 库存如何更新？
A: 创建订单时，系统自动从产品库存中减少，取消订单时恢复。

### Q: 如何测试支付集成？
A: 支付集成在第二阶段实现。当前订单默认状态为未支付。

---

## 📈 性能指标

目标性能指标：

| 指标 | 目标值 | 验证命令 |
|------|-------|---------|
| API 响应时间 | < 200ms | `time curl http://localhost:8000/api/products/` |
| 购物车操作 | < 100ms | 实测 POST /api/cart/add/ |
| 订单创建 | < 500ms | 实测 POST /api/orders/from_cart/ |
| 并发用户 | 100+ | 使用 Apache Bench 或 JMeter |

---

## ✅ 验收清单

完成以下检查才能进入第二阶段：

- [ ] 所有数据库迁移成功执行
- [ ] 产品 API 正常工作（GET /api/products/）
- [ ] 购物车 API 正常工作（POST /api/cart/add/）
- [ ] 订单 API 正常工作（POST /api/orders/from_cart/）
- [ ] 优惠券 API 正常工作（POST /api/promotions/coupons/validate/）
- [ ] 自动化测试通过率 > 85%
- [ ] API 文档完整（http://localhost:8000/api/docs/）
- [ ] 没有严重的性能问题

---

## 🔄 后续步骤

完成本阶段后，进入第二阶段：**支付和物流集成**

预计任务：
- Stripe 支付集成
- M-Pesa 支付集成
- 物流追踪系统
- 发货单生成

---

**更新时间**: 2026-06-19  
**版本**: 1.0 - Phase 1 完成  
**状态**: 准备部署到云服务器
