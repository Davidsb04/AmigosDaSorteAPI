from flask import Flask
from flask_session import Session

app = Flask(__name__)

#Configuração da SECRET_KEY do JWT
app.config['SECRET_KEY'] = '08JhD*4{8gQg£{aiP(a'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


from controllers.account import account_bp
app.register_blueprint(account_bp, url_prefix='/account')

from controllers.login import login_bp
app.register_blueprint(login_bp, url_prefix='/login')


if __name__ == '__main__':
    app.run(debug=True)
