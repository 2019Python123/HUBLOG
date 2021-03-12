from app import db
from app.models import User,Post,Comment,Collect,Follow,Reply,Category,Personal
from faker import Faker
from random import randint

fake = Faker(locale='zh_CN')


def fake_user(count=20):
    for i in range(count):
        # 实例化User类
        u = User(
            email=fake.email(),
            username=fake.name(),
            password='cat',
        )
        db.session.add(u)
    db.session.commit()


def fake_post(count=100):
    user_count = User.query.count()
    category_count = Category.query.count()
    for i in range(count):
        # 实例化Post类
        u = User.query.offset(randint(0, user_count - 1)).first()
        c = Category.query.offset(randint(0,category_count-1)).first()
        p = Post(
            title=fake.sentence(4),
            body=fake.text(2000),
            author=u,
            category=c,
            is_mute=False,
            is_personal_post=False,
            is_show_comment=False
        )
        db.session.add(p)
    db.session.commit()


def fake_comment(count=200):
    post_count = Post.query.count()
    user_count = User.query.count()
    for i in range(count):
        p = Post.query.offset(randint(0,post_count-1)).first()
        u = User.query.offset(randint(0,user_count-1)).first()
        c = Comment(
            body=fake.text(20),
            post_id=p.id,
            author_id=u.id,
            is_post_comment=True
        )
        db.session.add(c)
    db.session.commit()


def fake_collect(count=100):
    user_count = User.query.count()
    post_count = Post.query.count()
    for i in range(count):
        p = Post.query.offset(randint(0,post_count-1)).first()
        u = User.query.offset(randint(0,user_count-1)).first()
        collect = Collect(
            collector_id=u.id,
            collected_post_id=p.id
        )
        try:
            db.session.add(collect)
            db.session.commit()
        except:
            db.session.rollback()


def fake_personal():
    user_count = User.query.count()
    for i in range(user_count):
        p = Personal(user_id=User.query.filter_by(id=i+1).first().id)
        db.session.add(p)
    db.session.commit()


def fake_category():
    for i in range(10):
        c = Category(category_name=fake.sentence(4))
        db.session.add(c)
    db.session.commit()
