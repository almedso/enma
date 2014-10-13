# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
import datetime
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)
from flask.ext.login import login_user, login_required, logout_user

from enma.extensions import login_manager, oid
from enma.user.models import User, AnonymousUser
from enma.public.forms import LoginUserPasswordForm, LoginOpenIdForm, \
    RegisterUserPasswordForm, RequestPasswordChangeForm
from enma.utils import flash_errors
from enma.database import db

from enma.public.domain import get_first_last_name, compose_username
from enma.activity.models import record_authentication, record_user
from enma.user.mail import send_reset_password_link

from .version import get_version

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
    record_authentication('Logout')
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
        session.pop('action', None)

    openid_provider = 'local'
    if 'openid_provider' in session:
        openid_provider = session['openid_provider']

    username = compose_username(resp.nickname, resp.email, openid_provider)
    if not username:
        flash('Invalid credentials. Please try again.', category="warning")
        return redirect(url_for('public.login'))

    user = User.query.filter_by(username=username).first()

    if action == 'login':
        if user is None:
            # user unknown
            flash('Invalid login. Please try again.', "warning")
            return redirect(url_for('public.login'))
        if not user.active:
            flash('Your account is not activated - ask your administrator',
                  'warning')
            return redirect(url_for('public.login'))

    if action == 'register':
        # either registration or profile change
        if user:
            flash('Choose another Id - user already registered', "warning")
            return redirect(url_for('public.login'))
        first_name, last_name = get_first_last_name(resp.fullname)
        user = User(username=username, email=resp.email,
                    first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()

    # bind the user to the session
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
    login_user(user, remember=remember_me)

    if action == 'login':
        record_authentication()
        flash("You are logged in.", "info")
        redirect_url = url_for("user.home")
        if not user.email_validated:
            redirect_url = url_for('user.resend_confirmation')

    if action == 'register':
        record_user('Register', user)
        flash("Thank you for registering. Please update your profile.", "info")
        redirect_url = url_for("user.profile")
    return redirect(redirect_url)


@blueprint.route('/login/',  methods=['GET', 'POST'])
@oid.loginhandler
def login():
    form_openid = LoginOpenIdForm(request.form, prefix="oid")
    form_userpassword = LoginUserPasswordForm(request.form, prefix="up")
    if request.method == 'POST':
        session['remember_me'] = form_userpassword.remember_me.data
        if len(form_openid.openid.data) > 0 or form_openid.go.data:
            session['openid_provider'] = form_openid.openid.data
            session['action'] = 'login'
            if form_openid.validate_on_submit():
                return oid.try_login(form_openid.openid.data,
                                     ask_for_optional=['email', 'nickname'])
            else:
                flash_errors(form_openid)
        if form_userpassword.login.data:
            if form_userpassword.validate_on_submit():
                if not form_userpassword.user.active:
                    flash('Your account is not activated '
                          '- ask your administrator', 'warning')
                    return redirect(url_for('public.login'))
                login_user(form_userpassword.user,
                           remember=form_userpassword.remember_me.data)
                flash("You are logged in", 'info')
                record_authentication()
                redirect_url = request.args.get("next") or url_for("user.home")
                if not form_userpassword.user.email_validated:
                    redirect_url = url_for('user.resend_confirmation')
                return redirect(redirect_url)
            else:
                flash_errors(form_userpassword)

    return render_template('public/login.html',
                           form_up=form_userpassword,
                           form_oid=form_openid)


@blueprint.route("/register/", methods=['GET', 'POST'])
@oid.loginhandler
def register():
    form_openid = LoginOpenIdForm(request.form, prefix="oid")
    form_userpassword = RegisterUserPasswordForm(request.form, prefix="up")
    if request.method == 'POST':
        if len(form_openid.openid.data) > 0 or form_openid.go.data:
            session['openid_provider'] = form_openid.openid.data
            session['action'] = 'register'
            if form_openid.validate_on_submit():
                return oid.try_login(form_openid.openid.data,
                                     ask_for_optional=['nickname',
                                                       'email', 'fullname'])
            else:
                flash_errors(form_openid)
        if form_userpassword.register.data:
            if form_userpassword.validate_on_submit():
                username = compose_username(form_userpassword.username.data,
                                            None, 'local')
                new_user = User.create(username=username,
                                password=form_userpassword.password.data,
                                email="test@dummy.org" , active=False)
                login_user(new_user)
                record_user('Register', new_user)

                flash("Thank you for registering. Please update your profile.")
                return redirect(url_for("user.profile"))
            else:
                flash_errors(form_userpassword)

    return render_template('public/register.html',
                           form_up=form_userpassword,
                           form_oid=form_openid)


@blueprint.route('/forgotten/',  methods=['GET', 'POST'])
def forgotten_password():
    form = RequestPasswordChangeForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            send_reset_password_link(form.user)
            flash("We have sent you an email containing"
                  " a link to reset your password", 'info')
            return redirect(url_for('public.home'))
        else:
            flash_errors(form)
    return render_template('public/forgotten_password.html', form=form)


@blueprint.route("/help/")
def help():
    return render_template("public/help.html")


@blueprint.route("/about/")
def about():
    return render_template("public/about.html", 
                           versions=get_version(['Flask', 'Jinja2', 'WTForms']))


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