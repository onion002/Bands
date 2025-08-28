# 🎵 乐队管理系统 (Band)

一个现代化的全栈乐队管理平台，提供乐队信息管理、成员管理、活动组织以及音乐作品展示和社区交流等功能。  
[点击试用](http://47.107.79.244:3000/)  
请先查看[用户使用指南(USER_GUIDE.md)](./USER_GUIDE.md)，再阅读技术细节😜

> ⚠️ **重要声明**
>
> 本项目源代码仅作为**技术展示和参考**之用。
> - **允许**：浏览、学习、提交 Issue 和讨论。
> - **禁止**：**未经明确授权，严禁克隆、复制、分发或用于任何商业目的。**
> 如有特殊需求，请联系 [3137826052@qq.com]。
>  
---
## 💖特别感谢： 
- 1.[落月API](https://doc.vkeys.cn/api-doc/v2/%E9%9F%B3%E4%B9%90%E6%A8%A1%E5%9D%97/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90/1-netease.html)对于音乐盒使用的支持  
- 2.[保罗看板娘插件](https://paul.ren/project/pio)的看板娘为页面带来的活力  
  再次感谢各位开源大佬的帮助🥰

## 📖 项目简介

本系统采用前后端分离架构，为音乐爱好者提供交流平台，为专业音乐人和乐队经理提供一站式管理解决方案：

- **🎯 核心功能**：乐队管理、成员管理、活动组织、音乐作品展示
- **👥 用户类型**：管理员（完整权限）、普通用户（只读访问）
- **🎨 特色功能**：音乐盒播放器、看板娘交互、实时数据统计
- **📱 响应式设计**：支持桌面端和移动端访问

## 🏗️ 技术栈

### 前端技术
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **样式**: SCSS + 响应式设计
- **HTTP客户端**: Axios
- **特色组件**: Live2D看板娘

### 后端技术
- **框架**: Flask + Python 3.13
- **数据库**: MySQL
- **缓存**: Redis
- **认证**: JWT + 开发者密钥
- **文件存储**: 本地文件系统
- **部署**: Gunicorn + 进程管理

## 📁 项目结构

```
git-bands/
├── band-manager-front/          # 前端项目
│   ├── src/
│   │   ├── components/          # 可复用组件
│   │   ├── views/              # 页面组件
│   │   ├── api/                # API 服务
│   │   ├── stores/             # 状态管理
│   │   ├── modules/            # 功能模块
│   │   └── assets/             # 静态资源
│   ├── public/                 # 公共资源
│   └── package.json
├── BandManager/                 # 后端项目
│   ├── api/                    # API 路由
│   ├── models.py               # 数据模型
│   ├── services/               # 业务服务
│   ├── uploads/                # 文件上传目录
│   └── requirements.txt
├── deploy/                     # 部署脚本
├── docs/                       # 项目文档
└── README.md                   # 本文档  
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.9+
- **Node.js**: 16+
- **MySQL**: 5.7+
- **Redis**: 6.0+

### 本地开发环境搭建

#### 1. 克隆项目

```bash
git clone <repository-url>
cd git-bands
```

#### 2. 后端环境配置

```bash
# 进入后端目录
cd BandManager

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate
# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 数据库配置

```bash
# 创建MySQL数据库
mysql -u root -p
CREATE DATABASE band_manager;
```

#### 4. 环境变量配置

在 `BandManager` 目录下创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost/band_manager

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT密钥
JWT_SECRET_KEY=your-jwt-secret-key

# 开发者密钥（管理员注册必需）
DEVELOPER_SECRET_KEY=your-developer-key

# 邮件服务配置（可选）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### 5. 前端环境配置

```bash
# 进入前端目录
cd band-manager-front

# 安装依赖
npm install

# 配置环境变量（创建 .env.local）
echo "VITE_API_BASE_URL=http://localhost:5000" > .env.local
```

#### 6. 启动服务

```bash
# 启动后端服务
cd BandManager
python app.py

# 启动前端服务（新终端）
cd band-manager-front
npm run dev
```

访问地址：
- 前端：http://localhost:3000
- 后端API：http://localhost:5000

## 🔧 主要功能

### 👤 用户管理
- **管理员注册**：需要开发者密钥验证
- **用户登录**：JWT令牌认证
- **邮箱验证**：确保账户安全
- **权限控制**：多级权限管理

### 🎵 乐队管理
- **乐队信息**：名称、描述、封面图片
- **成员管理**：添加/编辑/删除成员
- **角色分配**：主唱、吉他手、贝斯手等
- **活动组织**：创建和管理乐队活动

### 🎼 音乐功能
- **音乐盒**：内置音乐播放器
- **作品展示**：音乐作品上传和展示
- **音乐老师**：AI音乐助手（集成DeepSeek API）

### 🎨 特色功能
- **看板娘**：Live2D动画角色交互
- **数据统计**：实时数据分析和图表
- **响应式设计**：适配各种设备屏幕
- **暗色主题**：现代化UI设计

## 📱 页面功能

### 🏠 主页 (/)
- 未登录用户展示系统介绍
- 已登录用户显示个人仪表板
- 快速导航到各功能模块

### 🔐 认证页面 (/auth)
- **登录页** (`/auth/login`)：用户登录
- **注册页** (`/auth/register`)：管理员注册

### 🎵 乐队相关 (/bands)
- **乐队列表** (`/bands`)：显示所有乐队
- **乐队详情** (`/bands/:id`)：查看乐队详细信息
- **成员管理** (`/bands/:id/members`)：管理乐队成员
- **活动管理** (`/bands/:id/events`)：管理乐队活动

### 👁️ 公开页面 (/public)
- 无需登录即可访问
- 展示精选乐队和作品
- 提供公开的音乐欣赏体验

### 🎓 音乐老师 (/music-teacher)
- AI音乐助手功能
- 音乐理论学习
- 乐器教学指导

### ⚙️ 管理后台 (/admin)
- 系统统计数据
- 用户管理
- 系统配置

## 🌐 部署指南

### 生产环境部署

#### 1. 使用自动化部署脚本

```bash
# 进入部署目录
cd deploy

# 给脚本执行权限
chmod +x quick_deploy_all.sh

# 运行自动部署
./quick_deploy_all.sh
```

#### 2. 手动部署步骤

```bash
# 1. 安装系统依赖
sudo yum update -y
sudo yum install -y mysql-server redis nodejs npm python3 python3-pip

# 2. 启动数据库服务
sudo systemctl start mysqld redis
sudo systemctl enable mysqld redis

# 3. 配置防火墙
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# 4. 部署后端
cd BandManager
pip3 install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 5. 部署前端
cd band-manager-front
npm install
npm run build
npm install -g serve
serve -s dist -l 3000
```

#### 3. 使用Docker部署

```bash
# 构建镜像
docker build -t band-manager .

# 运行容器
docker run -d -p 3000:3000 -p 5000:5000 band-manager
```

### 生产环境配置

#### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 文件上传
    client_max_body_size 16M;
}
```

## 🛠️ 开发指南

### 代码规范

- **前端**：使用ESLint + Prettier
- **后端**：遵循PEP 8规范
- **Git提交**：使用语义化提交信息

### 开发工作流

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发并测试
npm run lint  # 前端代码检查
npm run type-check  # 类型检查

# 3. 提交代码
git add .
git commit -m "feat: 添加新功能"

# 4. 推送并创建PR
git push origin feature/new-feature
```

### API开发

#### 添加新的API端点

```python
# 在 BandManager/api/ 目录下创建新的路由文件
from flask import Blueprint, request, jsonify
from auth_decorators import require_auth

bp = Blueprint('new_feature', __name__)

@bp.route('/api/new-endpoint', methods=['GET'])
@require_auth
def get_data():
    return jsonify({"message": "Hello World"})
```

#### 前端API调用

```typescript
// 在 band-manager-front/src/api/ 目录下创建服务文件
import { apiRequest } from './base'

export const newFeatureService = {
  getData: () => apiRequest.get('/api/new-endpoint'),
  createData: (data: any) => apiRequest.post('/api/new-endpoint', data)
}
```

## 🔍 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查MySQL服务状态
sudo systemctl status mysqld

# 检查数据库配置
mysql -u root -p -e "SHOW DATABASES;"
```

#### 2. Redis连接失败
```bash
# 检查Redis服务状态
sudo systemctl status redis

# 测试Redis连接
redis-cli ping
```

#### 3. 前端构建失败
```bash
# 清除缓存并重新安装
rm -rf node_modules package-lock.json
npm install

# 检查Node.js版本
node --version  # 应该 >= 16
```

#### 4. CORS错误
确保在 `.env` 文件中正确配置了CORS源：
```env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 日志查看

```bash
# 查看后端日志
tail -f BandManager/app.log

# 查看前端开发服务器日志
npm run dev  # 在终端中查看输出

# 查看系统服务日志
sudo journalctl -u your-service-name -f
```

## 📚 相关文档

- [认证系统设计](docs/AUTH_SYSTEM_DESIGN.md)
- [组件使用指南](docs/COMPONENT_USAGE_GUIDE.md)
- [部署指南](docs/DEPLOYMENT.md)
- [看板娘使用指南](docs/POSTER_GIRL_USAGE_GUIDE.md)
- [音乐盒实现说明](docs/MUSIC_BOX_IMPLEMENTATION.md)

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件（暂无）。

## 📞 联系方式

- **项目维护者**: 宋*贤
- **邮箱**: 3137826052@qq.com
- **问题反馈**:QQ群：693736489

## 🙏 致谢

感谢以下开源项目的支持：
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Flask](https://flask.palletsprojects.com/) - 轻量级Python Web框架
- [Live2D](https://www.live2d.com/) - 2D动画技术
- [Vite](https://vitejs.dev/) - 现代化构建工具

---

💡 **提示**: 如果您在使用过程中遇到任何问题，请先查阅相关文档，或在 Issues 中搜索类似问题。
