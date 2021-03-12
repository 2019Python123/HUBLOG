# 引用库
from flask import Blueprint

# 生成认证蓝图
auth = Blueprint('auth',__name__)

# 使蓝图对一下俩个模块生效
from . import views,forms,global_function