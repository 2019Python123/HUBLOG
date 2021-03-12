from . import db
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime, timedelta, timezone
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import login_manager
import bleach
from markdown import markdown
from faker import Faker
from random import randint
from sqlalchemy.exc import IntegrityError


class Personal(db.Model):
    __tablename__ = 'personals'
    id = db.Column(db.Integer, primary_key=True)
    is_personal = db.Column(db.Boolean, default=False)
    is_show_collect_post = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Reply(db.Model):
    __tablename__ = 'replies'
    replier_id = db.Column(db.Integer, db.ForeignKey('comments.id'), primary_key=True)
    replied_id = db.Column(db.Integer, db.ForeignKey('comments.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Follow(db.Model):
    # 重新命名这个表
    __tablename__ = 'follows'
    # 关注者id
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # 被关注者id
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # 关注时间
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Collect(db.Model):
    __tablename__ = 'collections'
    collector_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    collected_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)


# 程序权限
class Permission:
    # 关注别人的权限
    FOLLOW = 0x01
    # 评论权限
    COMMENT = 0x02
    # 写文章权限
    WRITE_ARTICLES = 0x04
    # 协住管理员权限
    MODERATE_COMMENTS = 0x08
    # 管理员权限
    ADMINISTER = 0x80


# 储存评论表
class Comment(db.Model):
    # 命名
    __tablename__ = 'comments'
    # 评论id
    id = db.Column(db.Integer, primary_key=True)
    # 评论内容
    body = db.Column(db.Text())

    # 是否被管理员审核
    allowed_by_admin = db.Column(db.Boolean, default=False)
    # 发布此评论的作者
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 评论文章的id
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    # 是不是评论文章的
    is_post_comment = db.Column(db.Boolean, default=True
                                )
    # 评论时间
    timestamp = db.Column(db.DateTime, default=datetime.now)
    replier = db.relationship('Reply',
                              foreign_keys=[Reply.replier_id],
                              backref=db.backref('replier', lazy='joined'),
                              lazy='dynamic',
                              cascade='all,delete-orphan')
    replied = db.relationship('Reply',
                              foreign_keys=[Reply.replied_id],
                              backref=db.backref('replied', lazy='joined'),
                              lazy='dynamic',
                              cascade='all,delete-orphan')

    def reply_(self, comment):
        r = Reply(replied=comment, replier=self)
        db.session.add(r)
        db.session.commit()


class Post(db.Model):
    __tablename__ = 'posts'
    # 文章id
    id = db.Column(db.Integer, primary_key=True)
    # 文章标题
    title = db.Column(db.String(32))
    # 文章主体
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    # 文章作者id
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # 与评论表关联
    comments = db.relationship('Comment', backref='comments', lazy='dynamic')
    # 被谁收藏的用户id
    collected_users = db.relationship('Collect',
                                      foreign_keys=[Collect.collected_post_id],
                                      backref=db.backref('collected_post', lazy='joined'),
                                      lazy='dynamic',
                                      cascade='all,delete-orphan')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category', back_populates='posts')
    # 是否关闭评论
    is_mute = db.Column(db.Boolean, default=False)
    # 是否私密文章
    is_personal_post = db.Column(db.Boolean, default=False)
    # 是否显示评论
    is_show_comment = db.Column(db.Boolean, default=True)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class', 'style'],
            'a': ['href', 'rel'],
            'img': ['alt', 'src'],
        }
        styles = ['height', 'width']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attrs, styles=styles, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)


# 角色表
class Role(db.Model):
    # 命名
    __tablename__ = 'roles'
    # 角色id
    id = db.Column(db.Integer, primary_key=True)
    # 角色名
    name = db.Column(db.String(36), unique=True)
    # 默认注册后的角色，否则赋予其他角色
    default = db.Column(db.Boolean, default=False)
    # 权限值
    permission = db.Column(db.Integer)
    # 与user表关联
    users = db.relationship('User', backref='role', lazy='dynamic')


    # 静态函数，用来更新角色表
    @staticmethod
    def insert_role():
        # 角色字典
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'For_words_user': (Permission.FOLLOW |
                               Permission.WRITE_ARTICLES, False),
            'For_write_user': (Permission.FOLLOW |
                               Permission.COMMENT, False),
            'For_follow_user': (Permission.COMMENT |
                                Permission.WRITE_ARTICLES, False),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        # 角色字典遍历
        for r in roles:
            # 查询是否有上面的角色字典里的角色
            role = Role.query.filter_by(name=r).first()
            # 如果没有
            if role is None:
                # 将角色字典的值填充数据库角色表新的一行记录
                role = Role(name=r)
            role.default = roles[r][1]
            role.permission = roles[r][0]
            # 将这个记录加到会话中
            db.session.add(role)
        # 向数据库提交会话
        db.session.commit()


# 用户模型
class User(UserMixin, db.Model):
    # 重新命名这个表名
    __tablename__ = 'users'
    # 用户唯一标识
    id = db.Column(db.Integer, primary_key=True)
    # 角色id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 用户邮箱
    email = db.Column(db.String(128), unique=True, index=True)
    # 用户昵称
    username = db.Column(db.String(12), unique=True, index=True)
    # 用哈希密码储存的用户密码
    password_hash = db.Column(db.String(128))
    # 用户头像名
    real_avatar = db.Column(db.String(128),default='default.ico')
    # 性别
    sex = db.Column(db.String)
    # 年龄
    age = db.Column(db.Integer)
    # 地区
    location = db.Column(db.String(128))
    # 生日
    birthday = db.Column(db.Date)
    # 个性签名
    about_me = db.Column(db.Text())
    # 登录状态
    online = db.Column(db.Boolean, default=False)
    # 与posts表关联
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 与comments表关联
    comments = db.relationship('Comment', backref='author_', lazy='dynamic')
    # 被关注者
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    # 关注者
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all,delete-orphan')
    # 收藏的文章
    collection_posts = db.relationship('Collect',
                                       foreign_keys=[Collect.collector_id],
                                       backref=db.backref('collector', lazy='joined'),
                                       lazy='dynamic',
                                       cascade='all,delete-orphan')
    # 是否只能给自己亲近的人看文章
    is_personal = db.relationship('Personal',
                                  backref='personal_user',
                                  lazy='dynamic'
                                  )
    is_show_fans = db.Column(db.Boolean, default=True)
    is_show_followed = db.Column(db.Boolean, default=True)
    # 是否认证
    confirmed = db.Column(db.Boolean, default=False)
    # 注册的时间
    logon_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    # 登录的时间
    login_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    # 初始化user对象
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role_id = Role.query.filter_by(id=6).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    # 将函数变成属性
    @property
    def password(self):
        return self.password_hash

    # 给password_hash赋值
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 定义函数用来检查密码
    def verify_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.online = True
        self.login_time = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def out_online(self):
        self.online = False
        db.session.add(self)
        db.session.commit()

    def can_follow(self, user):
        return not Follow.query.filter_by(followed_id=User.query.filter_by(username=user.username).first().id,
                                          follower_id=self.id).first()

    def following(self, user):
        return Follow.query.filter_by(followed_id=User.query.filter_by(username=user.username).first().id,
                                      follower_id=self.id).first()

    def follow(self, user):
        if self.can_follow(user):
            follow = Follow(
                follower=self,
                followed=user
            )
            db.session.add(follow)
            db.session.commit()

    def un_follow(self, user):
        if self.following(user):
            follow = Follow.query.filter_by(followed_id=user.id, follower_id=self.id).first()
            db.session.delete(follow)
            db.session.commit()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permission & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


# flask_login需要用户的id来管理用户登录的情况
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String, unique=True)
    posts = db.relationship('Post', back_populates='category', lazy='dynamic')


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


# class Message(db.Model):
#     __tablename__ = 'messages'
#     id = db.Column(db.Integer,primary_key=True)
#     op_body = db.Column(db.String)
#     del_post = db.Column(db.Boolean)
#     del_post_title = db.Column(db.String)
#     del_user = db.Column(db.Boolean)
#     del_comment = db.Column(db.Boolean)
#     del_comment_body =
#     del_category = db.Column(db.Boolean)
#     op_object = db.Column(db.String)


