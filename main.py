from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from views.viewsUser import *

if __name__ == '__main__':
    app.run(debug=True)
