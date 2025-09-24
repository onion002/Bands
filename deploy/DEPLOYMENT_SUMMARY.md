# 乐队管理系统部署总结

## 📋 部署概览

**部署时间**: 2024年9月24日  
**服务器信息**: 
- IP地址: 47.108.30.30
- 操作系统: CentOS Stream 9
- 已安装服务: Python 3.13, Node.js v22.15.1, MySQL, Redis

**部署状态**: ✅ 成功部署并运行

## 🎯 系统架构

### 技术栈
- **前端**: Vue 3 + TypeScript + Vite + Pinia + Vue Router 4
- **后端**: Flask + Python 3.13 + SQLAlchemy + JWT
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **邮件服务**: Flask-Mail (QQ邮箱)
- **AI服务**: DeepSeek API (OpenAI兼容)

### 服务端口
- **前端服务**: http://47.108.30.30:3000
- **后端API**: http://47.108.30.30:5000
- **MySQL**: 3306
- **Redis**: 6379

## 🔧 关键修改记录

### 1. 后端修改
- **文件**: `BandManager/app_factory.py`
- **修改**: 添加 `from dotenv import load_dotenv` 和 `load_dotenv()`
- **原因**: 确保环境变量正确加载，解决邮件服务配置问题

### 2. 环境变量配置
- **后端**: 创建 `BandManager/.env` 文件
- **前端**: 创建 `band-manager-front/.env.production` 文件
- **关键配置**:
  ```bash
  API_BASE_URL=http://47.108.30.30:5000
  MAIL_USERNAME=3137826052@qq.com
  MAIL_PASSWORD=ptvporstvsbqdegc
  ```

### 3. 前端构建配置
- **文件**: `band-manager-front/vite.config.ts`
- **修改**: 更新代理配置指向新服务器IP
- **结果**: 前端API调用正确路由到后端服务

## 🚀 部署流程

### 1. 环境准备
```bash
# 检查系统环境
systemctl status mysql redis
python3 --version
node --version
npm --version
```

### 2. 代码部署
```bash
# 克隆项目
git clone https://github.com/onion002/Bands.git /opt/Bands

# 设置后端环境
cd /opt/Bands/BandManager
pip3 install -r requirements.txt
python3 -c "from app_factory import create_app; from models import db; app = create_app(); db.create_all()"

# 设置前端环境
cd /opt/Bands/band-manager-front
npm install
npm run build
```

### 3. 服务启动
```bash
# 启动后端
cd /opt/Bands/BandManager
nohup python3 app.py > backend.log 2>&1 &

# 启动前端
cd /opt/Bands/band-manager-front
nohup npm run preview > frontend.log 2>&1 &
```

## 🛠️ 问题解决记录

### 1. 邮件验证码发送失败
- **问题**: 500 Internal Server Error
- **原因**: 环境变量未正确加载
- **解决**: 在 `app_factory.py` 中添加 `load_dotenv()`

### 2. Python依赖冲突
- **问题**: `click==8.2.1` 版本不兼容
- **解决**: 先安装兼容版本 `click==8.1.7`

### 3. 前端构建失败
- **问题**: 缺少 `EmailVerificationDemo.vue` 文件
- **解决**: 创建占位符组件文件

### 4. 端口占用问题
- **问题**: 端口5000被占用
- **解决**: 查找并终止占用进程 `kill -9 PID`

### 5. API地址配置错误
- **问题**: 前端硬编码了错误的IP地址
- **解决**: 创建环境变量文件并重新构建

## 📁 部署脚本说明

### 1. `deploy.sh` - 一键部署脚本
- 自动检查系统环境
- 克隆/更新项目代码
- 配置后端和前端环境
- 启动所有服务
- 验证部署结果

### 2. `manage.sh` - 服务管理脚本
- 启动/停止/重启服务
- 查看服务状态和日志
- 更新代码和备份数据
- 提供完整的服务管理功能

## 🔐 默认账户信息

- **管理员账户**: admin-syx
- **密码**: syx002101
- **权限**: 超级管理员

## 📊 系统功能

### 核心功能
- ✅ 乐队管理
- ✅ 成员管理
- ✅ 演出活动管理
- ✅ 音乐社区
- ✅ 公开展示
- ✅ AI音乐顾问
- ✅ 用户认证系统
- ✅ 邮件验证
- ✅ 文件上传
- ✅ 数据统计

### 特色功能
- 🎵 音乐盒播放器
- 🎭 Live2D看板娘
- 📱 响应式设计
- 🌙 深色主题
- 🔍 实时搜索
- 📈 数据可视化

## 🔍 访问地址

- **前端应用**: http://47.108.30.30:3000
- **后端API**: http://47.108.30.30:5000
- **API文档**: http://47.108.30.30:5000/api/docs (如果配置)

## 📝 维护建议

### 1. 定期备份
```bash
# 使用管理脚本备份
./manage.sh backup
```

### 2. 日志监控
```bash
# 查看服务日志
./manage.sh logs all
```

### 3. 服务状态检查
```bash
# 检查服务状态
./manage.sh status
```

### 4. 代码更新
```bash
# 更新代码
./manage.sh update
```

## 🎉 部署成功确认

- ✅ 前端服务正常运行 (端口3000)
- ✅ 后端API服务正常运行 (端口5000)
- ✅ 数据库连接正常
- ✅ Redis缓存服务正常
- ✅ 邮件服务配置正确
- ✅ 用户登录功能正常
- ✅ 文件上传功能正常
- ✅ 所有核心功能可用

## 📞 技术支持

如遇到问题，请检查：
1. 服务状态: `./manage.sh status`
2. 服务日志: `./manage.sh logs all`
3. 网络连接: `netstat -tlnp | grep -E ':(3000|5000)'`
4. 防火墙设置: `firewall-cmd --list-all`

---

**部署完成时间**: 2024年9月24日  
**部署人员**: AI助手  
**系统状态**: 🟢 正常运行