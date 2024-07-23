from models.usuario import Usuarios

def verificaToken(token):
    if not token:
        return False
    if Usuarios.query.filter_by(token_auth=token).first():
        return True
    else:
        return False