# migrate.py

from app_factory import create_app
from models import db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# 创建应用实例
app = create_app()

# 设置迁移管理器
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()