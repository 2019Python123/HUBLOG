from . import blog
from app.models import User,Post,Collect
from flask_login import current_user
from .forms import SearchForm


@blog.add_app_template_global
def is_list(var,type_):
    return isinstance(var,type_)


@blog.app_context_processor
def list_context():
    return dict(list=list)


@blog.add_app_template_global
def is_collect(post_id):
    if current_user.is_anonymous:
        return True
    return Collect.query.filter_by(collected_post_id=post_id,collector_id=current_user.id).first()


@blog.add_app_template_global
def is_personal_post(post_id):
    if current_user.is_administrator:
        return False
    return Post.query.filter_by(id=post_id,author_id=current_user.id).first()


@blog.add_app_template_global
def search_form():
    return SearchForm()


@blog.add_app_template_global
def is_show_comment(post):
    if Post.query.filter_by(id=post.id).first().is_show_comment is True:
        return True
    return False


@blog.add_app_template_global
def is_mute(post):
    if post.is_mute:
        return True
    return False


@blog.add_app_template_global
def real_avatar(user):
    return 'self_imag/'+str(User.query.filter_by(id=user.id).first().real_avatar)


@blog.add_app_template_global
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