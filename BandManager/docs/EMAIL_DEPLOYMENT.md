# 邮箱验证功能部署说明

## 前置要求

### 1. 邮箱配置

#### QQ邮箱配置
1. 登录QQ邮箱
2. 进入"设置" -> "账户"
3. 开启"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 生成授权码（客户端专用密码）
5. 记录以下信息：
   - 邮箱地址：your-email@qq.com
   - 授权码：your-authorization-code
   - SMTP服务器：smtp.qq.com
   - 端口：587（TLS）或 465（SSL）

#### 其他邮箱配置
- **Gmail**: smtp.gmail.com:587 (TLS)
- **163邮箱**: smtp.163.com:25 (TLS)
- **126邮箱**: smtp.126.com:25 (TLS)
- **Outlook**: smtp-mail.outlook.com:587 (TLS)

### 2. 系统依赖

确保系统已安装以下依赖：
```bash
pip install Flask-Mail==0.9.1
pip install redis==5.0.1  # 可选，用于缓存
```

## 部署步骤

### 1. 环境变量配置

创建 `.env` 文件或在系统环境变量中设置：

```bash
# 邮件配置
export MAIL_SERVER=smtp.qq.com
export MAIL_PORT=587
export MAIL_USE_TLS=true
export MAIL_USE_SSL=false
export MAIL_USERNAME=your-email@qq.com
export MAIL_PASSWORD=your-authorization-code
export MAIL_DEFAULT_SENDER=your-email@qq.com

# 验证码配置
export VERIFICATION_CODE_EXPIRE=300
export VERIFICATION_CODE_LENGTH=6

# 其他配置
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
```

### 2. 配置文件修改

在 `config.py` 中确认邮件配置：

```python
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.qq.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@qq.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-authorization-code'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'your-email@qq.com'
```

### 3. 数据库迁移

运行数据库迁移以创建邮箱验证表：

```bash
# 进入项目目录
cd BandManager

# 初始化迁移（如果还没有初始化）
flask db init

# 创建迁移文件
flask db migrate -m "Add email verification table"

# 应用迁移
flask db upgrade
```

### 4. 启动应用

```bash
# 开发环境
python app.py

# 生产环境
python app_production.py
```

## 测试验证

### 1. 功能测试

使用提供的测试脚本：

```bash
python test_email_verification.py
```

### 2. API测试

使用Postman或curl测试API接口：

```bash
# 发送验证码
curl -X POST http://localhost:5000/api/auth/send-verification-code \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "verification_type": "register"}'

# 验证验证码
curl -X POST http://localhost:5000/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "code": "123456", "verification_type": "register"}'

# 使用验证码注册
curl -X POST http://localhost:5000/api/auth/register-with-verification \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "TestPass123", "verification_code": "123456"}'
```

## 常见问题

### 1. 邮件发送失败

**问题描述**: 邮件发送失败，返回500错误

**解决方案**:
1. 检查邮箱配置是否正确
2. 确认授权码是否有效
3. 检查网络连接和防火墙设置
4. 查看应用日志获取详细错误信息

### 2. 验证码不匹配

**问题描述**: 输入的验证码与系统生成的验证码不匹配

**解决方案**:
1. 检查验证码是否过期（默认5分钟）
2. 确认使用的是最新发送的验证码
3. 检查数据库连接是否正常

### 3. 数据库连接问题

**问题描述**: 无法创建或访问邮箱验证表

**解决方案**:
1. 确认数据库服务正常运行
2. 检查数据库连接配置
3. 运行数据库迁移命令
4. 检查数据库权限设置

## 性能优化

### 1. 使用Redis缓存

在生产环境中，建议使用Redis缓存验证码：

```python
# 在 config.py 中配置Redis
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

# 在 email_service.py 中使用Redis
import redis
redis_client = redis.from_url(current_app.config['REDIS_URL'])
```

### 2. 验证码发送频率限制

添加发送频率限制，防止恶意攻击：

```python
# 在发送验证码前检查频率
def check_send_frequency(email):
    key = f"send_limit:{email}"
    count = redis_client.get(key)
    if count and int(count) >= 5:  # 每小时最多5次
        return False
    redis_client.incr(key)
    redis_client.expire(key, 3600)  # 1小时过期
    return True
```

### 3. 异步邮件发送

使用Celery等任务队列异步发送邮件：

```python
from celery import Celery

@celery.task
def send_verification_email_async(email, code, verification_type):
    # 异步发送邮件
    pass
```

## 监控和维护

### 1. 日志监控

监控邮件发送日志：

```python
import logging
logger = logging.getLogger(__name__)

# 记录邮件发送状态
logger.info(f"验证码邮件发送成功: {email}")
logger.error(f"验证码邮件发送失败: {email}, 错误: {str(e)}")
```

### 2. 定期清理

定期清理过期的验证码记录：

```python
# 在定时任务中执行
def clean_expired_codes():
    expired_codes = EmailVerification.query.filter(
        EmailVerification.expires_at < datetime.utcnow()
    ).all()
    
    for code in expired_codes:
        db.session.delete(code)
    
    db.session.commit()
```

### 3. 健康检查

添加健康检查接口：

```python
@auth_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        # 检查邮件服务
        # 可以尝试发送测试邮件
        
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
```

## 安全建议

1. **使用HTTPS**: 在生产环境中强制使用HTTPS
2. **限制频率**: 限制验证码发送频率，防止恶意攻击
3. **验证码复杂度**: 使用足够复杂的验证码（6位数字）
4. **过期时间**: 设置合理的验证码过期时间（5分钟）
5. **日志审计**: 记录所有验证码操作，便于审计
6. **IP限制**: 考虑添加IP地址限制，防止批量攻击
