from wtforms.validators import ValidationError
from wtforms import TextAreaField,PasswordField,SubmitField,StringField,BooleanField,DateField,DateTimeField,SelectField,RadioField,FileField
from flask_wtf import FlaskForm
from wtforms.validators import Required,DataRequired,Regexp,EqualTo,Email,Length


class LoginForm(FlaskForm):
    """
    登录表单
    """
    email = StringField('邮箱',validators=[Required(),Email()])
    username = StringField('昵称',validators=[Required(),Length(2,32)])
    password = PasswordField('密码',validators=[Required()])
    remember_me = BooleanField("记住")
    submit = SubmitField('登录')


class LogonForm(FlaskForm):
    """
    注册表单
    """
    email = StringField('邮箱',validators=[Required(u'邮箱不能为空'),Length(5,60),Email()])
    username = StringField('昵称',validators=[Required(u'昵称不能为空'),Length(2,32)])
    password = PasswordField('密码',validators=[Required(u'密码不能为空'),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                   '密码只能是大小写字母和数字')])
    re_password = PasswordField('再次输入密码',validators=[Required(u'输入密码不能为空'),EqualTo('password','与上面密码不匹配')])
    submit = SubmitField('注册')


class UserForm(FlaskForm):
    """
        用户信息表单
    """
    email = StringField('邮箱', validators=[Required(u'邮箱不能为空'), Length(12, 60), Email()])
    username = StringField('昵称', validators=[Required(u'昵称不能为空'), Length(4, 32)])
    sex = SelectField('性别',choices=[('男','男'),('女','女'),('保密','保密')])
    age = StringField('年龄')
    location = StringField('所在地')
    birthday = DateField('出生年月',format='%Y/%m/%d')
    about_me = TextAreaField('个性签名')
    submit = SubmitField('修改')


class SetForm(FlaskForm):
    is_show_comment = BooleanField("文章是否显示评论？")
    is_show_fans = BooleanField("是否显示粉丝列表？")
    is_show_followed = BooleanField("是否显示关注列表？")
    care_personal_can_see = BooleanField("发表文章是否只能自己关注和关注自己的人看？")
    is_show_collect_post = BooleanField("是否对外显示自己收藏的文章？")
    posts = SelectField("文章")
    is_mute = BooleanField('评论功能?')
    is_personal_post = BooleanField('将文章设置为私密文章?')
    is_show_comment_s = BooleanField("评论显示?")
    submit = SubmitField('保存设置')


class SearchForm(FlaskForm):
    search_category = SelectField('搜索类型',choices=[('用户','用户'),('文章','文章')])
    search_content = StringField('搜索用户或者文章')
    submit = SubmitField('搜索')


class AvatarForm(FlaskForm):
    avatar = FileField('头像')
    submit = SubmitField('更新头像')


