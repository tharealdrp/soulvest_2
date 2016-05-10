from flask import render_template, redirect, request, url_for, flash
import flask.ext.login as flask_login

from soulvest import app
from soulvest.forms import SignInForm, ForgotPasswordForm, SignUpForm
from soulvest.models import User, password_hash, get_user_by_email_and_password

from google.appengine.ext import ndb
import logging

#########################
# index / login
#########################
@app.route('/', methods=["GET", "POST"])
def index():
  form = SignInForm()
  if request.method == 'POST':
    if form.validate_on_submit():
      user = get_user_by_email_and_password(form.sign_in_email.data, form.sign_in_password.data)
      if user:
        user.id = user.email
        flask_login.login_user(user)
        return redirect(url_for('account'))
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
      user = get_user_by_email_and_password(form.sign_in_email.data, form.sign_in_password.data)
      if user:
        user.id = user.email
        flask_login.login_user(user)
        return redirect(url_for('account'))
    return render_template('login.html', form=form)

#########################
# logout
#########################
@app.route('/logout')
def logout():
  flask_login.logout_user()
  return render_template('logout.html')

#########################
# signup
#########################
@app.route('/signup', methods=["GET", "POST"])
def signup():
  form = SignUpForm()
  if form.validate_on_submit():
    user = User(email=form.sign_up_email.data, verified=True)
    user.put()
    user.password_hash = password_hash(user, form.sign_up_password.data)
    user.put()
    return redirect(url_for('signup_thankyou'))
  return render_template('signup.html', form=form)

#########################
# forgot password
#########################
@app.route('/forgot-password', methods=["GET", "POST"])
def forgot_password():
  form = ForgotPasswordForm()
  if form.validate_on_submit():
    # Check the password and log the user in
    # [...]
    return render_template('password-reset-link-sent.html')
  return render_template('forgot-password.html', form=form)

#########################
# account
#########################
@app.route('/account')
@flask_login.login_required
def account():
  return render_template('account.html')

#########################
# signup thank you
#########################
@app.route('/signup-thankyou')
def signup_thankyou():
  return render_template('signup-thankyou.html')
