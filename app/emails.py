from flask_mail import Message
from . import mail
from . import create_app
from threading import Thread
from flask import render_template


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    msg = Message(create_app().config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=create_app().config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    tr = Thread(target=send_async_email, args=[create_app(), msg])
    tr.start()
    return tr
