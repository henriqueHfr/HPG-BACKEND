from flask import request, jsonify
from helpers.verificaToken import verificaToken
from models.usuario import Usuarios
from models.gestaoPessoal import GestaoPessoal
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

@app.route('/home', methods=['POST'])
def home():
    data = request.json
    token = data.get('token')
    response = verificaToken(token)

    if response == True:
        return jsonify({"error": "usuario autenticado"}), 200
    else:
        return jsonify({"error": "Usuário não autenticado"}), 401

    return jsonify({"error": "algo inesperado aconteceu"})


@app.route('/gestaoPessoal', methods=['POST'])
def gestaopessoal():
    data = request.json
    token = data.get('token')
    email = data.get('email')
    print(data)
    response = verificaToken(token, email)
    if response == True:
        return jsonify({"message": "usuario autenticado "}), 200
    else:
        return jsonify({"error": "usuario não autenticado"}), 401

    return jsonify({"error": "algo inesperado aconteceu, tente novamente"})


@app.route('/criarNovoCardPessoal', methods=['POST'])
def criarNovoCardPessoal():
    data = request.json
    email = data.get('email')
    token = data.get('token')
    titutlo = data.get('titulo')
    conteudo = data.get('conteudo')
    data_hora = data.get('data')
    print(data)

    response = verificaToken(token)
    print(response)
    if response:
        usuario = Usuarios.query.filter_by(email=email).first()
        print(usuario)
        card = GestaoPessoal(titulo=titutlo, conteudo=conteudo, user_id=usuario.id, data_hora=data_hora)
        print(card)
        db.session.add(card)
        db.session.commit()

        return jsonify({"message": "card criada com sucesso"}), 201
    else:
        return jsonify({"error": "não foi possivel criar o card!"}), 401

    return jsonify({"error": "algo inesperado aconteceu, tente novamente"}), 500


@app.route('/buscaCardPessoal', methods=['POST'])
def buscaCardPessoal():
    data = request.json
    email = data.get('email')
    token = data.get('token')

    response = verificaToken(token)

    if response:
        usuario = Usuarios.query.filter_by(email=email, token_auth=token).first()
        if usuario:
            ListaCard = GestaoPessoal.query.filter_by(user_id=usuario.id).order_by(GestaoPessoal.id).all()
            cards = [{'id': card.id, 'titulo': card.titulo, 'conteudo': card.conteudo,'data': card.data_hora ,'user_id': card.user_id} for card in ListaCard]
            return jsonify({"cards": cards}), 200
        else:
            return jsonify({"error": "usuário não encontrado"}), 404
    else:
        return jsonify({"error": "usuário não autenticado"}), 401
@app.route('/deletaCardPessoal', methods=['POST'])
def deletaCardPessoal():
    data = request.json
    id = data.get('id')
    if id is None:
        return jsonify({"error": "ID não fornecido"}), 400

    try:
        GestaoPessoal.query.filter_by(id=id).delete()
        db.session.commit()
        return jsonify({"message": "Card deletado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"error": "algo inesperado aconteceu, tente novamente"}), 401