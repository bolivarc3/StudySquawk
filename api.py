from flask import render_template, Blueprint
from flask_session import Session

api = Blueprint('api', __name__, subdomain='api')
@api.route('/')
def api_main():
    return render_template("api_intro.html")