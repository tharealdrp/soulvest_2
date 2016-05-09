from flask import Flask

app = Flask(__name__, static_url_path="")

import views

@app.errorhandler(404)
def page_not_found(e):
  """Return a custom 404 error."""
  return "This is not the page you're looking for.", 404


@app.errorhandler(500)
def application_error(e):
  """Return a custom 500 error."""
  return 'Oops, our bad: {}'.format(e), 500
