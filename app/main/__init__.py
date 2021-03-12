from flask import Blueprint

# 生成主蓝图
main = Blueprint('main',__name__)

# 实现蓝图生效
from . import views,forms,global_function