# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
import datetime
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)
from flask.ext.login import login_user, login_required, logout_user

from enma.extensions import login_manager, oid
from enma.user.models import User, AnonymousUser
from enma.public.forms import LoginUserPasswordForm, LoginOpenIdForm
from enma.user.forms import RegisterForm
from enma.utils import flash_errors
from enma.database import db

blueprint = Blueprint('public', __name__, static_folder="../static")

login_manager.anonymous_user = AnonymousUser
# login_manager.login_view = 'login'  # will be redirected to login


@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    return render_template("public/home.html")


@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@oid.errorhandler
def on_error(message):
    flash(message, category="warning")


@oid.after_login
def after_login(resp):
    action = 'login'  # selector of what kind or processing is required
    if 'action' in session:
        action = session['action']
    if resp.email is None:
        flash('Invalid credentials. Please try again.', category="warning")
        return redirect(url_for('public.login'))
    user = User.query.filter_by(email=resp.email).first()
    openid_provider = 'local'
    if 'openid_provider' in session:
        openid_provider = session['openid_provider']

    if action == 'login':
        flash('DEBUG: This is login')
        if user is None or user.openid_provider != openid_provider:
            # user unknown
            flash('Invalid login. Please try again.', category="warning")
            return redirect(url_for('public.login'))

    if action == 'register':
        flash('DEBUG: This is register')
        # either registration or profile change
        if user is None and False:
            nickname = resp.nickname
            if nickname is None or nickname == "":
                nickname = resp.email.split('@')[0]
            user = User(nickname = nickname, email = resp.email)
            db.session.add(user)
            db.session.commit()

    # bind the user to the session
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    flash("You are logged in.", 'success')
    login_user(user, remember=remember_me)
    return redirect(url_for("user.home"))


@blueprint.route('/login/',  methods=['GET', 'POST'])
@oid.loginhandler
def login():
    form_openid = LoginOpenIdForm(request.form, prefix="oid")
    form_userpassword = LoginUserPasswordForm(request.form, prefix="up")
    if request.method == 'POST':
        session['remember_me'] = form_userpassword.remember_me.data
        if len(form_openid.openid.data) > 0 or form_openid.go.data:
            session['openid_provider'] = form_openid.openid.data
            if form_openid.validate_on_submit():
                return oid.try_login(form_openid.openid.data,
                                     ask_for=['email'])
            else:
                flash_errors(form_openid)
        if form_userpassword.login.data:
            if form_userpassword.validate_on_submit():
                login_user(form_userpassword.user,
                           remember=form_userpassword.remember_me.data)
                flash("You are logged in.", 'success')
                redirect_url = request.args.get("next") or url_for("user.home")
                return redirect(redirect_url)
            else:
                flash_errors(form_userpassword)

    return render_template('public/login.html',
                           form_up=form_userpassword,
                           form_oid=form_openid)


@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    form_openid = LoginOpenIdForm(request.form, prefix="oid")
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        new_user = User.create(username=form.username.data,
                        email=form.email.data,
                        password=form.password.data,
                        active=True)
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route("/help/")
def help():
    return render_template("public/help.html")


@blueprint.route("/about/")
def about():
    return render_template("public/about.html")


@blueprint.route("/contact/")
def contact():
    return render_template("public/contact.html")


@blueprint.route("/legal/")
def legal():
    return render_template("public/legal.html")


@blueprint.route("/privacy/")
def privacy():

    return render_template("public/privacy.html")

@blueprint.route("/terms/")
def terms():
    return render_template("public/terms.html")