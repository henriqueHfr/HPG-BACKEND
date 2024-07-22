from flask import request, jsonify
from helpers.verificaToken import verificaToken
from models.usuario import Usuarios
from main import app, db
from flask_bcrypt import check_password_hash, generate_password_hash
import jwt
import datetime


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')
    usuario = Usuarios.query.filter_by(email=email).first()

    if usuario and check_password_hash(usuario.senha, senha):
        token = jwt.encode({
            'id': usuario.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        usuario.token_auth = token
        db.session.commit()

        return jsonify(dict(message="Usuário conectado",
                            id=usuario.id,
                            token=token,
                            nome=usuario.nome,
                            email=usuario.email)), 200
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401


@app.route('/logout', methods=['GET'])
def logout():
    token = request.headers.get('x-access-tokens')
    if not token:
        return jsonify({"error": "Token é necessário!"}), 403

    usuario = Usuarios.query.filter_by(token_auth=token).first()
    if usuario:
        usuario.token_auth = None
        db.session.commit()
        return jsonify({"message": "Usuário desconectado"}), 200
    else:
        return jsonify({"error": "Token inválido"}), 403


@app.route('/cadastroUsuarios', methods=['POST'])
def cadastroUsuarios():
    data = request.json

    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    usuario_existente = Usuarios.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({"message": "Usuário já cadastrado"}), 400

    senha_hash = generate_password_hash(senha).decode('utf-8')
    criar_novo_user = Usuarios(email=email, nome=nome, senha=senha_hash)
    db.session.add(criar_novo_user)
    db.session.commit()

    return jsonify({"message": "Usuário cadastrado com sucesso"}), 201

@app.route('/gestaopessoal', methods=['POST'])
def gestatepessoal():
    data = request.json
    token = data.get('token')
    email = data.get('email')
    print(data)
    print("passei aqui ")
    response = verificaToken(token, email)
    print(response)

    if response == True:
        return jsonify({"error": "usuario autenticado"}), 200
    else:
        return jsonify({"error": "Usuário não autenticado"}), 401

    return jsonify({"error": "algo inesperado aconteceu"})