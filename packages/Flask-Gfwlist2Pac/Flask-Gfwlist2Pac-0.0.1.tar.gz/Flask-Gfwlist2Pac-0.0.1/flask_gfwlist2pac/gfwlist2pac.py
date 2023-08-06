# -*- coding: utf-8 -*-

from flask import request, redirect, url_for, Blueprint,\
     request, render_template

import os

from forms import GfwlistForm
from core import generate_pac_for_gfwlist

class Pac(object):
    def __init__(
            self,
            app=None,
            url='/pac',
            backend=None
    ):
        self.url=os.path.normpath(url)
        self.blueprint = Blueprint(
            'pac',
            __name__,
            url_prefix=None if self.url == '/' else self.url,
            template_folder='templates',
            static_folder='static',
        )

        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app

        for (url, func) in self.url_mapper():
            self.blueprint.add_url_rule(url, view_func=func)

        self.app.register_blueprint(self.blueprint)

    def url_mapper(self):
        return (
            ('/', self.index),
            ('/gfwlist', self.gfwlist),
        )

    def index(self):
        form=GfwlistForm(csrf_enabled=False)
        return render_template('index.html', form=form, action=url_for('pac.gfwlist'))

    def gfwlist(self):
        proxy_type=request.args.get('proxy_type')
        server=request.args.get('server')
        port=request.args.get('port')
        return self.generate_pac(proxy_type,server, port)

    def generate_pac(self, proxy_type, server, port):
        if proxy_type == 'HTTP':
            proxy_str = 'PROXY %s:%s' % (server, port)
        elif proxy_type == 'SOCKS':
            proxy_str = 'SOCKS5 %s:%s;SOCKS %s:%s' % (server, port, server, port)

        return generate_pac_for_gfwlist(proxy_str)
