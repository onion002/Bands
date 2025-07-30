#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加认证系统支持
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_factory import create_app
from models import db, User, UserType, Band, Member, Event

def create_tables():
    """创建新的表结构"""
    print("创建数据库表...")
    
    # 创建所有表
    db.create_all()
    print("✓ 数据库表创建完成")

def add_owner_columns():
    """为现有表添加owner_id列"""
    print("添加owner_id列...")

    try:
        # 使用text()来执行原生SQL
        from sqlalchemy import text

        # 检查是否已经存在owner_id列
        inspector = db.inspect(db.engine)

        # 检查bands表
        bands_columns = [col['name'] for col in inspector.get_columns('bands')]
        if 'owner_id' not in bands_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE bands ADD COLUMN owner_id INTEGER'))
                conn.execute(text('ALTER TABLE bands ADD INDEX idx_bands_owner_id (owner_id)'))
                conn.commit()
            print("✓ bands表添加owner_id列")
        else:
            print("✓ bands表已有owner_id列")

        # 检查members表
        members_columns = [col['name'] for col in inspector.get_columns('members')]
        if 'owner_id' not in members_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE members ADD COLUMN owner_id INTEGER'))
                conn.execute(text('ALTER TABLE members ADD INDEX idx_members_owner_id (owner_id)'))
                conn.commit()
            print("✓ members表添加owner_id列")
        else:
            print("✓ members表已有owner_id列")

        # 检查events表
        events_columns = [col['name'] for col in inspector.get_columns('events')]
        if 'owner_id' not in events_columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE events ADD COLUMN owner_id INTEGER'))
                conn.execute(text('ALTER TABLE events ADD INDEX idx_events_owner_id (owner_id)'))
                conn.commit()
            print("✓ events表添加owner_id列")
        else:
            print("✓ events表已有owner_id列")

    except Exception as e:
        print(f"添加列时出错: {e}")
        # 如果是新数据库，这些错误是正常的

def create_default_admin():
    """创建默认管理员账户"""
    print("创建默认管理员账户...")
    
    # 检查是否已存在管理员
    existing_admin = User.query.filter_by(user_type=UserType.ADMIN).first()
    if existing_admin:
        print(f"✓ 管理员账户已存在: {existing_admin.username}")
        return existing_admin
    
    # 创建默认管理员
    admin_user = User(
        username='admin',
        email='admin@example.com',
        user_type=UserType.ADMIN,
        display_name='系统管理员',
        is_active=True
    )
    admin_user.set_password('admin123')  # 默认密码，建议首次登录后修改
    
    db.session.add(admin_user)
    db.session.commit()
    
    print(f"✓ 创建默认管理员: {admin_user.username}")
    print(f"  邮箱: {admin_user.email}")
    print(f"  密码: admin123 (请首次登录后修改)")
    
    return admin_user

def migrate_existing_data():
    """将现有数据关联到默认管理员"""
    print("迁移现有数据...")
    
    # 获取默认管理员
    admin_user = User.query.filter_by(user_type=UserType.ADMIN).first()
    if not admin_user:
        print("❌ 未找到管理员账户")
        return
    
    # 更新现有乐队数据
    bands_updated = 0
    for band in Band.query.filter_by(owner_id=None).all():
        band.owner_id = admin_user.id
        bands_updated += 1
    
    # 更新现有成员数据
    members_updated = 0
    for member in Member.query.filter_by(owner_id=None).all():
        member.owner_id = admin_user.id
        members_updated += 1
    
    # 更新现有活动数据
    events_updated = 0
    for event in Event.query.filter_by(owner_id=None).all():
        event.owner_id = admin_user.id
        events_updated += 1
    
    db.session.commit()
    
    print(f"✓ 更新了 {bands_updated} 个乐队")
    print(f"✓ 更新了 {members_updated} 个成员")
    print(f"✓ 更新了 {events_updated} 个活动")

def create_test_user():
    """创建测试普通用户"""
    print("创建测试用户...")
    
    # 检查是否已存在测试用户
    existing_user = User.query.filter_by(username='testuser').first()
    if existing_user:
        print(f"✓ 测试用户已存在: {existing_user.username}")
        return existing_user
    
    # 创建测试用户
    test_user = User(
        username='testuser',
        email='test@example.com',
        user_type=UserType.USER,
        display_name='测试用户',
        is_active=True
    )
    test_user.set_password('test123')
    
    db.session.add(test_user)
    db.session.commit()
    
    print(f"✓ 创建测试用户: {test_user.username}")
    print(f"  邮箱: {test_user.email}")
    print(f"  密码: test123")
    
    return test_user

def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")
    
    # 检查用户表
    admin_count = User.query.filter_by(user_type=UserType.ADMIN).count()
    user_count = User.query.filter_by(user_type=UserType.USER).count()
    print(f"✓ 管理员用户: {admin_count} 个")
    print(f"✓ 普通用户: {user_count} 个")
    
    # 检查数据关联
    admin_user = User.query.filter_by(user_type=UserType.ADMIN).first()
    if admin_user:
        bands_count = Band.query.filter_by(owner_id=admin_user.id).count()
        members_count = Member.query.filter_by(owner_id=admin_user.id).count()
        events_count = Event.query.filter_by(owner_id=admin_user.id).count()
        
        print(f"✓ 管理员 {admin_user.username} 拥有:")
        print(f"  - {bands_count} 个乐队")
        print(f"  - {members_count} 个成员")
        print(f"  - {events_count} 个活动")
    
    # 检查孤立数据
    orphan_bands = Band.query.filter_by(owner_id=None).count()
    orphan_members = Member.query.filter_by(owner_id=None).count()
    orphan_events = Event.query.filter_by(owner_id=None).count()
    
    if orphan_bands + orphan_members + orphan_events > 0:
        print(f"⚠️  发现孤立数据:")
        print(f"  - {orphan_bands} 个无主乐队")
        print(f"  - {orphan_members} 个无主成员")
        print(f"  - {orphan_events} 个无主活动")
    else:
        print("✓ 没有孤立数据")

def main():
    """主迁移函数"""
    print("=" * 50)
    print("乐队管理系统 - 认证系统迁移")
    print("=" * 50)
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 创建表结构
            create_tables()
            
            # 2. 添加owner_id列
            add_owner_columns()
            
            # 3. 创建默认管理员
            admin_user = create_default_admin()
            
            # 4. 迁移现有数据
            migrate_existing_data()
            
            # 5. 创建测试用户
            create_test_user()
            
            # 6. 验证迁移结果
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
