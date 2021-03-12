from flask_script import Shell,Manager
from flask_migrate import MigrateCommand,Migrate
from app import db,create_app
from app.models import User,Role,Post
from app.fakes import fake_post,fake_user,fake_comment,fake_collect,fake_personal

# 实例化app
app = create_app()
# 数据库迁移类的实例化对象
migrate = Migrate(app,db)
# 创建脚本管理类实例化对象
manager = Manager(app)
# 将数据库迁移命令添加到终端命令里
manager.add_command('db',MigrateCommand)


def make_shell_context():
    return dict(db=db,User=User,Role=Role,Post=Post,fake_post=fake_post,fake_user=fake_user,fake_comment=fake_comment,fake_collect=fake_collect,fake_personal=fake_personal)


# 将上面函数里的db,user,post添加到终端命令里,使用python manage.py shell 可以直接用这些对象
manager.add_command('shell',Shell(make_context=make_shell_context))


if __name__ == '__main__':
    app.run()