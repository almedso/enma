# -*- coding: utf-8 -*-
"""
    @file
    google login via oauth2 (google calles it openid connect)
"""
from flask import redirect, url_for, session, request, flash, Blueprint
from flask.ext.login import login_user

from enma.extensions import oauth
from enma.database import db

from enma.public.domain import compose_username
from enma.user.models import User
from enma.activity.models import record_authentication, record_user


blueprint = Blueprint('oauth_google', __name__)


google = oauth.remote_app(
    'google',
    app_key = 'GOOGLE',

    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@blueprint.route('/login')
def login():
    return google.authorize(callback=url_for('oauth_google.authorized_login', _external=True))

@blueprint.route('/register')
def register():
    return google.authorize(callback=url_for('oauth_google.authorized_register', _external=True))


@blueprint.route('/chose/<token>')
def chose(token):
    user = User.verify_auth_token(token)
    if user:
        # hand over the the user ref to that is subject to change to the
        # post authentication processing
        # if set it also indicates that it is an chose authentication request
        session['picked_user'] = user.username
        return google.authorize(callback=url_for('oauth_google.authorized', _external=True))
    else:
        flash('This link has been expired - ', 'error')
        return redirect(url_for('public.login'))


@blueprint.route('/authorized_login')
def authorized_login():

    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth2_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    auth_provider = 'google-oauth2'
    nick_name = None 
    username = compose_username(nick_name, me.data['email'], auth_provider)
    user = User.query.filter_by(username=username).first()

    if user:
        login_user(user)
        flash("You are logged in", 'info')
        record_authentication()
        redirect_url = url_for("user.home")
        if not user.email_validated:
            redirect_url = url_for('user.resend_confirmation')
    else:
        flash('User {0} is unknown'.format(username), "warning")
        redirect_url = url_for("public.login")
    return redirect(redirect_url)


@blueprint.route('/authorized_register')
def authorized_register():

    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth2_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    auth_provider = 'google-oauth2'
    nick_name = None 
    username = compose_username(nick_name, me.data['email'], auth_provider)
    user = User.query.filter_by(username=username).first()

    if user:
        flash('Choose another Id - user already registered', "warning")
    else:
        new_user = User.create(username=username,
                        email=me.data['email'] , active=False)
        db.session.commit()
        login_user(new_user)
        record_user('Register', new_user)
        flash("Thank you for registering. Please update your profile.")

    return redirect(url_for("public.login"))


@google.tokengetter
def get_google_oauth_token():
    return session.get('oauth2_token')


