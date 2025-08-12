# 乐队删除逻辑优化

## 问题描述
原有的删除乐队逻辑存在以下问题：
1. 只删除当前的banner图片，不删除历史图片
2. 不删除该乐队成员的头像图片
3. 可能导致uploads目录中积累大量孤立的图片文件
4. **新发现问题**：通过upload_image端点上传的图片使用不同的命名格式，无法被原删除逻辑识别

## 图片命名格式分析
系统中存在两种图片命名格式：
- **格式1**：`band_{乐队名}_{时间戳}.{扩展名}` (创建/更新乐队时)
- **格式2**：`{时间戳}_{原始文件名}` (upload_image端点)

格式2的文件不包含乐队信息，导致删除时无法准确识别归属。

## 优化方案

### 1. 增强的删除函数 `delete_band_related_images()`

**功能**：
- 删除乐队的所有历史图片（基于文件名模式匹配）
- 删除该乐队所有成员的当前头像
- 删除该乐队所有成员的历史头像

**文件名匹配模式**：
- 乐队图片：`band_{safe_name}_{timestamp}.{ext}`
- 成员头像：`member_{safe_name}_{timestamp}.{ext}`

**支持的图片格式**：jpg, jpeg, png, gif, webp

### 2. 优化的API端点

#### 单个删除：`DELETE /api/bands/{id}`
- 使用增强的删除函数
- 返回删除的文件数量
- 自动删除关联的成员记录（cascade删除）

#### 批量删除：`POST /api/bands/batch_delete`
- 接受乐队ID列表
- 批量处理，提高效率
- 返回详细的删除统计信息

**请求格式**：
```json
{
  "band_ids": [1, 2, 3]
}
```

**响应格式**：
```json
{
  "message": "成功删除 3 个乐队",
  "deleted_bands": [
    {
      "id": 1,
      "name": "乐队名称",
      "deleted_files_count": 5
    }
  ],
  "total_deleted_files": 15
}
```

#### 清理孤立图片：`POST /api/bands/cleanup_orphaned_images`
- 清理没有被数据库记录引用的图片文件
- 分别处理bands和members目录
- 返回清理的文件列表

#### 强制清理乐队图片：`POST /api/bands/{id}/cleanup_all_images`
- 专门用于清理指定乐队的所有可能相关图片
- 处理格式1和格式2的文件
- 保护其他乐队正在使用的图片
- 返回清理的文件列表

#### 强制清理所有未使用图片：`POST /api/bands/force_cleanup_all_unused_images`
- **新增API**：解决格式2文件删除问题
- 删除所有未被任何乐队使用的图片文件
- 不区分文件格式，只要未被使用就删除
- 返回详细的清理统计和使用情况

**响应格式**：
```json
{
  "message": "强制清理完成，删除了 X 个未使用的图片文件",
  "deleted_files": ["20250725150704_ComfyUI_00127_.png"],
  "deleted_files_count": 1,
  "used_images": ["current_band_image.jpg"]
}
```

### 3. 前端优化

#### 确认对话框增强
- 明确告知用户删除操作的影响范围
- 包含删除图片和成员记录的警告

#### 批量删除优化
- 使用新的批量删除API
- 显示删除进度和结果统计

#### 错误处理改进
- 更详细的错误信息显示
- 区分不同类型的删除失败

## 使用示例

### 前端调用
```typescript
// 单个删除（增强版）
// 1. 先强制清理图片
await BandService.cleanupAllBandImages(bandId)
// 2. 删除乐队
await BandService.deleteBand(bandId)

// 批量删除（增强版）
// 1. 先为每个乐队强制清理图片
await Promise.all(bandIds.map(id => BandService.cleanupAllBandImages(id)))
// 2. 批量删除乐队
await BandService.batchDeleteBands(bandIds)

// 清理孤立图片
await BandService.cleanupOrphanedImages()

// 强制清理所有未使用的图片（解决格式2文件问题）
await BandService.forceCleanupAllUnusedImages()
```

### 确认对话框
```
确定删除乐队 "乐队名称" 吗？

⚠️ 此操作将同时删除：
• 乐队的所有历史图片
• 乐队成员的所有头像
• 乐队成员记录

此操作不可撤销！
```

## 技术实现细节

### 文件匹配逻辑
```python
# 乐队图片匹配模式
patterns = [
    f"band_{safe_band_name}_*.jpg",
    f"band_{safe_band_name}_*.jpeg", 
    f"band_{safe_band_name}_*.png",
    f"band_{safe_band_name}_*.gif",
    f"band_{safe_band_name}_*.webp"
]

# 使用glob进行文件匹配
matching_files = glob.glob(os.path.join(bands_upload_dir, pattern))
```

### 安全性考虑
- 文件名安全化处理（替换空格为下划线）
- 异常处理，单个文件删除失败不影响整体操作
- 详细的日志记录

### 数据库一致性
- 使用事务确保数据一致性
- cascade删除确保关联记录正确删除
- 回滚机制处理异常情况

## 优化效果

### ✅ 彻底清理
- 删除乐队时完全清理相关文件
- 避免磁盘空间浪费
- 保持uploads目录整洁

### ✅ 用户体验
- 明确的操作提示
- 详细的删除结果反馈
- 批量操作提高效率

### ✅ 系统维护
- 提供孤立文件清理功能
- 详细的操作日志
- 错误处理和恢复机制

## 注意事项

1. **不可逆操作**：删除操作无法撤销，需要用户明确确认
2. **性能考虑**：大量文件删除可能需要时间，建议在低峰期进行
3. **备份建议**：重要数据删除前建议先备份
4. **权限检查**：确保应用有足够权限删除文件

## 测试验证

提供了测试脚本 `test_band_deletion.py` 来验证删除功能：

```bash
cd git-bands
python test_band_deletion.py
```

测试脚本会：
1. 检查uploads目录状态
2. 获取现有乐队和成员信息
3. 执行强制清理图片
4. 删除测试乐队
5. 验证删除结果
6. 清理孤立图片

## 解决方案总结

### ✅ 已解决的问题
1. **格式1图片删除**：正确删除 `band_{name}_{timestamp}.{ext}` 格式的图片
2. **当前图片删除**：删除数据库中记录的当前banner图片
3. **成员头像删除**：删除所有成员的当前和历史头像
4. **格式2图片处理**：通过强制清理API处理 `{timestamp}_{filename}` 格式的图片
5. **安全保护**：避免删除其他乐队正在使用的图片

### 🔧 技术改进
1. **两阶段删除**：先清理图片，再删除数据库记录
2. **智能识别**：区分不同格式的图片文件
3. **安全检查**：保护其他乐队的图片不被误删
4. **详细日志**：记录所有删除操作
5. **错误处理**：单个文件删除失败不影响整体操作

## 未来扩展

1. **图片关联表**：创建专门的表记录图片与乐队的关联关系
2. **统一命名格式**：标准化所有图片的命名格式
3. **软删除选项**：可以考虑添加软删除功能
4. **回收站机制**：删除的文件可以先移动到回收站
5. **定时清理**：定期自动清理孤立文件
6. **删除审计**：记录详细的删除操作日志
