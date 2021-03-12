from wtforms.validators import Required
from wtforms import SubmitField,StringField,TextAreaField,SelectField,BooleanField
from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from app.models import Category


class PostForm(FlaskForm):
    # 文章表单
    title = StringField('标题')
    category = SelectField('文章类别',choices="")
    body = PageDownField('内容')
    is_personal_post = BooleanField('文章是否私密')
    is_mute = BooleanField('是否禁言')
    submit = SubmitField('发布')


class CommentForm(FlaskForm):
    text = PageDownField('内容')
    submit = SubmitField('评论')


class ReplyForm(FlaskForm):
    text = PageDownField('内容')
    submit = SubmitField('评论')


class SearchForm(FlaskForm):
    search_category = SelectField('搜索类型',choices=[('用户','用户'),('文章','文章')])
    search_content = StringField('搜索用户或者文章')
    submit = SubmitField('搜索')


class OpenForm(FlaskForm):
    open_or_close = BooleanField('开启评论或者关闭评论')
    submit = SubmitField('修改')