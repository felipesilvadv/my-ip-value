from .base import db_session, Base
from .models import User, Direccion, Token

session = db_session
Base = Base