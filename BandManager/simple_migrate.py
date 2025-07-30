#!/usr/bin/env python3
"""
简化的数据库迁移脚本
"""

import os
import sys
import mysql.connector
from werkzeug.security import generate_password_hash

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '002101',
    'database': 'band_db'
}

def connect_db():
    """连接数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"数据库连接失败: {e}")
        sys.exit(1)

def add_owner_columns():
    """添加owner_id列"""
    print("添加owner_id列...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 检查并添加bands表的owner_id列
        cursor.execute("SHOW COLUMNS FROM bands LIKE 'owner_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE bands ADD COLUMN owner_id INT")
            cursor.execute("ALTER TABLE bands ADD INDEX idx_bands_owner_id (owner_id)")
            print("✓ bands表添加owner_id列")
        else:
            print("✓ bands表已有owner_id列")
        
        # 检查并添加members表的owner_id列
        cursor.execute("SHOW COLUMNS FROM members LIKE 'owner_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE members ADD COLUMN owner_id INT")
            cursor.execute("ALTER TABLE members ADD INDEX idx_members_owner_id (owner_id)")
            print("✓ members表添加owner_id列")
        else:
            print("✓ members表已有owner_id列")
        
        # 检查并添加events表的owner_id列
        cursor.execute("SHOW COLUMNS FROM events LIKE 'owner_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE events ADD COLUMN owner_id INT")
            cursor.execute("ALTER TABLE events ADD INDEX idx_events_owner_id (owner_id)")
            print("✓ events表添加owner_id列")
        else:
            print("✓ events表已有owner_id列")
        
        conn.commit()
        
    except mysql.connector.Error as e:
        print(f"添加列失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def create_users_table():
    """创建users表"""
    print("创建users表...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 检查users表是否存在
        cursor.execute("SHOW TABLES LIKE 'users'")
        if cursor.fetchone():
            print("✓ users表已存在")
        else:
            # 创建users表
            create_table_sql = """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                user_type ENUM('ADMIN', 'USER') NOT NULL DEFAULT 'USER',
                display_name VARCHAR(100),
                avatar_url VARCHAR(255),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_users_username (username),
                INDEX idx_users_email (email)
            )
            """
            cursor.execute(create_table_sql)
            print("✓ users表创建成功")
        
        conn.commit()
        
    except mysql.connector.Error as e:
        print(f"创建users表失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def create_default_users():
    """创建默认用户"""
    print("创建默认用户...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 检查是否已有管理员
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'ADMIN'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # 创建默认管理员
            admin_password_hash = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, user_type, display_name)
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', 'admin@example.com', admin_password_hash, 'ADMIN', '系统管理员'))
            print("✓ 创建默认管理员: admin / admin123")
        else:
            print("✓ 管理员用户已存在")
        
        # 检查是否已有测试用户
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'testuser'")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # 创建测试用户
            user_password_hash = generate_password_hash('test123')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, user_type, display_name)
                VALUES (%s, %s, %s, %s, %s)
            """, ('testuser', 'test@example.com', user_password_hash, 'USER', '测试用户'))
            print("✓ 创建测试用户: testuser / test123")
        else:
            print("✓ 测试用户已存在")
        
        conn.commit()
        
    except mysql.connector.Error as e:
        print(f"创建用户失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def migrate_existing_data():
    """迁移现有数据"""
    print("迁移现有数据...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 获取管理员用户ID
        cursor.execute("SELECT id FROM users WHERE user_type = 'ADMIN' LIMIT 1")
        admin_result = cursor.fetchone()
        
        if not admin_result:
            print("❌ 未找到管理员用户")
            return
        
        admin_id = admin_result[0]
        
        # 更新bands表
        cursor.execute("UPDATE bands SET owner_id = %s WHERE owner_id IS NULL", (admin_id,))
        bands_updated = cursor.rowcount
        
        # 更新members表
        cursor.execute("UPDATE members SET owner_id = %s WHERE owner_id IS NULL", (admin_id,))
        members_updated = cursor.rowcount
        
        # 更新events表
        cursor.execute("UPDATE events SET owner_id = %s WHERE owner_id IS NULL", (admin_id,))
        events_updated = cursor.rowcount
        
        conn.commit()
        
        print(f"✓ 更新了 {bands_updated} 个乐队")
        print(f"✓ 更新了 {members_updated} 个成员")
        print(f"✓ 更新了 {events_updated} 个活动")
        
    except mysql.connector.Error as e:
        print(f"迁移数据失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 检查用户数量
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'ADMIN'")
        admin_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'USER'")
        user_count = cursor.fetchone()[0]
        
        print(f"✓ 管理员用户: {admin_count} 个")
        print(f"✓ 普通用户: {user_count} 个")
        
        # 检查数据关联
        cursor.execute("SELECT id FROM users WHERE user_type = 'ADMIN' LIMIT 1")
        admin_result = cursor.fetchone()
        
        if admin_result:
            admin_id = admin_result[0]
            
            cursor.execute("SELECT COUNT(*) FROM bands WHERE owner_id = %s", (admin_id,))
            bands_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM members WHERE owner_id = %s", (admin_id,))
            members_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM events WHERE owner_id = %s", (admin_id,))
            events_count = cursor.fetchone()[0]
            
            print(f"✓ 管理员拥有:")
            print(f"  - {bands_count} 个乐队")
            print(f"  - {members_count} 个成员")
            print(f"  - {events_count} 个活动")
        
        # 检查孤立数据
        cursor.execute("SELECT COUNT(*) FROM bands WHERE owner_id IS NULL")
        orphan_bands = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM members WHERE owner_id IS NULL")
        orphan_members = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM events WHERE owner_id IS NULL")
        orphan_events = cursor.fetchone()[0]
        
        if orphan_bands + orphan_members + orphan_events > 0:
            print(f"⚠️  发现孤立数据:")
            print(f"  - {orphan_bands} 个无主乐队")
            print(f"  - {orphan_members} 个无主成员")
            print(f"  - {orphan_events} 个无主活动")
        else:
            print("✓ 没有孤立数据")
        
    except mysql.connector.Error as e:
        print(f"验证失败: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("=" * 50)
    print("乐队管理系统 - 简化认证系统迁移")
    print("=" * 50)
    
    try:
        # 1. 创建users表
        create_users_table()
        
        # 2. 添加owner_id列
        add_owner_columns()
        
        # 3. 创建默认用户
        create_default_users()
        
        # 4. 迁移现有数据
        migrate_existing_data()
        
        # 5. 验证迁移结果
        verify_migration()
        
        print("\n" + "=" * 50)
        print("✅ 迁移完成!")
        print("=" * 50)
        print("\n登录信息:")
        print("管理员账户: admin / admin123")
        print("测试账户: testuser / test123")
        print("\n请在首次登录后修改默认密码!")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
