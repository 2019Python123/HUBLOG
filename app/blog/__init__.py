from flask import Blueprint

# 生成博客蓝图
blog = Blueprint('blog',__name__)

# 蓝图对一下模块生效
from . import forms,views,error,global_function