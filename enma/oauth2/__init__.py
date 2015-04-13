# -*- coding: utf-8 -*-
import google


def register_oauth_blueprints(app):
    if app.config.get('GOOGLE_CONSUMER_KEY'):
        app.register_blueprint(google.blueprint,
                               url_prefix='/oauth2/google')

