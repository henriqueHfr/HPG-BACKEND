import jwt
from main import app
from models.usuario import Usuarios

def verificaToken(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        usuario = Usuarios.query.filter_by(id=data['id']).first()
        if usuario:
            return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    return False