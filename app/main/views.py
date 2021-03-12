from flask import current_app, render_template, request, redirect, flash, url_for,session
from flask_login import current_user
from . import main
from flask_login import login_required
from app.models import User, Post, Category, Follow,Personal,Permission
from .forms import SearchForm
from sqlalchemy import or_,and_
from app import db,csrf
from app.decorators import permission_required,admin_required
import json


@main.route('/', methods=['POST', 'GET'])
def index():
    """
    显示主页
    :return: 返回主页
    """
    categories = Category.query.all()
    page = request.args.get('page', 1, type=int)
    post_is_personal_users = list()
    if current_user.is_authenticated:
        follows_1 = Follow.query.filter_by(follower_id=current_user.id).all()
        follows_2 = Follow.query.filter_by(followed_id=current_user.id).all()
        follows = follows_1 + follows_2
        followed_or_follower_list = list()
        for f in follows:
            followed_or_follower_list.append(Personal.user_id!=f.follower_id)
            followed_or_follower_list.append(Personal.user_id!=f.followed_id)
        followed_or_follower_list.append(Personal.is_personal==1)
        personals = Personal.query.filter(and_(*followed_or_follower_list)).all()
        for p in personals:
            post_is_personal_users.append(Post.author_id != User.query.filter_by(id=p.user_id).first().id)
    else:
        personals = Personal.query.filter_by(is_personal=1).all()
        for p in personals:
            post_is_personal_users.append(Post.author_id != User.query.filter_by(id=p.user_id).first().id)
    post_is_personal_users.append(Post.is_mute!=True)
    pagination = db.session.query(Post).filter(*post_is_personal_users).order_by(Post.timestamp.desc()).paginate(page,
                                                                     per_page=current_app.config[
                                                                         'FLASKY_POSTS_PER_PAGE'],
                                                                     error_out=False)
    posts = pagination.items
    return render_template('main/index.html', posts=posts, pagination=pagination, categories=categories,endpoint='main.index')


@main.route('/follow/other/<username>/<flag>/<from_>', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.FOLLOW)
def follow_other(username,flag,from_):
    followed_user = User.query.filter_by(username=username).first()
    User.follow(current_user, followed_user)
    flash('已经关注啦！')
    if flag == 'from_other':
        return redirect(url_for('auth.display_other', username=from_))
    elif flag == 'from_self':
        return redirect(url_for('auth.display_user'))


@main.route('/follow/self', methods=['POST', 'GET'])
@login_required
def follow_self():
    followed_user = User.query.filter_by(username=current_user.username).first()
    User.follow(current_user, followed_user)
    flash('已经关注啦！')
    return redirect(url_for('auth.display_user', username=current_user.username))


@main.route('/unfollow/self', methods=['POST', 'GET'])
@login_required
def un_follow_self():
    followed_user = User.query.filter_by(username=current_user.username).first()
    User.un_follow(current_user, followed_user)
    flash('已经取消关注啦！')
    return redirect(url_for('auth.display_user', username=current_user.username))


@main.route('/unfollow/other/<username>/<flag>/<from_>', methods=['POST', 'GET'])
@login_required
def un_follow_other(username,flag,from_):
    followed_user = User.query.filter_by(username=username).first()
    current_user.un_follow(followed_user)
    flash('已经取消关注啦！')
    if flag == 'from_other':
        return redirect(url_for('auth.display_other', username=from_))
    else:
        return redirect(url_for('auth.display_user'))


@main.route('/search', methods=['POST', 'GET'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        content = form.search_content.data
        search_category = form.search_category.data
        if search_category == '用户':
            return redirect(url_for('main.search_users',content=content))
        if search_category == '文章':
            return redirect(url_for('main.search_posts',content=content))


@main.route('/search/posts', methods=['POST', 'GET'])
def search_posts():
    if request.args.get('content'):
        content = request.args.get('content')
        session['content'] = content
    else:
        content = session['content']
    page = request.args.get('page',1,type=int)
    post_is_personal_users = list()
    personals = Personal.query.filter_by(is_personal=1).all()
    for p in personals:
        post_is_personal_users.append(Post.author_id!=User.query.filter_by(id=p.user_id).first().id)
    pagination = db.session.query(Post).filter(and_(or_(Post.title.like('%'+str(content)+'%'),Post.body.like('%'+str(content)+'%')),*post_is_personal_users)).order_by(Post.timestamp.desc()).paginate(page,
                                                                                                     per_page=10,
                                                                                                          error_out=False
                                                                                                     )
    posts = pagination.items
    return render_template("main/search_posts.html", posts=posts,pagination=pagination,endpoint='main.search_posts')


@main.route('/search/users', methods=['POST', 'GET'])
def search_users():
    if request.args.get('content'):
        content = request.args.get('content')
        session['content'] = content
    else:
        content = session['content']
    page = request.args.get('page',1,type=int)
    pagination = User.query.filter(User.username.like('%'+str(content)+'%')).paginate(page,
                                                                            per_page=10,
                                                                           error_out=False
                                                                           )
    users = pagination.items
    return render_template("main/search_users.html", users=users,pagination=pagination,endpoint='main.search_users')


@csrf.exempt
@main.route('/search_tips',methods=['POST','GET'])
def search_tips():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    if data['tar'] == '文章':
        posts = Post.query.filter(Post.title.like('%'+data['data']+'%')).all()
        print(render_template('main/tips.html',tar=posts,name='post'))
        return render_template('main/tips.html',tar=posts,name='post')
    if data['tar'] == '用户':
        users = User.query.filter(User.username.like('%'+data['data']+'%')).all()
        print(render_template('main/tips.html',tar=users,name='user'))
        return render_template('main/tips.html',tar=users,name='user')
