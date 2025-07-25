#!/usr/bin/env python3
"""
检查数据库中的乐队图片使用情况
"""

import sys
import os

# 添加项目路径
sys.path.append('BandManager')

try:
    from models import Band, Member, db
    from app_factory import create_app
    
    def check_database():
        app = create_app()
        
        with app.app_context():
            print("数据库检查")
            print("=" * 40)
            
            # 检查所有乐队
            bands = Band.query.all()
            print(f"\n找到 {len(bands)} 个乐队:")
            
            target_file = "20250725150704_ComfyUI_00127_.png"
            file_in_use = False
            
            for band in bands:
                banner_url = band.banner_image_url or "无"
                if band.banner_image_url:
                    filename = band.banner_image_url.split('/')[-1]
                    if filename == target_file:
                        file_in_use = True
                        print(f"  ⚠️  乐队 {band.name} (ID: {band.id}) 正在使用文件: {target_file}")
                    else:
                        print(f"  - 乐队 {band.name} (ID: {band.id}), 图片: {filename}")
                else:
                    print(f"  - 乐队 {band.name} (ID: {band.id}), 图片: 无")
            
            print(f"\n目标文件 {target_file} 是否被使用: {'是' if file_in_use else '否'}")
            
            # 检查成员
            members = Member.query.all()
            print(f"\n找到 {len(members)} 个成员:")
            for member in members:
                avatar_url = member.avatar_url or "无"
                if member.avatar_url:
                    filename = member.avatar_url.split('/')[-1]
                    print(f"  - 成员 {member.name} (乐队ID: {member.band_id}), 头像: {filename}")
                else:
                    print(f"  - 成员 {member.name} (乐队ID: {member.band_id}), 头像: 无")
    
    if __name__ == "__main__":
        check_database()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在正确的目录中运行此脚本")
except Exception as e:
    print(f"运行错误: {e}")
