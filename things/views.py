from flask import jsonify

from . import application
from .models import THINGS
from .decorators import token_auth_requires, simple_paginating, simple_sorting, simple_filtering


@application.route('/api/v1.0/things/')
@token_auth_requires
@simple_paginating
@simple_sorting
@simple_filtering
def things_list():
    return jsonify(THINGS)
