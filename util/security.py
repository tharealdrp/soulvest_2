from itsdangerous import URLSafeTimedSerializer

from . import main

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
