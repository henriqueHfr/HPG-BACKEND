import os
import random

from flask import request, jsonify
from flask_mail import Message

from helpers.token_required import token_required
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


@app.route('/home', methods=['POST'])
@token_required
def home(current_user):
    return jsonify({"message": "Usuário autenticado"}), 200

@app.route('/gestaoPessoal', methods=['POST'])
@token_required
def gestaopessoal(current_user):
    return jsonify({"message": "Usuário autenticado"}), 200

@app.route('/criarNovoCardPessoal', methods=['POST'])
@token_required
def criarNovoCardPessoal(current_user):
    data = request.json
    titulo = data.get('titulo')
    conteudo = data.get('conteudo')
    data_hora = data.get('data')

    card = GestaoPessoal(titulo=titulo, conteudo=conteudo, user_id=current_user.id, data_hora=data_hora)
    db.session.add(card)
    db.session.commit()

    msg = Message('Card novo criado no HPG', sender=os.environ.get('MAIL_USERNAME'),
                  recipients=[current_user.email],
                  body=f'''Venho informar que foi criado um novo card no HPG\n\n\n
titulo:{titulo},\n
Conteudo: {conteudo},\n
Data e hora do termino: {data_hora}
                                   '''
                  )
    mail.send(msg)
    return jsonify({"message": "Card criado com sucesso"}), 201

@app.route('/buscaCardPessoal', methods=['POST'])
@token_required
def buscaCardPessoal(current_user):
    ListaCard = GestaoPessoal.query.filter_by(user_id=current_user.id).order_by(GestaoPessoal.id).all()
    cards = [{'id': card.id, 'titulo': card.titulo, 'conteudo': card.conteudo, 'data': card.data_hora, 'user_id': card.user_id} for card in ListaCard]
    return jsonify({"cards": cards}), 200

@app.route('/deletaCardPessoal', methods=['POST'])
@token_required
def deletaCardPessoal(current_user):
    data = request.json
    id = data.get('id')
    if id is None:
        return jsonify({"error": "ID não fornecido"}), 400

    try:
        GestaoPessoal.query.filter_by(id=id, user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({"message": "Card deletado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

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

    return jsonify(dict(message="Código de reset enviado",
                            token=hashed_token)), 200

@app.route('/verificaCodeReset', methods=['POST'])
def verificaCodeReset():
    data = request.json
    token = data.get('token')
    code = data.get('code')
    usuario = Usuarios.query.filter_by(token_reset=token).first()
    code_sem_hash = check_password_hash(usuario.token_reset, code)

    if usuario and code_sem_hash:
        return jsonify({"message": "Código autenticado com sucesso"}), 200
    else:
        return jsonify({"error": "Código de autenticação errado"}), 401

@app.route('/atualizaSenha', methods=['POST'])
def atualizaSenha():
    data = request.json
    token = data.get('token')
    senha = data.get('senha')
    email = data.get('email')
    if token and senha and email:
        usuario = Usuarios.query.filter_by(email=email, token_reset=token).first()
        if usuario:
            senha_hash = generate_password_hash(senha).decode('utf-8')
            usuario.senha = senha_hash
            usuario.token_reset = None
            db.session.commit()
            return jsonify({"success": "Senha atualizada com sucesso"}), 200

    return jsonify({"error": "Algo inesperado aconteceu"}), 400


