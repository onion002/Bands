# 新服务器部署指南

## 🎯 服务器信息
- **服务器IP**: 47.108.30.30
- **操作系统**: CentOS Stream 9
- **已安装软件**: Python、MySQL、Node.js、Redis

## 📋 部署步骤

### 第一步：上传代码到服务器

#### 方法1：使用rsync（推荐）
```bash
# 在本地项目根目录执行
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude 'dist' --exclude '__pycache__' --exclude '*.pyc' ./ root@47.108.30.30:/www/wwwroot/git-bands/
```

#### 方法2：使用scp
```bash
# 压缩项目
tar -czf git-bands.tar.gz --exclude='node_modules' --exclude='.git' --exclude='dist' --exclude='__pycache__' .

# 上传到服务器
scp git-bands.tar.gz root@47.108.30.30:/www/wwwroot/

# 登录服务器解压
ssh root@47.108.30.30
cd /www/wwwroot
tar -xzf git-bands.tar.gz
mv git-bands/* ./
rm -rf git-bands git-bands.tar.gz
```

### 第二步：登录服务器并配置环境

```bash
# 登录服务器
ssh root@47.108.30.30

# 进入项目目录
cd /www/wwwroot/git-bands

# 设置执行权限
chmod +x deploy/*.sh
```

### 第三步：运行部署脚本

```bash
# 运行一键部署脚本
./deploy/quick_deploy_all.sh
```

### 第四步：手动配置（如果自动脚本失败）

#### 4.1 配置后端环境
```bash
cd BandManager

# 安装Python依赖
pip3 install -r requirements.txt

# 配置环境变量（使用您现有的.env文件）
# 确保.env文件中的邮件配置正确

# 初始化数据库
python3 -c "from app_factory import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

#### 4.2 配置前端环境
```bash
cd band-manager-front

# 安装依赖
npm install

# 构建生产版本
npm run build
```

#### 4.3 启动服务

**启动后端服务：**
```bash
cd BandManager
nohup python3 app.py > backend.log 2>&1 &
```

**启动前端服务：**
```bash
cd band-manager-front
nohup npm run preview > frontend.log 2>&1 &
```

### 第五步：验证部署

1. **检查服务状态**
```bash
# 检查端口是否监听
netstat -tlnp | grep -E ':(3000|5000)'

# 检查进程
ps aux | grep -E '(python|node)'
```

2. **测试访问**
- 前端: http://47.108.30.30:3000
- 后端API: http://47.108.30.30:5000/health

## 🔧 常见问题

### Q: 端口被占用怎么办？
```bash
# 查看端口占用
netstat -tlnp | grep :5000
netstat -tlnp | grep :3000

# 杀死占用进程
kill -9 <PID>
```

### Q: 权限问题？
```bash
# 设置正确权限
chown -R root:root /www/wwwroot/git-bands
chmod -R 755 /www/wwwroot/git-bands
```

### Q: 防火墙问题？
```bash
# 开放端口
firewall-cmd --permanent --add-port=3000/tcp
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```

## 📞 技术支持

如果遇到问题，请提供：
1. 错误日志
2. 服务状态
3. 网络连接情况
