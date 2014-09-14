from flask_wtf import Form
from wtforms import TextField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, URL


from enma.user.models import User


## Open Id provider
OPENID_PROVIDERS = [
    {'name': 'Google', 'text': '<i class="fa fa-google-plus"></i> Google',
      'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Facebook', 'text': '<i class="fa fa-facebook"></i> Facebook',
      'url': 'facebook-openid.appspot.com/<username>'},
    {'name': 'Yahoo', 'text': '<i class="fa fa-yahoo"></i> Yahoo',
      'url': 'https://me.yahoo.com'},
    {'name': 'Flickr', 'text': '<i class="fa fa-flickr"></i> Flickr',
      'url': 'http://www.flickr.com/<username>'},
    ]

class LoginOpenIdForm(Form):

    providers = OPENID_PROVIDERS
    openid = TextField('OpenId Provider', validators=[URL])
    go = SubmitField('Go', id='oid-go')


class LoginUserPasswordForm(Form):

    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
    login = SubmitField('Login')


    def __init__(self, *args, **kwargs):
        super(LoginUserPasswordForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(LoginUserPasswordForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append('Unknown username')
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        if not self.user.active:
            self.username.errors.append('User not activated')
            return False
        return True