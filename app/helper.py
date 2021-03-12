from PIL import Image, ImageDraw, ImageFont
from random import randint
from flask import url_for
import os


def get_random_color():
    return randint(120, 200), randint(120, 200), randint(120, 200)


def get_random_code():
    codes = [[chr(i) for i in range(48, 58)], [chr(i) for i in range(65, 91)], [chr(i) for i in range(97, 123)]]
    codes = codes[randint(0, 2)]
    return codes[randint(0, len(codes) - 1)]


def generate_captcha(width=140, height=60, length=4):
    # 生成验证码
    # 创建对象
    img = Image.new("RGB", (width, height), (250, 250, 250))
    # 生成画布
    draw = ImageDraw.Draw(img)
    # 指定画布中字体
    font = ImageFont.truetype("C:\\Users\\m1767\\PycharmProjects\\HuLog\\app\\static\\font\\FZZJ-LongYTJW.TTF", size=36)
    # 验证码文本
    text = ""
    for i in range(length):
        # 获取随机码
        c = get_random_code()
        text += c
        rand_len = randint(-5, 5)
        draw.text((width * 0.2 * (i + 1) + rand_len, height * 0.2 + rand_len), c, font=font, fill=get_random_color())
    # 加入干扰线
    for i in range(3):
        x1 = randint(0, width)
        y1 = randint(0, height)
        x2 = randint(0, width)
        y2 = randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_random_color())
    # 加入干扰点
    for i in range(16):
        draw.point((randint(0, width), randint(0, height)), fill=get_random_color())
    # 保存图片
    img.save("C:\\Users\\m1767\\PycharmProjects\\HuLog\\app\\static\\captcha\\" + text + ".jpg")
    return text + ".jpg"


def get_captcha_list():
    return os.listdir("C:\\Users\\m1767\\PycharmProjects\HuLog\\app\\static\\captcha")


def get_captcha_():
    return get_captcha_list()[randint(0,1000)]


if __name__ == "__main__":
    print(get_captcha_())
