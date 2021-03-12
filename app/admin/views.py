from flask import render_template,redirect,request,session,flash,url_for
from app.decorators import admin_required,permission_required
from flask_login import current_user,login_required,login_user,logout_user
from . import admin
from app import db
from app.models import Post,Category,Comment,User,Collect,Role,Permission
from .forms import CategoryForm,PermissionForm


@admin.route('delete/post/<id>',methods=['POST','GET'])
@login_required
@admin_required
def admin_delete_post(id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('admin.admin_show_posts'))


@admin.route('/show/posts',methods=['POST','GET'])
@login_required
@admin_required
def admin_show_posts():
    page = request.args.get('page',1,type=int)
    pagination = db.session.query(Post).order_by(Post.timestamp.desc()).paginate(page,per_page=10,error_out=False)
    posts = pagination.items
    return render_template('admin/posts.html',pagination=pagination,posts=posts,endpoint='admin.admin_show_posts')


@admin.route('/show/comments',methods=['POST','GET'])
@login_required
@admin_required
def admin_show_comments():
    page = request.args.get('page',1,type=int)
    pagination = db.session.query(Comment).order_by(Comment.timestamp.desc()).paginate(page,per_page=10,error_out=False)
    comments = pagination.items
    return render_template('admin/comments.html',pagination=pagination,endpoint='admin.admin_show_comments',comments=comments)


@admin.route('delete/comment/<id>',methods=['POST','GET'])
@login_required
@admin_required
def admin_delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    db.session.delete(comment)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('admin.admin_show_comments'))


@admin.route('/show/comment/<id>',methods=['POST','GET'])
@login_required
@admin_required
def show_a_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    return render_template('admin/show_a_comment.html',comment=comment)


@admin.route('/show/categories',methods=['POST','GET'])
@login_required
@permission_required(Permission.COMMENT|Permission.FOLLOW|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS)
def admin_show_categories():
    page = request.args.get('page',1,type=int)
    pagination = db.session.query(Category).paginate(page,per_page=10,error_out=False)
    categories = pagination.items
    return render_template('admin/show_categories.html',pagination=pagination,categories=categories,endpoint='admin.admin_show_categories')


@admin.route('delete/category/<id>',methods=['POST','GET'])
@login_required
@permission_required(Permission.COMMENT|Permission.FOLLOW|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS)
def admin_delete_category(id):
    category = Category.query.filter_by(id=id).first()
    posts = Post.query.filter_by(category_id=id).all()
    for post in posts:
        post.category_id = 10
        db.session.add(post)
    db.session.commit()
    db.session.delete(category)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('admin.admin_show_categories'))


@admin.route('add/categor',methods=['POST','GET'])
@login_required
@permission_required(Permission.COMMENT|Permission.FOLLOW|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS)
def admin_add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        c = Category(
            category_name=form.name.data
        )
        db.session.add(c)
        db.session.commit()
        flash('添加成功')
        return redirect(url_for('admin.admin_show_categories'))
    return render_template('admin/admin_add_category.html',form=form)


@admin.route('/show/users',methods=['POST','GET'])
@login_required
@admin_required
def admin_show_users():
    page = request.args.get('page',1,type=int)
    pagination = db.session.query(User).paginate(page,per_page=10,error_out=False)
    users = pagination.items
    return render_template('admin/admin_show_users.html',pagination=pagination,users=users,endpoint='admin.admin_show_users')


@admin.route('/modify/user/<id>',methods=['POST','GET'])
@login_required
@admin_required
def admin_modify_permission(id):
    form = PermissionForm()
    form.permission.choices = [(r.id,r.name) for r in Role.query.filter_by().all()]
    if form.validate_on_submit():
        user = User.query.filter_by(id=id).first()
        user.role_id = form.permission.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.admin_show_users'))
    return render_template('admin/admin_permission.html',form=form)


@admin.route('/delete/user/<id>',methods=['POST','GET'])
@login_required
@admin_required
def admin_delete_user(id):
    user = User.query.filter_by(id=id).first()
    posts = Post.query.filter_by(author_id=id).all()
    comments = Comment.query.filter_by(author_id=id).all()
    db.session.delete(user)
    for comment in comments:
        db.session.delete(comment)
    for post in posts:
        db.session.delete(post)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('admin.admin_show_users'))