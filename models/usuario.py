from main import db
class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(20), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    token_auth = db.Column(db.String(255), nullable=True, unique=True)
    token_reset = db.Column(db.String(60), nullable=True)
    def __repr__(self):
        return '<Usuario %r>' % self.nome
