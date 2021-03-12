# 库的引用
from flask_login import login_required, login_user, logout_user, current_user
from flask import current_app, flash, render_template, redirect, request, url_for, session
from .forms import LoginForm, LogonForm, UserForm, SetForm,AvatarForm
from ..models import User
from app import db
from . import auth
from app.models import Post, User, Comment, Collect, Follow, Category, Personal,Permission
from app.emails import send_mail
from sqlalchemy import and_, or_
from app.decorators import admin_required,permission_required
from flask_dropzone import random_filename
from flask import jsonify
import json
from app import csrf
from app.helper import generate_captcha,get_captcha_


@auth.route('/login', methods=['POST', 'GET'])
def login():
    """
    对用户的密码和邮箱进行核对，如果数据库有并且都符合数据库里的数据则登录成功
    :return:登录成功返回主页，不成功继续返回登录姐姐们
    """
    form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first()
    #     if user is None:
    #         flash('用户不存在')
    #         return redirect(url_for('auth.login'))
    #     else:
    #         if user.verify_password_hash(form.password.data) and \
    #                 user.username == form.username.data:
    #             user.ping()
    #             if form.remember_me is True:
    #                 login_user(user, True)
    #             else:
    #                 login_user(user, False)
    #             flash('登录成功')
    #             return redirect(url_for(request.args.get('next') or 'main.index'))
    #         else:
    #             flash('用户名错误或密码错误')
    #             return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)


@csrf.exempt
@auth.route('/ajax_login',methods=['POST'])
def ajax_login():
    form = json.loads(request.get_data(as_text=True))
    user = User.query.filter_by(username=form['username']).first()
    if user is None:
        return jsonify({'msg':'用户不存在'})
    else:
        if user.verify_password_hash(form['password']) and \
                user.username == form['username']:
            if form['captcha'].lower() == form['imag'].lower():
                user.ping()
                if form['re_me'] is True:
                    login_user(user, True)
                else:
                    login_user(user, False)
                return jsonify({'url':url_for('main.index')})
            else:
                return jsonify({'msg':'验证码错误','url':url_for('auth.login')})
        else:
            return jsonify({'msg':'密码错误','url':url_for('auth.login')})


@csrf.exempt
@auth.route('/get_captcha',methods=['GET','POST'])
def get_captcha():
    if request.method == 'GET':
        data = get_captcha_()
        data_ = data.rsplit('.')
        return jsonify({'url':url_for('static',filename='captcha/'+data),'alt':data_[0]})
    else:
        get_data = request.get_data(as_text=True)
        import os

        get_data = get_data.rsplit('/')
        os.remove('C:/Users/m1767/PycharmProjects/HuLog/app/static/captcha/'+get_data[5])
        data = generate_captcha()
        data_ = data.rsplit('.')
        return jsonify({'url':url_for('static',filename='captcha/'+data),'alt':data_[0]})


@auth.route('/logon', methods=['POST', 'GET'])
def logon():
    """
    该视图函数对用户的邮箱和用户名进行检查，如果数据库没有，则通过注册，然后返回到登录界面
    :return:返回注册页面，注册成功后返回的是主页
    """
    form = LogonForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        u1 = User.query.filter_by(username=form.username.data).first()
        if u or u1:
            flash('用户已存在')
            return redirect(url_for('auth.logon'))
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功')
        return redirect(url_for('auth.login'))
    return render_template('auth/logon.html', form=form)


# 用户退出登录的路由
@auth.route('/logout', methods=['POST', 'GET'])
def logout():
    """
    将用户的信息从session的会话中删除掉，实现退出登录
    :return: 返回网站主页
    """
    current_user.out_online()
    logout_user()
    flash('欢迎下次再来!')
    return redirect(url_for('main.index'))


# 用户更改信息的路由
@auth.route('/change_user', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.FOLLOW)
def change_user():
    """
    实现修改个人信息的视图函数
    if里面是将提交表单后得到的数据进行对数据库中储存当前用户记录的修改
    之后将不管是修改过还是没有修改过的数据库里记录的字段给页面显示
    :return: 返回一个修改个人信息的页面
    """
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.username = form.username.data
        user.age = form.age.data
        user.email = form.email.data
        user.sex = form.sex.data
        user.birthday = form.birthday.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('修改成功!')
        return redirect(url_for('main.index'))
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.age.data = current_user.age
    form.sex.data = current_user.sex
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    form.birthday.data = current_user.birthday
    return render_template('auth/formations.html', form=form)


@auth.route('/display_user', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.FOLLOW)
def display_user():
    """
    显示当前用户个人信息的页面
    :return: 返回一个当前用户的个人信息页面
    """
    form = SetForm()
    form.posts.choices = [(p.id, p.title) for p in Post.query.filter_by(author_id=current_user.id).all()]

    if form.validate_on_submit():
        post_ = Post.query.filter_by(id=form.posts.data).first()
        user = User.query.filter_by(id=current_user.id).first()
        post_.is_mute = form.is_mute.data
        post_.is_personal_post = form.is_personal_post.data
        post_.is_show_comment_s = form.is_show_comment_s.data
        user.is_show_fans = form.is_show_fans.data
        user.is_show_followed = form.is_show_followed.data
        personal = Personal(is_personal=form.care_personal_can_see.data,
                            is_show_collect_post=form.is_show_collect_post.data,
                            user_id=current_user.id
                            )
        delete_personal = Personal.query.filter_by(user_id=current_user.id).first()
        posts = Post.query.filter_by(author_id=current_user.id).all()
        db.session.add(user)
        db.session.commit()
        db.session.add(personal)
        db.session.delete(delete_personal)
        db.session.commit()
        for post in posts:
            post.is_show_comment = form.is_show_comment.data
            db.session.add(post)
        db.session.commit()
        db.session.add(post_)
        db.session.commit()
        flash('保存成功')
    form.care_personal_can_see.data = Personal.query.filter_by(user_id=current_user.id).first().is_personal
    form.is_show_comment.data = Post.query.filter_by(
        author_id=current_user.id).first().is_show_comment if Post.query.filter_by(
        author_id=current_user.id).first() else False
    form.is_show_followed.data = current_user.is_show_followed
    form.is_show_fans.data = current_user.is_show_fans
    form.is_show_collect_post.data = Personal.query.filter_by(user_id=current_user.id).first().is_show_collect_post
    if request.method == 'GET':
        if session.get('page'):
            page = session['page']
        else:
            page = request.args.get('page', 1, type=int)
        if session.get('collect_page'):
            collect_page = session['collect_page']
        else:
            collect_page = request.args.get('collect_page', 1, type=int)
        if session.get('followed_page'):
            followed_page = session['followed_page']
        else:
            followed_page = request.args.get('followed_page', default=1, type=int)
        if session.get('follower_page'):
            follower_page = session['follower_page']
        else:
            follower_page = request.args.get('follower_page', 1, type=int)
        if session.get('personal_page'):
            personal_page = session['personal_page']
        else:
            personal_page = request.args.get('personal_page', 1, type=int)
    else:
        page = request.args.get('page', default=1, type=int)
        collect_page = request.args.get('collect_page', 1, type=int)
        followed_page = request.args.get('followed_page', 1, type=int)
        follower_page = request.args.get('follower_page', 1, type=int)
        personal_page = request.args.get('personal_page', 1, type=int)
        session['page'] = page
        session['collect_page'] = collect_page
        session['followed_page'] = followed_page
        session['follower_page'] = follower_page
        session['personal_page'] = personal_page
    followed_pagination = Follow.query.filter_by(follower_id=current_user.id).paginate(followed_page,
                                                                                       per_page=current_app.config[
                                                                                           'FLASKY_FOLLOWERS_PER_PAGE'],
                                                                                       error_out=False)
    follower_pagination = Follow.query.filter_by(followed_id=current_user.id).paginate(follower_page,
                                                                                       per_page=current_app.config[
                                                                                           'FLASKY_FOLLOWERS_PER_PAGE'],
                                                                                       error_out=False)
    pagination = Post.query.filter_by(author_id=current_user.id, is_personal_post=False).paginate(page, per_page=
    current_app.config[
        'FLASKY_POSTS_PER_PAGE'],
                                                                                                  error_out=False
                                                                                                  )
    personal_pagination = Post.query.filter_by(author_id=current_user.id, is_personal_post=True).paginate(personal_page,
                                                                                                          per_page=
                                                                                                          current_app.config[
                                                                                                              'FLASKY_POSTS_PER_PAGE'],
                                                                                                          error_out=False
                                                                                                          )
    collect_pagination = Collect.query.filter_by(collector_id=current_user.id).paginate(
        page=collect_page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    categories = Category.query.all()
    collects = collect_pagination.items
    posts = pagination.items
    followeds = followed_pagination.items
    followers = follower_pagination.items
    personal_posts = personal_pagination.items
    followed_users = list()
    follower_users = list()
    collect_posts = list()
    for f in followeds:
        followed_users.append(User.query.filter_by(id=f.followed_id).first())
    for f in followers:
        follower_users.append(User.query.filter_by(id=f.follower_id).first())
    for c in collects:
        p = Post.query.filter_by(id=c.collected_post_id).first()
        collect_posts.append(p)
    return render_template('auth/user.html', posts=posts, pagination=pagination, endpoint='auth.display_user',
                           collect_pagination=collect_pagination, collect_posts=collect_posts,
                           current_user=current_user, followed_users=followed_users,
                           followed_pagination=followed_pagination, follower_pagination=follower_pagination,
                           follower_users=follower_users, categories=categories, form=form,
                           personal_pagination=personal_pagination, personal_posts=personal_posts)


@auth.route('/display_other/<username>', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.FOLLOW)
def display_other(username):
    """
    查看其它人个人信息的显示
    :param u:参数u是被查看的用户的昵称
    :return:返回的是一个查看其他人信息的页面
    """
    user_ = User.query.filter_by(username=username).first()
    categories = Category.query.all()
    if request.method == 'GET':
        if session.get('page'):
            page = session['page']
        else:
            page = request.args.get('page', 1, type=int)
        if session.get('collect_page'):
            collect_page = session['collect_page']
        else:
            collect_page = request.args.get('collect_page', 1, type=int)
        if session.get('followed_page'):
            followed_page = session['followed_page']
        else:
            followed_page = request.args.get('followed_page', default=1, type=int)
        if session.get('follower_page'):
            follower_page = session['follower_page']
        else:
            follower_page = request.args.get('follower_page', 1, type=int)
    else:
        page = request.args.get('page', default=1, type=int)
        collect_page = request.args.get('collect_page', 1, type=int)
        followed_page = request.args.get('followed_page', 1, type=int)
        session['page'] = page
        session['collect_page'] = collect_page
        session['followed_page'] = followed_page
    followed_pagination = Follow.query.filter_by(follower_id=user_.id).paginate(followed_page,
                                                                                per_page=current_app.config[
                                                                                    'FLASKY_FOLLOWERS_PER_PAGE'],
                                                                                error_out=False)
    follower_pagination = Follow.query.filter_by(followed_id=user_.id).paginate(follower_page,
                                                                                per_page=current_app.config[
                                                                                    'FLASKY_FOLLOWERS_PER_PAGE'],
                                                                                error_out=False)
    pagination = Post.query.filter_by(author_id=user_.id).paginate(page, per_page=current_app.config[
        'FLASKY_POSTS_PER_PAGE'],
                                                                   error_out=False
                                                                   )
    collect_pagination = Collect.query.filter_by(collector_id=user_.id).paginate(
        page=collect_page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    collects = collect_pagination.items
    posts = pagination.items
    followers = follower_pagination.items
    followeds = followed_pagination.items
    followed_users = list()
    follower_users = list()
    collect_posts = list()
    for f in followers:
        follower_users.append(User.query.filter_by(id=f.follower_id).first())
    for f in followeds:
        followed_users.append(User.query.filter_by(id=f.followed_id).first())
    for c in collects:
        p = Post.query.filter_by(id=c.collected_post_id).first()
        collect_posts.append(p)
    return render_template('auth/other.html', user=user_, pagination=pagination, collect_posts=collect_posts,
                           collect_pagination=collect_pagination, posts=posts, endpoint='auth.display_other',
                           current_user_=user_, followed_pagination=followed_pagination, followed_users=followed_users,
                           categories=categories, follower_pagination=follower_pagination,
                           follower_users=follower_users)


@auth.route('/upload/<username>',methods=['POST','GET'])
@login_required
def upload_imag(username):
    import os
    form = AvatarForm()
    if form.validate_on_submit():
        avatar = request.files['avatar']
        if avatar.filename != 'default.ico':
            filename = random_filename(avatar.filename)
        else:
            filename = avatar.filename
        old_filename = current_user.real_avatar
        UPLOAD_FOLDER = 'C:\\Users\\m1767\\PycharmProjects\\HuLog\\app\\static\\self_imag\\'
        ALLOWED_EXTENSIONS = ['png','ico','jpg']
        flag = '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
        if not flag:
            flash('该文件格式不支持!')
            return redirect(url_for('auth.display_user'))
        avatar.save('{}{}'.format(UPLOAD_FOLDER,filename))
        current_user.real_avatar = str(filename)
        db.session.add(current_user)
        db.session.commit()
        flash('更新头像成功')
        if old_filename != 'default.ico':
            os.remove(os.path.join(UPLOAD_FOLDER, old_filename ))
            print('删除成功')
        return redirect(url_for('auth.display_user'))
    return render_template('auth/edit_avatar.html',form=form)