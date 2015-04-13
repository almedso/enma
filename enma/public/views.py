# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
import datetime
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session, current_app)
from flask.ext.login import login_user, login_required, logout_user

from enma.extensions import login_manager
from enma.user.models import User, AnonymousUser
from enma.public.forms import LoginUserPasswordForm, \
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


def get_oauth2_providers(flag='login'):
    """ Dynamically create and return the list of OAUTH2 providers

    The content is dependent upon the respect Client ID = Application ID
    exists. (i.e. this is the id under which this application is known to
    the authentication provider.

    Returns:
        List containing dictionary of OAUTH2 providers. A provider is 
        has as key the callback URL and as value the httml sniplet
        identifying the provider
    """
    providers = []
    if current_app.config.get('GOOGLE_CONSUMER_KEY'):
        providers.append({'url_for': 'oauth_google.' + flag,
                     'name': '<i class="fa fa-google-plus"></i> Google'})
    return providers


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


@blueprint.route('/login/',  methods=['GET', 'POST'])
def login():
    form = LoginUserPasswordForm(request.form, prefix="up")
    if request.method == 'POST':
        session['remember_me'] = form.remember_me.data
        if form.login.data:
            if form.validate_on_submit():
                if not form.user.active:
                    flash('Your account is not activated '
                          '- ask your administrator', 'warning')
                    return redirect(url_for('public.login'))
                login_user(form.user,
                           remember=form.remember_me.data)
                flash("You are logged in", 'info')
                record_authentication()
                redirect_url = request.args.get("next") or url_for("user.home")
                if not form.user.email_validated:
                    redirect_url = url_for('user.resend_confirmation')
                return redirect(redirect_url)
            else:
                flash_errors(form)

    return render_template('public/login.html', form_up=form,
                           oauth2_providers=get_oauth2_providers())


@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegisterUserPasswordForm(request.form, prefix="up")
    if request.method == 'POST':
        if form.register.data:
            if form.validate_on_submit():
                username = compose_username(form.username.data,
                                            None, 'local')
                new_user = User.create(username=username,
                                password=form.password.data,
                                email="test@dummy.org" , active=False)
                login_user(new_user)
                record_user('Register', new_user)

                flash("Thank you for registering. Please update your profile.")
                return redirect(url_for("user.profile"))
            else:
                flash_errors(form)

    return render_template('public/register.html', form_up=form,
                           oauth2_providers=get_oauth2_providers('register'))


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