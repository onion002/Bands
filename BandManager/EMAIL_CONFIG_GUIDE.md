# 邮箱验证码配置指南

## 问题描述
发送验证码失败，出现500内部服务器错误，主要原因是邮件服务配置缺失。

## 解决方案

### 1. 创建环境变量文件
在 `BandManager/` 目录下创建 `.env` 文件，内容如下：

```env
# 数据库配置
DATABASE_URL=mysql+mysqlconnector://root:002101@localhost/band_db

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
DEVELOPER_SECRET_KEYS=dev-key-123,admin-key-456,oninon466

# 邮件配置 - 请替换为您的实际邮箱配置
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@qq.com

# Redis配置
REDIS_URL=redis://localhost:6379/0

# API配置
API_BASE_URL=http://localhost:5000

# 环境配置
FLASK_ENV=development
DEBUG=true
```

### 2. 配置QQ邮箱
如果您使用QQ邮箱，需要：

1. **开启SMTP服务**：
   - 登录QQ邮箱
   - 设置 → 账户 → 开启SMTP服务
   - 获取授权码（不是QQ密码）

2. **更新配置**：
   ```env
   MAIL_USERNAME=your-qq-email@qq.com
   MAIL_PASSWORD=your-authorization-code
   MAIL_DEFAULT_SENDER=your-qq-email@qq.com
   ```

### 3. 其他邮箱配置
- **Gmail**: smtp.gmail.com:587
- **163邮箱**: smtp.163.com:25
- **126邮箱**: smtp.126.com:25

### 4. 重启后端服务
配置完成后，重启Flask后端服务：

```bash
cd BandManager
python app.py
```

### 5. 测试验证码发送
配置完成后，再次尝试发送验证码。

## 常见问题

### Q: 仍然提示500错误？
A: 检查：
1. `.env` 文件是否在正确位置
2. 邮箱授权码是否正确
3. 网络连接是否正常
4. 查看后端日志输出

### Q: 如何获取QQ邮箱授权码？
A: 
1. 登录QQ邮箱
2. 设置 → 账户
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"IMAP/SMTP服务"
5. 按提示获取授权码

### Q: 可以使用其他邮箱吗？
A: 可以，只需修改 `MAIL_SERVER` 和 `MAIL_PORT` 配置即可。

## 临时解决方案
如果暂时不需要邮箱验证，可以：
1. 使用开发者密钥直接注册管理员账户
2. 或者修改代码跳过邮箱验证步骤
