# 数据清理服务使用指南

## 概述

`cleanup_service.py` 是一个强大的数据清理工具，可以自动清理系统中的过期数据、孤立记录和未使用的文件。

## 功能特性

### 🔍 **数据清理**
- **过期邮箱验证码**: 自动删除已过期的邮箱验证码
- **旧举报记录**: 清理30天前已处理的举报记录
- **孤立点赞记录**: 删除指向不存在帖子/评论的点赞
- **已删除用户关联数据**: 清理已删除用户的所有关联数据（乐队、成员、活动、帖子、评论、点赞、举报）
- **孤立文件**: 清理未被数据库记录引用的图片文件

### 📁 **文件清理**
- **乐队图片**: `uploads/bands/` 目录下的孤立图片
- **成员头像**: `uploads/members/` 目录下的孤立头像
- **活动海报**: `uploads/events/` 目录下的孤立海报
- **用户头像**: `uploads/avatars/` 目录下的孤立头像
- **帖子图片**: `uploads/community/`, `uploads/posts/` 等目录下的孤立图片

## 使用方法

### 1. 基本用法

```bash
# 在项目根目录运行
cd E:\git-bands\BandManager

# 完整清理（默认模式）
python services/cleanup_service.py

# 快速清理（仅数据库数据）
python services/cleanup_service.py --mode quick

# 仅文件清理
python services/cleanup_service.py --mode files

# 查看清理状态
python services/cleanup_service.py --mode status
```

### 2. 高级选项

```bash
# 强制清理（跳过确认）
python services/cleanup_service.py --force

# 完整清理 + 强制模式
python services/cleanup_service.py --mode full --force

# 查看帮助
python services/cleanup_service.py --help
```

## 清理模式详解

### 🧹 **完整清理 (full)**
- 清理过期邮箱验证码
- 清理旧举报记录
- 清理孤立点赞记录
- 清理已删除用户关联数据
- 清理所有类型的孤立文件
- **推荐用于定期维护**

### ⚡ **快速清理 (quick)**
- 清理过期邮箱验证码
- 清理旧举报记录
- 清理孤立点赞记录
- 清理已删除用户关联数据
- **不清理文件，速度快**

### 🗂️ **文件清理 (files)**
- 仅清理孤立的图片文件
- 不清理数据库记录
- **适用于磁盘空间不足时**

### 📊 **状态查看 (status)**
- 显示可清理的数据统计
- 显示系统整体数据状态
- **不执行任何清理操作**

## 安全特性

### ✅ **确认机制**
- 默认需要用户确认才执行清理
- 使用 `--force` 参数可跳过确认
- 显示详细的清理计划

### 📝 **日志记录**
- 所有操作都会记录到日志
- 控制台实时显示清理进度
- 保存到 `cleanup_service.log` 文件

### 🔒 **数据保护**
- 只删除明确过期的数据
- 只删除孤立的文件
- 不会删除正在使用的资源

## 使用场景

### 🏠 **开发环境**
```bash
# 快速清理测试数据
python services/cleanup_service.py --mode quick

# 查看数据状态
python services/cleanup_service.py --mode status
```

### 🚀 **生产环境**
```bash
# 定期完整清理（建议每天凌晨执行）
python services/cleanup_service.py --mode full

# 紧急磁盘空间清理
python services/cleanup_service.py --mode files --force
```

### 🔧 **维护任务**
```bash
# 检查系统状态
python services/cleanup_service.py --mode status

# 清理特定类型数据
python services/cleanup_service.py --mode quick
```

## 注意事项

### ⚠️ **重要提醒**
1. **备份重要数据**: 清理前建议备份重要数据
2. **生产环境谨慎**: 在生产环境使用前先在测试环境验证
3. **定期执行**: 建议设置定时任务定期执行清理
4. **监控日志**: 定期检查清理日志，确保操作正常

### 🕐 **执行时间**
- **完整清理**: 根据数据量，通常需要几分钟到几十分钟
- **快速清理**: 通常几秒钟完成
- **文件清理**: 根据文件数量和大小，通常需要几秒钟到几分钟

### 📊 **清理效果**
- **数据库**: 减少数据库大小，提高查询性能
- **磁盘空间**: 释放未使用文件占用的磁盘空间
- **系统性能**: 清理孤立数据，提高系统整体性能

## 故障排除

### ❌ **常见问题**

1. **权限错误**
   ```bash
   # 确保有足够的文件系统权限
   # 检查 uploads 目录的读写权限
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库配置
   # 确保数据库服务正在运行
   ```

3. **文件删除失败**
   ```bash
   # 检查文件是否被其他进程占用
   # 检查磁盘空间是否充足
   ```

### 🔍 **调试方法**

```bash
# 查看详细日志
tail -f cleanup_service.log

# 使用状态模式检查
python services/cleanup_service.py --mode status

# 检查文件权限
ls -la uploads/
```

## 最佳实践

### 📅 **定时执行**
```bash
# 添加到 crontab（Linux/Mac）
0 2 * * * cd /path/to/BandManager && python services/cleanup_service.py --mode full --force

# Windows 计划任务
# 每天凌晨 2:00 执行完整清理
```

### 📊 **监控指标**
- 清理成功率
- 释放的磁盘空间
- 清理的数据量
- 执行时间

### 🔄 **维护计划**
- **每日**: 快速清理（过期验证码、孤立点赞）
- **每周**: 文件清理（孤立图片文件）
- **每月**: 完整清理（所有类型数据）

## 总结

`cleanup_service.py` 是一个功能完整、安全可靠的数据清理工具，能够有效维护系统数据健康，释放存储空间，提高系统性能。通过合理使用不同的清理模式，可以满足各种维护需求。
