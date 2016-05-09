from flask import render_template, redirect, url_for
from soulvest import app
from soulvest.forms import EmailPasswordForm

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login', methods=["GET", "POST"])
def login():
    form = EmailPasswordForm()
    if form.validate_on_submit():

        # Check the password and log the user in
        # [...]

        return redirect(url_for('index'))
    return render_template('login.html', form=form)
