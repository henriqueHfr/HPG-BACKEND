import os
import random

from flask import request, jsonify
from flask_mail import Message
from helpers.verificaToken import verificaToken
from models.usuario import Usuarios
from models.gestaoPessoal import GestaoPessoal
from main import app, db, mail
from flask_bcrypt import check_password_hash, generate_password_hash
import jwt
import random
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
    token = request.headers.get('x-access-tokens')
    email = data.get('email')
    response = verificaToken(token, email)

    if response == True:
        return jsonify({"error": "usuario autenticado"}), 200
    else:
        return jsonify({"error": "Usuário não autenticado"}), 401

    return jsonify({"error": "algo inesperado aconteceu"})


@app.route('/gestaoPessoal', methods=['POST'])
def gestaopessoal():
    data = request.json
    token = request.headers.get('x-access-tokens')
    email = data.get('email')
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
    token = request.headers.get('x-access-tokens')
    titulo = data.get('titulo')
    conteudo = data.get('conteudo')
    data_hora = data.get('data')

    response = verificaToken(token, email)
    if response:
        usuario = Usuarios.query.filter_by(email=email, token_auth=token).first()
        card = GestaoPessoal(titulo=titulo, conteudo=conteudo, user_id=usuario.id, data_hora=data_hora)
        db.session.add(card)
        db.session.commit()
        msg = Message('Card novo criado no HPG', sender=os.environ.get('MAIL_USERNAME'),
                      recipients=[usuario.email],
                      body=f'''Venho informar que foi criado um novo card no HPG\n\n\n
titulo:{titulo},\n
Conteudo: {conteudo},\n
Data e hora do termino: {data_hora}
                                   '''
                      )
        mail.send(msg)
        return jsonify({"message": "Card criada com sucesso"}), 201
    else:
        return jsonify({"error": "Não foi possível criar o card!"}), 401

    return jsonify({"error": "Algo inesperado aconteceu, tente novamente"}), 500


@app.route('/buscaCardPessoal', methods=['POST'])
def buscaCardPessoal():
    data = request.json
    email = data.get('email')
    token = request.headers.get('x-access-tokens')

    response = verificaToken(token, email)

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


@app.route('/resetSenha', methods=['POST'])
def resetSenha():
    data = request.json
    email = data.get('email')

    usuario = Usuarios.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "Usuário não possui cadastro"}), 401

    random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    hashed_token = generate_password_hash(random_numbers).decode('utf-8')
    msg = Message('Codigo para resetar senha',
                  sender=os.environ.get('MAIL_USERNAME'),
                  recipients=[usuario.email],
                  body=f'''Codigo para efetuar o reset do seu usuário.\n\n\
Numero : {random_numbers}
                  '''
                  )
    mail.send(msg)

    usuario.token_reset = hashed_token
    db.session.commit()

    return jsonify(dict(message="Usuário conectado",
                            token=hashed_token)), 200

@app.route('/verificaCodeReset', methods=['POST'])
def verificaCodeReset():
    data = request.json
    token = data.get('token')
    code = data.get('code')
    usuario = Usuarios.query.filter_by(token_reset=token).first()
    code_sem_hash = check_password_hash(usuario.token_reset, code)

    if usuario and code_sem_hash:
        return jsonify({"message": "codigo autenticado com sucesso"}), 200

    if not code_sem_hash:
        return jsonify({"message": "codigo de autenticação errado"}), 401

    return jsonify({"error": "algo inesperado aconteceu, tente novamente"}), 401


@app.route('/atualizaSenha', methods=['POST'])
def atualizaSenha():
    data = request.json
    token = data.get('token')
    senha = data.get('senha')
    email = data.get('email')
    if token and senha and email:
        usuario = Usuarios.query.filter_by(email=email, token_reset = token).first()
        if usuario:
            senha_hash = generate_password_hash(senha)
            usuario.senha = senha_hash
            usuario.token_reset = None
            db.session.commit()
            return jsonify({"success": "Senha atualizada com sucesso"}), 200

    return jsonify({"error": "Algo inesperado aconteceu"}), 400

