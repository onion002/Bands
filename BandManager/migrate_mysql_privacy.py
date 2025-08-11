#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL数据库隐私设置字段迁移脚本
为users表添加bands_public, members_public, events_public字段
"""

import mysql.connector
from mysql.connector import Error

def migrate_mysql_privacy():
    """迁移MySQL数据库，添加隐私设置字段"""
    
    try:
        # 连接MySQL数据库
        print("🔌 连接到MySQL数据库...")
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='002101',
            database='band_db'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 检查当前表结构
            print("📋 检查当前users表结构...")
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            
            print("当前users表列:")
            existing_columns = []
            for col in columns:
                print(f"  {col[0]} ({col[1]})")
                existing_columns.append(col[0])
            
            # 需要添加的字段
            new_columns = [
                ('bands_public', 'BOOLEAN DEFAULT FALSE'),
                ('members_public', 'BOOLEAN DEFAULT FALSE'),
                ('events_public', 'BOOLEAN DEFAULT FALSE')
            ]
            
            # 添加缺失的字段
            for col_name, col_def in new_columns:
                if col_name not in existing_columns:
                    print(f"➕ 添加 {col_name} 字段...")
                    try:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
                        print(f"✅ {col_name} 字段添加成功")
                    except Error as e:
                        print(f"❌ 添加 {col_name} 字段失败: {e}")
                else:
                    print(f"ℹ️ {col_name} 字段已存在")
            
            # 提交更改
            connection.commit()
            print("💾 数据库更改已提交")
            
            # 验证最终表结构
            print("\n📋 验证最终users表结构...")
            cursor.execute("DESCRIBE users")
            final_columns = cursor.fetchall()
            
            print("最终users表列:")
            for col in final_columns:
                print(f"  {col[0]} ({col[1]})")
            
            # 检查是否有数据需要初始化
            print("\n🔍 检查现有用户数据...")
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"当前用户数量: {user_count}")
            
            if user_count > 0:
                # 更新现有用户的隐私设置为默认值（False）
                print("🔄 初始化现有用户的隐私设置...")
                cursor.execute("""
                    UPDATE users 
                    SET bands_public = FALSE, 
                        members_public = FALSE, 
                        events_public = FALSE 
                    WHERE bands_public IS NULL 
                       OR members_public IS NULL 
                       OR events_public IS NULL
                """)
                
                updated_rows = cursor.rowcount
                if updated_rows > 0:
                    print(f"✅ 更新了 {updated_rows} 个用户的隐私设置")
                    connection.commit()
                else:
                    print("ℹ️ 所有用户的隐私设置都已正确初始化")
            
            print("\n🎉 MySQL数据库迁移完成！")
            
        else:
            print("❌ 无法连接到MySQL数据库")
            
    except Error as e:
        print(f"❌ MySQL连接错误: {e}")
        
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 MySQL连接已关闭")

if __name__ == "__main__":
    print("🚀 开始MySQL数据库隐私设置迁移...")
    migrate_mysql_privacy()
    print("✨ 迁移脚本执行完成")
