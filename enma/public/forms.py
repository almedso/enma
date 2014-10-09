from flask_wtf import Form
from wtforms import TextField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, URL, Length, EqualTo


from enma.user.models import User
from enma.public.domain import compose_username


class ReadonlyTextField(TextField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyTextField, self).__call__(*args, **kwargs)


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
        username = compose_username(self.username.data, None, 'local')
        self.user = User.query.filter_by(username=username).first()
        if not self.user:
            self.username.errors.append('Unknown username')
            return False

        if not self.user.active:
            self.username.errors.append('User not activated')
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        return True


class RegisterUserPasswordForm(Form):

    username = TextField('Username',
                    validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Password',
                                validators=[Optional(), Length(min=6, max=40)])
    confirm = PasswordField('Verify password',
                [DataRequired(), EqualTo('password',
                message='Passwords must match')])
    register = SubmitField('Create Account', id='register')

    def __init__(self, *args, **kwargs):
        super(RegisterUserPasswordForm, self).__init__(*args, **kwargs)
        self.user = None
        
    def validate(self):
        initial_validation = super(RegisterUserPasswordForm, self).validate()
        if not initial_validation:
            self.username.errors.append("Initial fail")
            return False
        username = compose_username(self.username.data, None, 'local')
        self.user = User.query.filter_by(username=username).first()
        if self.user:
            self.username.errors.append("Username already registered")
            return False
        return True


class RequestPasswordChangeForm(Form):

    username = TextField('Username',
                    validators=[DataRequired(), Length(min=3, max=25)])
    request = SubmitField('Request')

    def __init__(self, *args, **kwargs):
        super(RequestPasswordChangeForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(RequestPasswordChangeForm, self).validate()
        if not initial_validation:
            return False
        username = compose_username(self.username.data, None, 'local')
        self.user = User.query.filter_by(username=username).first()
        if not self.user:
            self.username.errors.append('Unknown username')
            return False

        if not self.user.active:
            self.username.errors.append('User not activated')
            return False

        return True