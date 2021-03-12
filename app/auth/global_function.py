from . import auth
from app.models import User, Follow, Category, Post, Personal
from flask_login import current_user
from app import moment
from .forms import SearchForm


@auth.add_app_template_global
def is_follow(self, user):
    """
    判断自己是否关注过ta
    :param self: 自己
    :param user: 其它用户对象
    :return: 返回自己是否已经关注过ta
    """
    return User.following(self, user)


@auth.add_app_template_global
def self_followed_time(user):
    """
    关注的每个人的关注时间
    :param user:当前用户
    :return:返回自己关注每个人的关注时间
    """
    return Follow.query.filter_by(follower_id=current_user.id,
                                  followed_id=user.id).first().timestamp


@auth.add_app_template_global
def self_follower_time(user):
    """
    每个人粉丝关注自己的时间
    :param user:当前用户
    :return:返回每个粉丝关注TA的时间
    """
    return Follow.query.filter_by(followed_id=current_user.id,
                                  follower_id=user.id).first().timestamp


@auth.add_app_template_global
def other_followed_time(user):
    """
    查看别人信息页面时，别人关注每个人人的关注时间
    :param user: 其它用户对象
    :return: 关注时间
    """
    return Follow.query.filter_by(follower_id=user.id).first().timestamp


@auth.add_app_template_global
def other_follower_time(user):
    """
    查看别人信息页面时，别人每个粉丝的关注TA的时间
    :param user: 其它用户对象
    :return: 关注时间
    """
    return Follow.query.filter_by(followed_id=user.id).first().timestamp


@auth.add_app_template_global
def judge_category(post_id):
    """
    判断文章对象的文章类型
    :param post_id: 文章在数据库里id
    :return: 返回文章类型名称
    """
    post = Post.query.filter_by(id=post_id).first()
    category = Category.query.filter_by(id=post.category_id).first()
    return category.category_name


@auth.add_app_template_global
def followed_number(user):
    """
    用户关注的人数量
    :param user:用户对象
    :return: 返回关注的人数值
    """
    return Follow.query.filter_by(follower=user).count()


@auth.add_app_template_global
def is_personal(user):
    """
    判断用户是否显示自己的文章
    :param user:
    :return:
    """
    return bool(Personal.query.filter_by(user_id=user.id).first().is_personal)


@auth.add_app_template_global
def is_show_collect_post(user):
    """
    判断用户是否显示自己收藏的文章
    :param user: 用户对象
    :return: 返回bool值，用户是否显示自己的收藏文章
    """
    return bool(Personal.query.filter_by(user_id=user.id).first().is_show_collect_post)


@auth.add_app_template_global
def is_follower(user_1, user_2):
    """
    判断自己是不是已经关注别人
    :return:
    """
    if Follow.query.filter_by(follower=user_1, followed=user_2).first():
        return True
    return False


@auth.add_app_template_global
def printf(var):
    """
    打印变量在页面
    :param var: 任意变量
    :return: 返回变量
    """
    return var


@auth.add_app_template_global
def follower_number(user):
    """
    粉丝数量
    :param user:查询的用户对象
    :return: 对象的粉丝数量
    """
    return Follow.query.filter_by(followed=user).count()


@auth.add_app_template_global
def search_form():
    return SearchForm()


@auth.add_app_template_global
def is_show_comment(post):
    if Post.query.filter_by(id=post.id).first().is_show_comment is True:
        return True
    return False


@auth.add_app_template_global
def is_mute(post):
    if post.is_mute:
        return True
    return False


@auth.add_app_template_global
def is_closely(user):
    return True if Follow.query.filter_by(follower_id=user.id,
                                          followed_id=current_user.id).first() or Follow.query.filter_by(
        follower_id=current_user.id, followed_id=user.id).first() else False


@auth.add_app_template_global
def is_show_fans(user):
    return bool(User.query.filter_by(id=user.id).first().is_show_fans)


@auth.add_app_template_global
def is_show_followed(user):
    return bool(User.query.filter_by(id=user.id).first().is_show_followed)


@auth.add_app_template_global
def real_avatar(user):
    return 'self_imag/'+str(User.query.filter_by(id=user.id).first().real_avatar)


@auth.add_app_template_global
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
