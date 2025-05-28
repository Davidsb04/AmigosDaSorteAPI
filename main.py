from controllers.bet import bet_bp
from controllers.group import group_bp
from controllers.login import login_bp
from controllers.account import account_bp
from flask import Flask
from flask_session import Session
from helpers.userHelper import load_config
from datetime import timedelta

app = Flask(__name__)

# Configuração da SECRET_KEY do flask_session
config = load_config()

app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SESSION_TYPE'] = config['SESSION_TYPE']
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    seconds=config['PERMANENT_SESSION_LIFETIME'])
Session(app)


app.register_blueprint(account_bp, url_prefix='/account')

app.register_blueprint(login_bp, url_prefix='/login')

app.register_blueprint(group_bp, url_prefix='/group')

app.register_blueprint(bet_bp, url_prefix='/bet')


if __name__ == '__main__':
    app.run(debug=True)
