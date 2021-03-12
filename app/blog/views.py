from .forms import PostForm, CommentForm, ReplyForm,OpenForm
from app import db
from flask import render_template, redirect, url_for, request, session, flash
from app.models import Post, User, Comment, Collect, Category, Reply,Permission
from flask_login import current_user, login_required
from flask import current_app
from . import blog
from app.decorators import permission_required,admin_required


@blog.route('/<username>/edit', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def edit(username):
    """
    实现用户发布文章
    :param username: 当前用户名称
    :return: 若是提交表单了则返回主页，否则继续返回编辑文章页面
    """
    form = PostForm()
    form.category.choices = [(cate.category_name, cate.category_name) for cate in Category.query.all()]
    if form.validate_on_submit():
        category_ = Category.query.filter_by(category_name=form.category.data).first()
        post = Post(title=form.title.data,
                    body=request.form.get('body'),
                    category_id=category_.id,
                    is_personal_post=form.is_personal_post.data,
                    is_mute=form.is_mute.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('发布成功')
        return redirect(url_for('main.index'))
    return render_template('blog/new_post.html', form=form)


@blog.route('/<username>/post/<id>', methods=['GET', 'POST'])
def show_signal_post(username, id):
    """
    显示单篇文章
    :param username: 文章作者名称
    :param id: 文章id
    :return: 返回显示单篇文章页面
    """
    post = Post.query.filter_by(id=id).first()
    page = request.args.get('page', 1, type=int)
    form = CommentForm()
    pagination = Comment.query.filter_by(post_id=id, is_post_comment=True).paginate(page,
                                                              per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                              error_out=False
                                                              )
    comments = pagination.items
    categories = Category.query.all()
    comments_r = dict()
    comments_list = list()
    for comment_is in comments:
        re = Reply.query.filter_by(replied_id=comment_is.id).all()
        for r in re:
            re_1 = Reply.query.filter_by(replied_id=r.replier.id).all()
            comments_list.append(re_1)
        comments_r[comment_is] = re+comments_list
        comments_list.clear()
    return render_template('blog/signal_post.html', post=post, comments=comments, form=form, pagination=pagination,
                           endpoint='blog.show_signal_post', Comment=Comment,comment_r=comments_r,categories=categories)


@blog.route('/<username>/self/post/<id>', methods=['GET', 'POST'])
@login_required
def through_self(username, id):
    """
    显示单篇文章
    :param username: 文章作者名称
    :param id: 文章id
    :return: 返回显示单篇文章页面
    """
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(post_id=id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    categories = Category.query.all()
    comments = pagination.items
    comments_r = dict()
    comments_list = list()
    for comment_is in comments:
        re = Reply.query.filter_by(replied_id=comment_is.id).all()
        for r in re:
            re_1 = Reply.query.filter_by(replied_id=r.replier.id).all()
            comments_list.append(re_1)
        comments_r[comment_is] = re + comments_list
        comments_list.clear()
    post = Post.query.filter_by(id=id).first()
    return render_template('blog/show_self_signal_post.html', post=post, comments=comments, pagination=pagination,
                           endpoint='blog.through_self',comment_r=comments_r,categories=categories)


@blog.route('/delete/<id>', methods=['POST', 'GET'])
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    user = User.query.filter_by(id=post.author_id).first()
    if post.author_id == user.id:
        db.session.delete(post)
        db.session.commit()
        flash('删除成功')
    else:
        flash("没有权限删除!")
    return redirect(url_for('blog.show_posts', username=current_user.username))


@blog.route('/collect/posts/<id>', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def collect_post(id):
    inquiry_collected_post = Collect.query.filter_by(collected_post_id=id,collector_id=current_user.id).first()
    post = Post.query.filter_by(id=id).first()
    if current_user:
        if inquiry_collected_post and int(inquiry_collected_post.collected_post_id) == int(id):
            flash('已经收藏了')
        else:
            collect = Collect(
                collector_id=current_user.id,
                collected_post_id=id
            )
            db.session.add(collect)
            db.session.commit()
            flash('收藏成功')
    else:
        flash('没有权限收藏')
    return redirect(url_for('blog.show_signal_post', id=id, username=post.author.id))


@blog.route('/comment/<id>', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.COMMENT)
def comment(id):
    form = CommentForm()
    post = Post.query.filter_by(id=id).first()
    if form.validate_on_submit():
        comment = Comment(
            body=form.text.data,
            post_id=id,
            author_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('评论成功')
    form.text.data = ''
    return redirect(url_for('blog.show_signal_post', username=post.author.id, id=post.id)+'#comment-form')


@blog.route('/collect/show_post/<id>')
@login_required
def show_collect_signal_post(id):
    form = CommentForm()
    collected_post = Post.query.filter_by(id=id).first()
    collector_user = User.query.filter_by(id=Collect.query.filter_by(collected_post_id=id).first().collector_id).first()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(post_id=id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    comments_r = dict()
    comments_list = list()
    for comment_is in comments:
        re = Reply.query.filter_by(replied_id=comment_is.id).all()
        for r in re:
            re_1 = Reply.query.filter_by(replied_id=r.replier.id).all()
            comments_list.append(re_1)
        comments_r[comment_is] = re + comments_list
        comments_list.clear()
    return render_template('blog/show_signal_collected_post.html', comments=comments, pagination=pagination,
                           post=collected_post, form=form, endpoint='blog.show_collect_signal_post',comment_r=comments_r,collector_user=collector_user)


@blog.route('/cancel/collect/post/<id>', methods=['POST', 'GET'])
@login_required
def cancel_collect_post(id):
    collected_post = Collect.query.filter_by(collected_post_id=id).first()
    db.session.delete(collected_post)
    db.session.commit()
    flash('取消成功')
    return redirect(url_for('auth.display_user', username=current_user.username))


@blog.route('/through_self/<post_id>/delete/comment/<comment_id>', methods=['POST', 'GET'])
@login_required
def delete_comment(post_id, comment_id):
    post = Post.query.filter_by(id=post_id).first()
    comment_ = Comment.query.filter_by(id=comment_id).first()
    post_user = User.query.filter_by(id=post.author.id).first()
    comment_user = User.query.filter_by(id=comment_.author_id).first()
    if current_user.id == post_user.id or current_user.id == comment_user.id:
        delete_comment = Comment.query.filter_by(id=comment_id).first()
        db.session.delete(delete_comment)
        db.session.commit()
        flash('删除评论成功')
    return redirect(url_for('blog.through_self', username=current_user.username, id=post_id))


@blog.route('/show_signal_post/<post_id>/delete/comment/<comment_id>', methods=['POST', 'GET'])
@login_required
def delete_comment_signal(post_id, comment_id):
    post = Post.query.filter_by(id=post_id).first()
    comment_ = Comment.query.filter_by(id=comment_id).first()
    post_user = User.query.filter_by(id=post.author.id).first()
    comment_user = User.query.filter_by(id=comment_.author_id).first()
    if current_user.id == post_user.id or current_user.id == comment_user.id:
        delete_comment = Comment.query.filter_by(id=comment_id).first()
        db.session.delete(delete_comment)
        db.session.commit()
        flash('删除评论成功')
    return redirect(url_for('blog.show_signal_post', username=current_user.username, id=post_id))


@blog.route('/<post_id>/reply/to/<responded_id>', methods=['POST', 'GET'])
@login_required
@permission_required(Permission.COMMENT)
def reply(post_id, responded_id):
    form = ReplyForm()
    if form.validate_on_submit():
        post = Post.query.filter_by(id=post_id).first()
        comment = Comment.query.filter_by(id=responded_id).first()
        comment_ = Comment(
            body=form.text.data,
            author_id=current_user.id,
            post_id=post_id,
            is_post_comment=False
        )
        comment_.reply_(comment)
        db.session.add(comment_)
        db.session.commit()

        return redirect(url_for('blog.show_signal_post', username=post.author.username, id=post_id))
    return render_template('blog/reply.html', form=form)


@blog.route('/<category_name>/posts',methods=['POST','GET'])
def display_category_posts(category_name):
    page = request.args.get('page',1,type=int)
    categories = Category.query.all()
    pagination = Post.query.filter_by(category_id=Category.query.filter_by(category_name=category_name).first().id,is_personal_post=False).paginate(page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                                                                                        error_out=False
                                                                                                                        )
    category_posts = pagination.items
    return render_template('blog/category_posts.html',posts=category_posts,pagination=pagination,endpoint='blog.display_category_posts',category_name=category_name,categories=categories)


