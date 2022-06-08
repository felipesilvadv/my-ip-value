from .base import Base
import sqlalchemy as sa
import re
from logs.log import getLogger
import os
import sqlite3 # hay que borrarlo 

connection = sqlite3.connect('db/datos.db')
logger = getLogger(__name__)

auxiliar_table = sa.schema.Table(
    'ip_tokens', Base.metadata,
    sa.Column('token_id', sa.ForeignKey('tokens.id')),
    sa.Column('ip_id', sa.ForeignKey('direcciones.id'))
)

class Direccion(Base):

    __tablename__ = 'direcciones'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    ip = sa.Column(sa.String(16))
    time = sa.Column(sa.types.DateTime, server_default=sa.sql.func.now())

    ip_pattern = r"[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}"

    def __init__(self, ip):
        if re.match(self.ip_pattern, ip) is None:
            raise ValueError(f'IP no cumple con el formato ip dada es {ip}')
        self.ip = ip


class User(Base):

    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    email = sa.Column(sa.String(20))
    username = sa.Column(sa.String(30), unique=True, nullable=False)
    tokens = sa.orm.relationship("Token", backref='user')
    

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def add_ip(self, ip, token):
        if token not in self.tokens:
            raise ValueError('Token no pertenece a usuario')
        try:
            new_ip = Direccion(ip)
        except ValueError:
            return False
        token.ips.append(new_ip)
        return True

class Token(Base):

    __tablename__ = 'tokens'

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    value = sa.Column(sa.String(128), unique=True, nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    ips = sa.orm.relationship("Direccion", secondary=auxiliar_table)

    def __init__(self, token=None):
        if token is None:

           self.value = self.new_token()
        else:
            self.value = token

    @staticmethod
    def new_token():
        return os.urandom(64).hex()

    def validate(self):
        return True




def get_ip():
    try:
        sql = "SELECT ip FROM direcciones WHERE id = (SELECT MAX(id) FROM direcciones)"
        logger.info('Obteniendo direccion IP')
        cursor = connection.cursor()
        cursor.execute(sql)
        dato = cursor.fetchone()
        return dato[0]
    except sqlite3.OperationalError as err:
        logger.error('Fallo algo en la DB')
        logger.exception(err)
        return ''

def update_ip(new_ip):
    ip_pattern = r"[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}"
    if re.match(ip_pattern, new_ip):
        sql = """INSERT INTO direcciones (ip) VALUES (?)"""
        cursor = connection.cursor()
        cursor.execute(sql, new_ip)
    else:
        raise ValueError(f'Invalid ip {new_ip}')


def auth_tokens():
    pass

def init_db():
    table = """
        CREATE TABLE direcciones(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 ip VARCHAR(16),
                                 time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    """
    users = """create table users(id integer primary key autoincrement,
     username varchar(30), email varchar(40), level integer default 0,
     created_at timestamp default current_timestamp)"""
    status = """create table db_status(status integer default 0)"""
    tokens = """CREATE TABLE tokens(user_id integer, token varchar(128), created_at timestamp default current_timestamp,
    constraint fk_user foreign key (user_id) references users(id))"""
    queries = [table, users, status, tokens]
    for q in queries:
        try:
            create_table(q)
        except sqlite3.OperationalError as err:
            patt = r"\w+ \w+ [\w_\-]+\("
            name = re.findall(patt, q)[0][13:-1]
            logger.error(f'Ya existía tabla {name} en la base de datos')
    
    user, email = os.environ.get('USER'), os.environ.get('EMAIL')
    if user and email:
        add_user(user, email)
    else:
        raise NameError('Falta definir variables de entorno')
    set_status = """UPDATE db_status set status = 1"""
    create_table(set_status)
    
def add_user(username, email):
    pass

def add_token(username):
    q = """SELECT id from users where username = (?)"""
    cursor = connection.cursor()
    cursor.execute(q, username)
    id = cursor.fetchone()
    if len(id):
        id = id[0]
        token = os.urandom(64).hex()
        q1 = """INSERT INTO tokens(user_id, token) VALUES (?, ?)"""
        try:
            cursor.execute(q1, id, token)
            return token
        except sqlite3.OperationalError as err:
            logger.exception(err)
            return ''   
    else:
        raise ValueError('Username no encontrado')


def create_table(query):
    logger.info('Creando tabla en base de datos')
    cursor = connection.cursor()
    cursor.execute(query)
    logger.info('Se creo tabla en base de datos')