# 🌐 域名和SSL配置指南 - bands.icu

## 📋 配置概览

- **域名**: bands.icu
- **服务器IP**: 47.108.30.30
- **前端端口**: 3000
- **后端端口**: 5000
- **架构**: 单域名 + 子路径API
- **访问方式**: 
  - 前端: https://bands.icu
  - API: https://bands.icu/api/

---

## 🚀 第一步：配置DNS解析

### 1.1 主域名解析
在你的域名管理面板中添加以下DNS记录：

```dns
# 主域名指向服务器
@ (或 bands.icu)     A     47.108.30.30

# www子域名
www                  A     47.108.30.30
```

> **注意**: 我们使用单域名架构，API通过子路径访问，因此不需要单独的api子域名。

### 1.2 验证DNS解析
```bash
# 检查DNS解析是否生效
nslookup bands.icu
nslookup www.bands.icu

# 或使用ping命令
ping bands.icu
ping www.bands.icu
```

**预期结果**: 域名应该解析到 `47.108.30.30`

---

## 🔧 第二步：安装和配置Nginx

### 2.1 安装Nginx
```bash
# 在服务器上安装Nginx
sudo yum install -y nginx

# 启动并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx
```

### 2.2 配置防火墙
```bash
# 开放HTTP和HTTPS端口
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# 验证端口开放
sudo firewall-cmd --list-services
sudo firewall-cmd --list-ports
```

### 2.3 创建Nginx配置文件
```bash
# 创建配置文件
sudo nano /etc/nginx/conf.d/bands.icu.conf
```

```nginx
# /etc/nginx/conf.d/bands.icu.conf

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name bands.icu www.bands.icu;
    return 301 https://$server_name$request_uri;
}

# 主应用 - bands.icu (单域名架构)
server {
    listen 443 ssl http2;
    server_name bands.icu www.bands.icu;
    
    ssl_certificate /etc/ssl/certs/bands.icu.pem;
    ssl_certificate_key /etc/ssl/private/bands.icu.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    
    # API路径 - /api/*
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
    
    # 前端应用 - 所有其他路径
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> **关键配置说明**:
> - 使用单域名架构，API通过 `/api/` 子路径访问
> - 前端: `https://bands.icu` → 代理到 `http://127.0.0.1:3000`
> - API: `https://bands.icu/api/` → 代理到 `http://127.0.0.1:5000/`
> - SSL证书只需要覆盖主域名，避免子域名证书问题

---

## 🔐 第三步：配置SSL证书

### 3.1 上传SSL证书文件
```bash
# 创建SSL证书目录
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

# 上传证书文件（你需要将证书文件传输到服务器）
# 假设你有以下文件：
# - bands.icu.pem (证书文件)
# - bands.icu.key (私钥文件)

# 将证书文件复制到正确位置
sudo cp /path/to/your/bands.icu.pem /etc/ssl/certs/
sudo cp /path/to/your/bands.icu.key /etc/ssl/private/

# 设置正确的权限
sudo chmod 644 /etc/ssl/certs/bands.icu.pem
sudo chmod 600 /etc/ssl/private/bands.icu.key
sudo chown root:root /etc/ssl/certs/bands.icu.pem
sudo chown root:root /etc/ssl/private/bands.icu.key
```

### 3.2 验证SSL证书
```bash
# 检查证书文件
sudo openssl x509 -in /etc/ssl/certs/bands.icu.pem -text -noout

# 检查证书和私钥是否匹配
sudo openssl x509 -noout -modulus -in /etc/ssl/certs/bands.icu.pem | openssl md5
sudo openssl rsa -noout -modulus -in /etc/ssl/private/bands.icu.key | openssl md5
# 两个输出的MD5值应该相同
```

### 3.3 测试Nginx配置
```bash
# 测试Nginx配置语法
sudo nginx -t

# 如果配置正确，重新加载Nginx
sudo systemctl reload nginx

# 检查Nginx状态
sudo systemctl status nginx
```

---

## ⚙️ 第四步：更新应用配置

### 4.1 更新后端配置
```bash
# 编辑后端环境变量
cd /opt/Bands/BandManager
sudo nano .env
```

```env
# 在.env文件中更新以下配置
API_BASE_URL=https://bands.icu/api
CORS_ORIGINS=https://bands.icu,https://www.bands.icu

# 数据库配置
DATABASE_URL=mysql+mysqlconnector://root:002101@localhost/band_db

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
DEVELOPER_SECRET_KEYS=dev-key-123,admin-key-456,oninon466

# 邮件配置
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=3137826052@qq.com
MAIL_PASSWORD=ptvporstvsbqdegc
MAIL_DEFAULT_SENDER=3137826052@qq.com

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 环境配置
FLASK_ENV=production
DEBUG=false
```

### 4.2 更新前端配置
```bash
# 编辑前端环境变量
cd /opt/Bands/band-manager-front
sudo nano .env.production
```

```env
# 更新前端API地址为子路径
VITE_API_BASE_URL=https://bands.icu/api
```

### 4.3 修改前端Vite配置
```bash
# 编辑vite.config.ts文件
cd /opt/Bands/band-manager-front
sudo nano vite.config.ts
```

在 `preview` 配置中添加：
```typescript
preview: {
  host: true, // 允许外部访问，禁用host检查
  port: 3000,
  allowedHosts: ['bands.icu', 'www.bands.icu', 'localhost', '127.0.0.1']
},
```

同时修改 `package.json` 的 preview 脚本：
```json
"preview": "vite preview --host"
```

### 4.4 重新构建和启动服务
```bash
# 重新构建前端应用
cd /opt/Bands/band-manager-front
npm run build

# 重启前端服务
pkill -f "npm run preview"
nohup npm run preview > frontend.log 2>&1 &

# 重启后端服务
cd /opt/Bands/BandManager
pkill -f "python3 app.py"
nohup python3 app.py > backend.log 2>&1 &
```

---

## 🧪 第五步：测试和验证

### 5.1 基础连接测试
```bash
# 测试HTTP重定向
curl -I http://bands.icu
# 应该返回 301 重定向到 https://bands.icu

# 测试HTTPS连接
curl -I https://bands.icu
# 应该返回 200 OK

# 测试API连接（子路径）
curl -k https://bands.icu/api/health
# 应该返回 200 OK 和 JSON 响应
```

### 5.2 SSL证书验证
```bash
# 检查SSL证书详情
openssl s_client -connect bands.icu:443 -servername bands.icu < /dev/null

# 使用在线工具检查SSL配置
# https://www.ssllabs.com/ssltest/analyze.html?d=bands.icu
```

### 5.3 功能测试
1. **访问主站**: https://bands.icu
2. **测试API**: https://bands.icu/api/health
3. **测试管理员登录**: 使用 admin-syx / syx002101
4. **测试文件上传**: 上传头像或图片
5. **测试邮件验证**: 发送验证码功能

### 5.4 性能测试
```bash
# 测试网站响应时间
curl -w "@curl-format.txt" -o /dev/null -s https://bands.icu

# curl-format.txt 内容：
#     time_namelookup:  %{time_namelookup}\n
#        time_connect:  %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#    time_pretransfer:  %{time_pretransfer}\n
#       time_redirect:  %{time_redirect}\n
#  time_starttransfer:  %{time_starttransfer}\n
#                     ----------\n
#          time_total:  %{time_total}\n
```

---

## 🚨 故障排除

### 常见问题及解决方案

#### 1. DNS解析未生效
```bash
# 清除本地DNS缓存
sudo systemctl flush-dns

# 使用不同DNS服务器测试
nslookup bands.icu 8.8.8.8
nslookup bands.icu 1.1.1.1
```

#### 2. SSL证书错误
```bash
# 检查证书文件权限
ls -la /etc/ssl/certs/bands.icu.pem
ls -la /etc/ssl/private/bands.icu.key

# 检查证书有效期
openssl x509 -in /etc/ssl/certs/bands.icu.pem -noout -dates

# 重新加载Nginx配置
sudo nginx -s reload
```

#### 3. 代理连接失败
```bash
# 检查后端服务状态
ps aux | grep python
netstat -tlnp | grep :5000

# 检查前端服务状态
ps aux | grep node
netstat -tlnp | grep :3000

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/bands.icu_error.log
```

#### 4. CORS跨域问题
- 确保后端CORS配置正确
- 检查前端API请求地址
- 验证Nginx CORS头设置

---

## 📊 配置完成检查清单

- [x] DNS解析配置完成并生效
- [x] Nginx安装并运行正常
- [x] SSL证书配置正确
- [x] HTTP自动重定向到HTTPS
- [x] 前端应用可通过 https://bands.icu 访问
- [x] 后端API可通过 https://bands.icu/api/ 访问
- [x] Vite Host检查配置正确
- [x] 应用功能测试正常
- [x] 文件上传功能正常
- [x] 邮件验证功能正常

---

## 🎯 最终访问地址

- **主站**: https://bands.icu
- **API**: https://bands.icu/api/
- **管理员**: admin-syx / syx002101

## 🔧 关键配置要点

1. **单域名架构**: 避免了子域名SSL证书问题
2. **子路径API**: API通过 `/api/` 路径访问，简化配置
3. **Vite Host配置**: 解决了生产环境Host检查问题
4. **Nginx代理**: 正确配置了前后端代理规则

---

## 📈 后续优化建议

1. **CDN加速**: 使用CloudFlare等CDN服务
2. **监控报警**: 配置服务监控和报警
3. **备份策略**: 定期备份数据和配置
4. **安全加固**: 定期更新SSL证书和安全配置
5. **性能优化**: 启用Gzip压缩和缓存优化

## 🎉 部署成功！

恭喜！你已经成功完成了域名和SSL的配置。现在可以通过 https://bands.icu 访问你的乐队管理系统了！

### 实际部署中遇到的关键问题和解决方案：

1. **SSL证书子域名问题**: 
   - 问题：证书不覆盖 `api.bands.icu` 子域名
   - 解决：采用单域名 + 子路径架构（`/api/`）

2. **Vite Host检查问题**:
   - 问题：生产环境下Vite阻止来自域名的请求
   - 解决：配置 `host: true` 和 `--host` 参数

3. **环境变量加载问题**:
   - 问题：Flask应用未正确加载 `.env` 文件
   - 解决：在 `app_factory.py` 中添加 `load_dotenv()`

4. **前端构建中的硬编码IP**:
   - 问题：前端代码包含旧服务器IP地址
   - 解决：使用 `sed` 批量替换并配置环境变量


