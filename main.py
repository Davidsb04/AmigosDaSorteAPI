from flask import Flask
from controllers.account import account_bp

app = Flask(__name__)

app.register_blueprint(account_bp, url_prefix='/account')


if __name__ == '__main__':
    app.run(debug=True)
