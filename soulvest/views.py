from flask import render_template, redirect, request, url_for, flash
import flask.ext.login as flask_login

from soulvest import app
from soulvest.forms import SignInForm, ForgotPasswordForm, SignUpForm, ActivateRenewForm
from soulvest.models import User, password_hash, get_user_by_email, get_user_by_email_and_password
from soulvest.models import get_user_by_activation_token, send_activation_link
from soulvest.models import get_user_by_password_reset_token, send_password_reset_link

from google.appengine.ext import ndb
import logging
import datetime

#########################
# index / login
#########################
@app.route('/', methods=["GET", "POST"])
def index():
  if flask_login.current_user.is_authenticated:
    return redirect(url_for('dashboard'))
  form = SignInForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      user = get_user_by_email_and_password(
        form.sign_in_email.data, form.sign_in_password.data)
      if user:
        user.id = user.email
        flask_login.login_user(user)
        return redirect(url_for('dashboard'))
      else:
        return redirect(url_for('login'))
    else:
      return redirect(url_for('login'))
  return render_template('index.html', form=form)

#########################
# login
#########################
@app.route('/login', methods=["GET", "POST"])
def login():
  form = SignInForm()
  if form.validate_on_submit():
    user = get_user_by_email_and_password(
      form.sign_in_email.data, form.sign_in_password.data)
    if user:
      user.id = user.email
      flask_login.login_user(user)
      return redirect(url_for('dashboard'))
  return render_template('login.html', form=form)

#########################
# logout
#########################
@app.route('/logout')
def logout():
  flask_login.logout_user()
  form = SignInForm()
  return redirect(url_for('index'))

#########################
# signup
#########################
@app.route('/signup', methods=["GET", "POST"])
def signup():
  signup_complete = False
  form = SignUpForm()
  if form.validate_on_submit():
    user = User(email=form.sign_up_email.data, verified=False)
    user.put()
    user.password_hash = password_hash(user, form.sign_up_password.data)
    user.put()
    # create activation link and email user
    send_activation_link(user)
    signup_complete = True
    # return redirect(url_for('signup_thankyou'))
  return render_template('signup.html', form=form, signup_complete=signup_complete)

#########################
# activate
#########################
@app.route('/activate')
def activate():
  token = request.args.get('token')
  # return token
  # if we find the user and the activation link is valid
  # log the user in and redirect to the dashboard
  user = get_user_by_activation_token(token)
  # if user is None the token is invalid. allow user to enter email and
  # get a new link
  if user:
    user.verified = True
    user.put()
    user.id = user.email
    flask_login.login_user(user)
    # return flask_login.current_user.email
    return render_template('activate.html')
  return redirect(url_for('activate_renew'))

#########################
# activate renew
#########################
@app.route('/activate-renew', methods=["GET", "POST"])
def activate_renew():
  form = ActivateRenewForm()
  already_activated = False
  if form.validate_on_submit():
    user = get_user_by_email(
      form.email.data)
    if user:
      if user.verified == False:
        send_activation_link(user)
        return redirect(url_for('signup_thankyou'))
      else:
        already_activated=True
  return render_template('activate-renew.html', form=form, already_activated=already_activated)

#########################
# forgot password
#########################
@app.route('/forgot-password', methods=["GET", "POST"])
def forgot_password():
  link_sent = False
  form = ForgotPasswordForm()
  if form.validate_on_submit():
    user = get_user_by_email(form.email.data)
    send_password_reset_link(user)
    link_sent = True
  return render_template('forgot-password.html', form=form, link_sent=link_sent)

#########################
# Reset password
#########################
@app.route('/reset-password', methods=["GET", "POST"])
def reset_password():
  form = ResetPasswordForm()
  token = request.args.get('token')
  user = get_user_by_password_reset_token(token)
  if not user:
    # invalid password reset token
    return render_template('invalid-password-reset-token.html')
  if form.validate_on_submit():
    user.password_hash = password_hash(user, form.new_password.data)
    user.put()
    user.id = user.email
    flask_login.login_user(user)
    return redirect(url_for('dashboard'))
  return render_template('reset-password.html', form=form)

#########################
# account
#########################
@app.route('/account')
@flask_login.login_required
def account():
  # return 'Logged in as: ' + flask_login.current_user.email
  return render_template('account.html')

#########################
# dashboard
#########################
@app.route('/dashboard')
@flask_login.login_required
def dashboard():
  # return 'Logged in as: ' + flask_login.current_user.email
  return render_template('dashboard.html')

#########################
# signup thank you
#########################
@app.route('/signup-thankyou')
def signup_thankyou():
  return render_template('signup-thankyou.html')
