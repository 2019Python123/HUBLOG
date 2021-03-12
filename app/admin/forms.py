from wtforms import SubmitField,StringField,SelectField
from flask_wtf import FlaskForm


class CategoryForm(FlaskForm):
    name = StringField('文章类型名')
    submit = SubmitField('提交')


class PermissionForm(FlaskForm):
    permission = SelectField('权限',choices=[])
    submit = SubmitField('修改')
