from wtforms import SubmitField,SelectField,StringField
from flask_wtf import FlaskForm


class SearchForm(FlaskForm):
    search_category = SelectField('搜索类型',choices=[('用户','用户'),('文章','文章')])
    search_content = StringField('搜索用户或者文章')
    submit = SubmitField('搜索')