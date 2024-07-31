from functools import wraps
from flask import request, jsonify
from models.usuario import Usuarios
import jwt
from main import app

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('x-access-tokens')
        if not token:
            return jsonify({"error": "Token é necessário!"}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuarios.query.filter_by(id=data['id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido!"}), 401

        return f(current_user, *args, **kwargs)

    return decorator