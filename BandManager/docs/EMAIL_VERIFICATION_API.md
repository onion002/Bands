# 邮箱验证API文档

## 概述

本系统实现了完整的邮箱验证功能，包括发送验证码、验证验证码和使用验证码注册等功能。

## API接口

### 1. 发送验证码

**接口地址：** `POST /api/auth/send-verification-code`

**请求参数：**
```json
{
    "email": "user@example.com",
    "verification_type": "register"
}
```

**参数说明：**
- `email`: 邮箱地址（必填）
- `verification_type`: 验证码类型（可选，默认：register）
  - `register`: 注册验证
  - `login`: 登录验证
  - `reset_password`: 重置密码验证

**响应示例：**
```json
{
    "message": "验证码发送成功",
    "email": "user@example.com",
    "verification_type": "register"
}
```

### 2. 验证邮箱验证码

**接口地址：** `POST /api/auth/verify-email`

**请求参数：**
```json
{
    "email": "user@example.com",
    "code": "123456",
    "verification_type": "register"
}
```

**参数说明：**
- `email`: 邮箱地址（必填）
- `code`: 验证码（必填）
- `verification_type`: 验证码类型（可选，默认：register）

**响应示例：**
```json
{
    "message": "验证成功",
    "email": "user@example.com",
    "verification_type": "register"
}
```

### 3. 使用验证码注册

**接口地址：** `POST /api/auth/register-with-verification`

**请求参数：**
```json
{
    "username": "testuser",
    "email": "user@example.com",
    "password": "password123",
    "verification_code": "123456",
    "user_type": "user",
    "display_name": "测试用户"
}
```

**参数说明：**
- `username`: 用户名（必填，3-20位，只能包含字母、数字、下划线）
- `email`: 邮箱地址（必填）
- `password`: 密码（必填，至少8位，包含字母和数字）
- `verification_code`: 验证码（必填）
- `user_type`: 用户类型（可选，默认：user）
- `display_name`: 显示名称（可选）

**响应示例：**
```json
{
    "message": "注册成功",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "user@example.com",
        "user_type": "user",
        "display_name": "测试用户",
        "avatar_url": null,
        "is_active": true,
        "created_at": "2025-01-27T10:00:00",
        "bands_public": false,
        "members_public": false,
        "events_public": false
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 配置说明

### 邮件配置

在 `config.py` 中配置邮件服务：

```python
# 邮件配置
MAIL_SERVER = 'smtp.qq.com'  # 邮件服务器
MAIL_PORT = 587              # 端口
MAIL_USE_TLS = True          # 使用TLS
MAIL_USE_SSL = False         # 不使用SSL
MAIL_USERNAME = 'your-email@qq.com'  # 邮箱用户名
MAIL_PASSWORD = 'your-email-password'  # 邮箱密码或授权码
MAIL_DEFAULT_SENDER = 'your-email@qq.com'  # 默认发件人
```

### 环境变量配置

可以通过环境变量覆盖配置：

```bash
export MAIL_SERVER=smtp.qq.com
export MAIL_PORT=587
export MAIL_USE_TLS=true
export MAIL_USERNAME=your-email@qq.com
export MAIL_PASSWORD=your-email-password
```

## 使用流程

### 注册流程

1. 用户填写邮箱地址
2. 调用 `/api/auth/send-verification-code` 发送验证码
3. 用户收到邮件，输入验证码
4. 调用 `/api/auth/verify-email` 验证验证码
5. 用户填写完整注册信息
6. 调用 `/api/auth/register-with-verification` 完成注册

### 登录验证流程

1. 用户输入邮箱和密码
2. 调用 `/api/auth/send-verification-code` 发送登录验证码
3. 用户收到邮件，输入验证码
4. 调用 `/api/auth/verify-email` 验证验证码
5. 验证成功后，调用 `/api/auth/login` 完成登录

## 注意事项

1. 验证码有效期为5分钟
2. 验证码使用后立即失效
3. 同一邮箱可以多次发送验证码，但只有最新的有效
4. 注册时邮箱验证码类型必须为 `register`
5. 建议在生产环境中使用Redis缓存验证码，提高性能

## 错误码说明

- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `409`: 冲突（用户名或邮箱已存在）
- `500`: 服务器内部错误

## 安全建议

1. 限制验证码发送频率，防止恶意攻击
2. 使用HTTPS传输，保护用户隐私
3. 定期清理过期的验证码记录
4. 监控异常登录行为
5. 使用强密码策略
