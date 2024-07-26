from models.usuario import Usuarios

def verificaToken(token, email):
    if not token or not email:
        return False
    if Usuarios.query.filter_by(email=email, token_auth=token).first():
        return True
    else:
        return False