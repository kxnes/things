from flask import Flask


application = Flask(__name__)


# to prevent recursive import and trigger flask routing
from . import views
