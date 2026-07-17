from flask import Blueprint

bp = Blueprint("api", __name__)

from . import schools
from . import localities
from . import jobs
from . import search
from . import users
from . import regions
