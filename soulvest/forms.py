from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from wtforms.validators import ValidationError

from soulvest.models import User, get_user_by_email_and_password


class UniqueEmail(object):
  def __call__(self, form, field):
    user = User.query(User.email == field.data).get()
    if user:
      raise ValidationError('Sorry, that email is already taken.')

class ValidLogin(object):
  def __call__(self, form, field):
    user = get_user_by_email_and_password(
      form.sign_in_email.data, form.sign_in_password.data)
    if not user:
      raise ValidationError(
        "Sorry, we couldn't find a user with that email and password.")


class SignInForm(Form):
  sign_in_email = StringField('Email', validators = [
      DataRequired(), Email()])
  sign_in_password = PasswordField('Password', validators=[DataRequired()])
  def validate(self):
    if not Form.validate(self):
      return False
    user = get_user_by_email_and_password(
      self.sign_in_email.data, self.sign_in_password.data)
    if not user:
      self.sign_in_email.errors.append(
        "Sorry, we couldn't find a user with that email and password.")
    return True


class SignUpForm(Form):
  sign_up_email = StringField('Email', validators = [
      DataRequired(), Email(), UniqueEmail()])
  sign_up_password = PasswordField('Password', validators=[DataRequired()])


class ForgotPasswordForm(Form):
  sign_in_email = StringField('Email', validators=[DataRequired(), Email()])

