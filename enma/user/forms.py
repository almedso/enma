from flask_wtf import Form
from wtforms import TextField, PasswordField, HiddenField, BooleanField
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms import ValidationError
from .models import User
from flask import flash


class ReadonlyTextField(TextField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyTextField, self).__call__(*args, **kwargs)


class ReadonlyBooleanField(BooleanField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('disabled', True)
        return super(ReadonlyBooleanField, self).__call__(*args, **kwargs)


class EmailExists(object):
    """
    WTF Validator that checks if an email address already exists.

    via the exclude parameter a specific email addressed can be excluded
    from the check (i.e. the current email address of a user)
    """
    def __init__(self, exclude='', message='Email already registered'):
        self._exclude=exclude
        self._message = message

    def __call__(self, form, field):
        user = User.query.filter_by(email=field.data).first()
        if user and user.email != self._exclude:
            raise ValidationError(self._message)


class RegisterForm(Form):
    openid_provider = ReadonlyTextField('OpenId Provider')
    username = TextField('Username',
                    validators=[DataRequired(), Length(min=3, max=25)])
    email = TextField('Email',
                    validators=[DataRequired(), Email(), EmailExists(),
                                Length(min=6, max=40)])
    first_name = TextField('First Name',
                    validators=[DataRequired(), Length(min=1, max=25)])
    last_name = TextField('Last Name',
                    validators=[DataRequired(), Length(min=1, max=25)])
    password = PasswordField('Password',
                                validators=[Optional(), Length(min=6, max=40)])
    confirm = PasswordField('Verify password',
                [DataRequired(), EqualTo('password', message='Passwords must match')])
    register = SubmitField('Create Account', id='register')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        return True


class EditForm(Form):
    username = HiddenField('Username', validators=[])
    firstname = TextField('First Name', validators=[DataRequired(),
                            Length(min=2, max=40)])
    lastname = TextField('Last Name', validators=[DataRequired(),
                            Length(min=2, max=40)])
    email = TextField('Email', validators=[DataRequired(), Email(),
                            Length(min=6, max=40)])
    apply = SubmitField('Apply')

    def update_data(self, user=None):
        if user:
            self.username.data = user.username
            self.firstname.data = user.first_name
            self.lastname.data = user.last_name
            self.email.data = user.email

            

    def validate(self):
        initial_validation = super(EditForm, self).validate()
        if not initial_validation:
            return False
        return True

class DeleteForm(Form):
    username = HiddenField('Username', validators=[])
    safety_question = BooleanField('Do you really want to delete the user?',
                                  default = False)
    delete = SubmitField('Delete')

    def __init__(self, user=None, *args, **kwargs):
        super(DeleteForm, self).__init__(*args, **kwargs)
        print user
        if user:
            self.username.data = user.username

    def validate(self):
        if self.safety_question.data == 0:
            self.safety_question.errors = []
            self.safety_question.errors.append(
                "Please confirm by setting the checkmark")
            return False
        return True

class ChangePasswordForm(Form):
    username = HiddenField('username',)
    oldpassword = PasswordField('Old Password',
                        validators=[DataRequired(), Length(min=6, max=40)])
    password = PasswordField('Password',
                        validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField('Verify password',
                [DataRequired(), EqualTo('password',
                                          message='Passwords must match')])
    setpwd = SubmitField('Set Password')

    def update_data(self, user):
        self.username.data = user.username

    def validate(self):
        flash('validate chpwd called', 'info')

        initial_validation = super(ChangePasswordForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("User does not exist")
            return False
        if not user.check_password(self.oldpassword.data):
            self.email.errors.append("Old password is wrong")
            return False
        return True


class UserAdminForm(Form):
    username = ReadonlyTextField('Username')
    email = ReadonlyTextField('Email')
    last_seen = ReadonlyTextField('Last seen')
    created_at = ReadonlyTextField('Created at')
    auth_provider = ReadonlyTextField('Authentication Provider')
    email_validated = ReadonlyBooleanField('Email validated')
    active = BooleanField('Is user active')
    role = SelectField(u'Role', choices=[])
    apply = SubmitField('Apply')


    def __init__(self, roles=['SiteAdmin'], *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = map(lambda x: (x, x), roles)

    def update_data(self, user=None):
        if user:
            self.username.data = user.username
            self.email.data = user.email
            self.auth_provider.data = user.auth_provider
            self.created_at.data = user.created_at
            self.last_seen.data = user.last_seen
            self.email_validated.data = user.email_validated
            self.active.data = user.active
            self.role.data = str(user.role)


class RestTokenForm(Form):
    token = ReadonlyTextField('Access Token')
    expiry = ReadonlyTextField('Token Expiry')
    lifetime = SelectField('Token Lifetime', default='60',
                           choices=[('60', 'One Minute'),
                                    ('3600', 'One hour'),
                                    ('86400', 'One day'),
                                    ('2592000', '30 days')])

    generate = SubmitField('Generate new Token')

    def update_data(self, user):
        pass