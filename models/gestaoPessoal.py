from datetime import datetime
from main import db

class GestaoPessoal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(255), nullable=False)
    conteudo = db.Column(db.String(1000), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __repr__(self):
        return '<Pessoal %r>' % self.titulo
