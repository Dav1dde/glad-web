from flask import Blueprint, abort


generated = Blueprint('generated', __name__)


# @generated.route('/')
# def landing():
#     return abort(404)