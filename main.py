from flask import Flask
from flask_jwt_extended import JWTManager
import json

app = Flask(__name__)

#Configuração da SECRET_KEY do JWT
with open('config.json') as config_file:
    config = json.load(config_file)
    app.config['SECRET_KEY'] = config['SECRET_KEY']
    app.config['JWT_SECRET_KEY'] = config['SECRET_KEY']

jwt = JWTManager(app)


from controllers.account import account_bp
app.register_blueprint(account_bp, url_prefix='/account')

from controllers.login import login_bp
app.register_blueprint(login_bp, url_prefix='/login')


if __name__ == '__main__':
    app.run(debug=True)
