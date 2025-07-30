# 乐队管理系统认证架构设计

## 系统概述

本系统采用多租户架构，支持两种用户类型：
- **管理员用户**：拥有独立的数据空间，可以管理自己的乐队、成员和活动
- **普通用户**：只读访问，可以查看指定管理员的数据

## 用户模型设计

### User 表结构
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('admin', 'user') NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 开发者密钥验证
- 管理员注册需要提供开发者密钥
- 密钥存储在环境变量中：`DEVELOPER_SECRET_KEY`
- 支持多个密钥，用逗号分隔

## 多租户数据隔离方案

### 方案选择：行级隔离（Row-Level Isolation）
在现有表中添加 `owner_id` 字段，关联到管理员用户ID：

```sql
-- 修改现有表
ALTER TABLE bands ADD COLUMN owner_id INTEGER REFERENCES users(id);
ALTER TABLE members ADD COLUMN owner_id INTEGER REFERENCES users(id);
ALTER TABLE events ADD COLUMN owner_id INTEGER REFERENCES users(id);
```

### 数据访问控制
1. **管理员用户**：只能访问 `owner_id = user.id` 的数据
2. **普通用户**：通过指定管理员用户名访问对应数据
3. **API层面**：所有查询自动添加 `owner_id` 过滤条件

## 认证流程设计

### 注册流程
1. **普通用户注册**：
   - 用户名、邮箱、密码
   - 自动设置 `user_type = 'user'`

2. **管理员注册**：
   - 用户名、邮箱、密码、开发者密钥
   - 验证开发者密钥
   - 设置 `user_type = 'admin'`

### 登录流程
1. 用户名/邮箱 + 密码验证
2. 生成 JWT Token
3. Token 包含用户信息：`user_id`, `username`, `user_type`

### 权限验证
1. **装饰器验证**：`@require_auth`, `@require_admin`
2. **中间件验证**：自动解析 JWT Token
3. **数据过滤**：根据用户类型自动过滤数据

## API 设计

### 认证相关 API
```
POST /api/auth/register          # 注册
POST /api/auth/login             # 登录
POST /api/auth/logout            # 登出
GET  /api/auth/profile           # 获取用户信息
PUT  /api/auth/profile           # 更新用户信息
POST /api/auth/refresh           # 刷新Token
```

### 数据访问 API 修改
```
# 管理员访问（需要登录）
GET /api/bands                   # 获取当前用户的乐队
GET /api/members                 # 获取当前用户的成员
GET /api/events                  # 获取当前用户的活动

# 普通用户访问（公开）
GET /api/public/bands/{admin_username}     # 查看指定管理员的乐队
GET /api/public/members/{admin_username}   # 查看指定管理员的成员
GET /api/public/events/{admin_username}    # 查看指定管理员的活动
```

## 前端架构设计

### 页面结构
```
/auth/login                      # 登录页面
/auth/register                   # 注册页面
/dashboard                       # 管理员仪表板
/public/{admin_username}         # 公开展示页面
/bands                          # 乐队管理（需要管理员权限）
/members                        # 成员管理（需要管理员权限）
/events                         # 活动管理（需要管理员权限）
```

### 状态管理
使用 Pinia 管理认证状态：
```typescript
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isAdmin: boolean
}
```

### 路由守卫
```typescript
// 需要登录的路由
const requireAuth = (to, from, next) => {
  if (!authStore.isAuthenticated) {
    next('/auth/login')
  } else {
    next()
  }
}

// 需要管理员权限的路由
const requireAdmin = (to, from, next) => {
  if (!authStore.isAdmin) {
    next('/public')
  } else {
    next()
  }
}
```

## 安全考虑

### 密码安全
- 使用 bcrypt 进行密码哈希
- 最小密码长度：8位
- 密码复杂度要求：包含字母、数字

### Token 安全
- JWT Token 有效期：24小时
- 支持 Refresh Token 机制
- Token 存储在 httpOnly Cookie 中

### API 安全
- 所有敏感操作需要认证
- 数据访问自动过滤
- 防止 SQL 注入和 XSS 攻击

## 数据迁移计划

### 现有数据处理
1. 创建默认管理员账户
2. 将现有数据关联到默认管理员
3. 更新所有 API 接口
4. 测试数据隔离效果

### 迁移脚本
```python
# 创建默认管理员
default_admin = User(
    username='admin',
    email='admin@example.com',
    user_type='admin'
)

# 更新现有数据
Band.query.update({'owner_id': default_admin.id})
Member.query.update({'owner_id': default_admin.id})
Event.query.update({'owner_id': default_admin.id})
```

## 实施步骤

1. ✅ 设计系统架构
2. 🔄 创建用户模型和认证API
3. 🔄 实现多租户数据隔离
4. 🔄 创建前端认证页面
5. 🔄 实现路由守卫和权限控制
6. 🔄 集成到现有功能
7. 🔄 测试和优化
