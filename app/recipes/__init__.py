from flask import Blueprint

recipes = Blueprint('recipes', __name__)

from . import views