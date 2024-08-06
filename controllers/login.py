from flask import Blueprint, request, jsonify, session
from data.firebaseConfig import db
from helpers.passwordUtils import check_password

login_bp = Blueprint('login', __name__)  

#Rota para validação das credenciais de acesso do usuário
@login_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    
    if not email or not password:
        return jsonify({
            "erro" : "Insira todos os campos."
        }), 400
    
    try:   
        user_query = db.collection('users').where('email', '==', email).stream()
        users = list(user_query)
        
        if not users:
            return jsonify({
                "erro" : "Usuário não encontrado"
            }), 400
        
        user_data = users[0].to_dict()
        
        if not check_password(user_data['password'], password):
            return jsonify({
                "erro" : "Senha inválida."
            }), 400           
        
        
        username = user_data['username']
        session['username'] = username
        return jsonify({
            "message" : "Usuário logado com sucesso."
        }), 200
        
        
    except Exception as e:
        return jsonify({
            "erro" : str(e) or "Não foi possível efetuar o login"
        }), 500
        
#Rota para desconectar usuário
@login_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({
        "message" : "Usuário desconectado com sucesso."
    }), 200
        
@login_bp.route('/protected', methods=['GET'])
def protected():
    if 'username' in session:
        return jsonify({
            "message" : "Você está logado :)"
        }), 200
    return jsonify({
        "message" : "Efetue o login para acessar."
    }), 400