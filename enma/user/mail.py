# -*- coding: utf-8 -*-
from flask.ext.mail import Message
from flask import current_app, url_for
from flask.ext.login import current_user
from enma.extensions import mail
from flask.templating import render_template
from threading import Thread
import time
from enma.activity.models import record_user

def send_email(to, subject, template, **kwargs):
    """
    @brief Send any email
    
    All emails are prefixed and will be send from one general account.
    @param to addressee email address
    @param subject the subject of the email
    @param template the base path of the template without extension.
           The .txt and html extension will be automatically added
    @param kwargs that are passed on to render the message
    """
    message = Message(
                current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
#                sender= current_app.config['MAIL_SENDER'],
                recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    #with current_app.app_context():
    mail.send(message)
    #worker = Thread(target=send_async_email, args=[current_app, message])
    #worker.start()


def send_async_email(app, message):
    """
    Send emails asynchronously to have a responsive web application
    """
    with app.app_context():
        mail.send(message)


def request_email_confirmation(user=None):
    """
    @brief Request a confirmation of the email address
    
    By sending this email and urging the user to click the contained
    link the email address gets tested if it is a working/valid one.
    @param user The user object that will be addressed. If not given
           the current user is used. The user must not be anonymous.
    """
    if None == user:
        user = current_user  # current user must not be anonymous
    if not user.email_validated:
        record_user('Request email address confirmation')

        send_email(user.email,'Confirm your mail address',
                   'mail/confirm_email', full_name=user.full_name,
                   link=generate_email_confirm_url(user))


def generate_email_confirm_url(user):
    expiry = time.time() +  3600 * 48  # two days valid
    token = user.generate_auth_token(expiry)
    return url_for('user.confirm_email', token=token, _external=True)


def send_reset_password_link(user):
    """
    @brief Send an email containing a link to reset password
    @param user The user object that requires a new password.
    """
    record_user('Request password reset', acted_on=user)
    send_email(user.email,'Set new password',
                   'mail/reset_password_email', full_name=user.full_name,
                   link=generate_reset_password_url(user))


def generate_reset_password_url(user):
    expiry = time.time() +  300  # 5 minutes valid
    token = user.generate_auth_token(expiry)
    return url_for('user.set_password', token=token, _external=True)