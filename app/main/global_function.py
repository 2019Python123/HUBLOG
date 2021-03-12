from . import main
from app.models import User, Category, Personal, Post
from .forms import SearchForm


@main.add_app_template_global
def inquire_category_name(category_name):
    return Category.query.filter_by(category_name=category_name).first().category_name


@main.add_app_template_global
def query_post_permissions(user):
    return Personal.query.filter_by(user_id=user.id).first().is_personal


@main.add_app_template_global
def search_form():
    return SearchForm()


@main.add_app_template_global
def is_show_comment(post):
    if Post.query.filter_by(id=post.id).first().is_show_comment is True:
        return True
    return False


@main.add_app_template_global
def is_mute(post):
    if post.is_mute:
        return True
    return False


@main.add_app_template_global
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
