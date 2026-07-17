from flask import Blueprint, render_template

main_bp = Blueprint("main_bp", __name__)

from . import home
from . import schools
from . import jobs


@main_bp.route("/")
def index():
    return render_template("home.html")
