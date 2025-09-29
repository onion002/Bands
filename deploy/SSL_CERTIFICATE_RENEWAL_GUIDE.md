# 🔐 SSL证书更新指南

## 📅 证书到期信息

当前证书有效期：**2025年9月29日 - 2025年12月27日**

⚠️ **重要提醒**：建议在证书到期前 **30天** 开始准备更新！

---

## 🚀 快速更新步骤

### 方法一：自动化脚本更新（推荐）

创建自动更新脚本：

```bash
#!/bin/bash
# SSL证书自动更新脚本

# 1. 下载新证书到临时目录
cd /tmp
wget -O new_certificate.pem "你的新证书下载链接"
wget -O new_private.key "你的新私钥下载链接"

# 2. 验证新证书
openssl x509 -in new_certificate.pem -text -noout
openssl rsa -in new_private.key -check

# 3. 备份旧证书
cp /etc/ssl/certs/bands.icu.pem /etc/ssl/certs/bands.icu.pem.bak.$(date +%Y%m%d)
cp /etc/ssl/private/bands.icu.key /etc/ssl/private/bands.icu.key.bak.$(date +%Y%m%d)

# 4. 安装新证书
cp new_certificate.pem /etc/ssl/certs/bands.icu.pem
cp new_private.key /etc/ssl/private/bands.icu.key

# 5. 设置正确权限
chmod 644 /etc/ssl/certs/bands.icu.pem
chmod 600 /etc/ssl/private/bands.icu.key
chown root:root /etc/ssl/certs/bands.icu.pem
chown root:root /etc/ssl/private/bands.icu.key

# 6. 测试Nginx配置
nginx -t

# 7. 重新加载Nginx
if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo "✅ SSL证书更新成功！"
else
    echo "❌ Nginx配置错误，恢复备份..."
    cp /etc/ssl/certs/bands.icu.pem.bak.$(date +%Y%m%d) /etc/ssl/certs/bands.icu.pem
    cp /etc/ssl/private/bands.icu.key.bak.$(date +%Y%m%d) /etc/ssl/private/bands.icu.key
fi

# 8. 验证新证书
curl -I https://bands.icu
openssl s_client -connect bands.icu:443 -servername bands.icu < /dev/null | grep -A2 "Verify return code"
```

### 方法二：手动更新步骤

```bash
# 1. 检查当前证书到期时间
openssl x509 -in /etc/ssl/certs/bands.icu.pem -noout -dates

# 2. 备份现有证书
cd /etc/ssl/certs
cp bands.icu.pem bands.icu.pem.bak.$(date +%Y%m%d)
cd /etc/ssl/private
cp bands.icu.key bands.icu.key.bak.$(date +%Y%m%d)

# 3. 上传新证书文件（通过FTP/SCP等方式）
# 上传到 /tmp/new_certificate.pem 和 /tmp/new_private.key

# 4. 验证新证书
openssl x509 -in /tmp/new_certificate.pem -text -noout
openssl rsa -in /tmp/new_private.key -check

# 5. 安装新证书
cp /tmp/new_certificate.pem /etc/ssl/certs/bands.icu.pem
cp /tmp/new_private.key /etc/ssl/private/bands.icu.key

# 6. 设置权限
chmod 644 /etc/ssl/certs/bands.icu.pem
chmod 600 /etc/ssl/private/bands.icu.key

# 7. 测试并重新加载Nginx
nginx -t && systemctl reload nginx
```

---

## 🔍 证书验证检查

### 更新后必做的验证步骤：

```bash
# 1. 检查证书有效期
openssl x509 -in /etc/ssl/certs/bands.icu.pem -noout -dates

# 2. 检查证书域名
openssl x509 -in /etc/ssl/certs/bands.icu.pem -noout -subject -ext subjectAltName

# 3. 验证私钥匹配
cert_md5=$(openssl x509 -noout -modulus -in /etc/ssl/certs/bands.icu.pem | openssl md5)
key_md5=$(openssl rsa -noout -modulus -in /etc/ssl/private/bands.icu.key | openssl md5)
echo "证书MD5: $cert_md5"
echo "私钥MD5: $key_md5"

# 4. 测试HTTPS连接
curl -I https://bands.icu
curl -I https://www.bands.icu

# 5. 检查SSL评级（可选）
# 访问 https://www.ssllabs.com/ssltest/ 输入 bands.icu 进行在线检测
```

---

## ⏰ 证书监控和提醒

### 创建证书到期检查脚本：

```bash
#!/bin/bash
# 证书到期检查脚本 - /opt/scripts/check_ssl_expiry.sh

DOMAIN="bands.icu"
CERT_FILE="/etc/ssl/certs/bands.icu.pem"
DAYS_WARNING=30

# 获取证书到期日期
EXPIRY_DATE=$(openssl x509 -in $CERT_FILE -noout -enddate | cut -d= -f2)
EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_TIMESTAMP=$(date +%s)
DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_TIMESTAMP - $CURRENT_TIMESTAMP) / 86400 ))

echo "证书到期时间: $EXPIRY_DATE"
echo "剩余天数: $DAYS_UNTIL_EXPIRY 天"

if [ $DAYS_UNTIL_EXPIRY -le $DAYS_WARNING ]; then
    echo "⚠️ 警告：SSL证书将在 $DAYS_UNTIL_EXPIRY 天后到期！"
    echo "请及时更新证书！"
    
    # 可以添加邮件通知或其他告警方式
    # mail -s "SSL证书即将到期" admin@example.com < /dev/null
fi
```

### 设置定期检查（可选）：

```bash
# 添加到crontab，每周检查一次
crontab -e

# 添加以下行：
0 9 * * 1 /opt/scripts/check_ssl_expiry.sh
```

---

## 🚨 应急处理方案

### 如果证书已经到期：

```bash
# 1. 立即停止HTTPS访问，启用HTTP临时访问
nano /etc/nginx/conf.d/bands.icu.conf

# 临时注释掉HTTPS部分，只保留HTTP重定向到HTTP
# server {
#     listen 443 ssl http2;
#     ...
# }

# 改为临时HTTP服务
server {
    listen 80;
    server_name bands.icu www.bands.icu;
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# 2. 重新加载Nginx
systemctl reload nginx

# 3. 更新应用配置使用HTTP
# 修改后端 .env 文件
nano /opt/Bands/BandManager/.env
# API_BASE_URL=http://bands.icu

# 修改前端 .env.production 文件
nano /opt/Bands/band-manager-front/.env.production
# VITE_API_BASE_URL=http://bands.icu/api

# 4. 重启服务
cd /opt/Bands/deploy
./manage.sh restart

# 5. 尽快获取新证书并恢复HTTPS
```

---

## 📋 证书更新检查清单

更新SSL证书时，请按以下清单逐项检查：

- [ ] **准备阶段**
  - [ ] 备份现有证书和私钥
  - [ ] 准备新的证书文件
  - [ ] 验证新证书的有效期和域名

- [ ] **安装阶段**
  - [ ] 上传新证书到正确位置
  - [ ] 设置正确的文件权限
  - [ ] 验证证书和私钥匹配

- [ ] **测试阶段**
  - [ ] 测试Nginx配置 (`nginx -t`)
  - [ ] 重新加载Nginx服务
  - [ ] 验证HTTPS访问正常

- [ ] **验证阶段**
  - [ ] 检查证书有效期
  - [ ] 测试主域名访问
  - [ ] 测试www子域名访问
  - [ ] 测试API接口访问
  - [ ] 检查SSL评级（可选）

- [ ] **清理阶段**
  - [ ] 删除临时文件
  - [ ] 记录更新日志
  - [ ] 设置下次更新提醒

---

## 🔧 常见问题解决

### 1. 证书和私钥不匹配
```bash
# 检查证书和私钥的MD5值是否一致
openssl x509 -noout -modulus -in /etc/ssl/certs/bands.icu.pem | openssl md5
openssl rsa -noout -modulus -in /etc/ssl/private/bands.icu.key | openssl md5
```

### 2. Nginx配置测试失败
```bash
# 查看详细错误信息
nginx -t
# 检查Nginx错误日志
tail -50 /var/log/nginx/error.log
```

### 3. 浏览器显示证书错误
```bash
# 清除浏览器缓存
# 或使用隐私/无痕模式测试
# 检查证书链是否完整
openssl s_client -connect bands.icu:443 -servername bands.icu
```

### 4. 证书权限问题
```bash
# 重新设置正确权限
chmod 644 /etc/ssl/certs/bands.icu.pem
chmod 600 /etc/ssl/private/bands.icu.key
chown root:root /etc/ssl/certs/bands.icu.pem
chown root:root /etc/ssl/private/bands.icu.key
```

---

## 📞 紧急联系信息

如果在证书更新过程中遇到问题：

1. **立即恢复备份**：
   ```bash
   cp /etc/ssl/certs/bands.icu.pem.bak.* /etc/ssl/certs/bands.icu.pem
   cp /etc/ssl/private/bands.icu.key.bak.* /etc/ssl/private/bands.icu.key
   systemctl reload nginx
   ```

2. **记录错误信息**：
   ```bash
   nginx -t > nginx_error.log 2>&1
   tail -100 /var/log/nginx/error.log > nginx_runtime_error.log
   ```

3. **联系证书提供商**获取技术支持

---

## 💡 最佳实践建议

1. **提前更新**：在证书到期前30天开始准备
2. **定期检查**：每月检查一次证书状态
3. **自动化监控**：设置证书到期提醒
4. **备份策略**：始终保留证书备份
5. **测试环境**：如果可能，先在测试环境验证
6. **文档记录**：记录每次更新的详细过程

使用这个指南，你可以安全、快速地更新SSL证书，确保网站的持续安全运行！🔐✨
