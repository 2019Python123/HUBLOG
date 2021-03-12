from . import admin
from app.models import User,Follow,Comment


@admin.add_app_template_global
def identification(user):
    if user.role_id == 2:
        return '普通用户 F_speak'
    elif user.role_id == 3:
        return '普通用户 F_write'
    elif user.role_id == 4:
        return '普通用户 F_follow'
    elif user.role_id == 1:
        return '普通用户'
    elif user.role_id == 5:
        return '管理员助理'
    elif user.role_id == 6:
        return '管理员'


@admin.add_app_template_global
def real_avatar(user):
    return 'self_imag/'+str(User.query.filter_by(id=user.id).first().real_avatar)


@admin.add_app_template_global
def follower_number(user):
    """
    粉丝数量
    :param user:查询的用户对象
    :return: 对象的粉丝数量
    """
    return Follow.query.filter_by(followed=user).count()


@admin.add_app_template_global
def followed_number(user):
    """
    用户关注的人数量
    :param user:用户对象
    :return: 返回关注的人数值
    """
    return Follow.query.filter_by(follower=user).count()


@admin.add_app_template_global
def comment_number(user):
    """

    :param user:
    :return:
    """
    return Comment.query.filter_by(author_id=user.id).count()