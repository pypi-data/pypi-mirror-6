# -*- coding: utf-8 -*-

from wtforms import TextField, RadioField, IntegerField
from flask_wtf import Form
from wtforms.validators import DataRequired


class GfwlistForm(Form):
    proxy_type = RadioField(u'代理类型', choices=[
        ('HTTP', 'HTTP'),
        ('SOCKS', 'SOCKS'),
    ])
    server = TextField(u'代理服务器', [DataRequired()])
    port = IntegerField(u'端口', [DataRequired()])
