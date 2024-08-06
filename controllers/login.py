from flask import Blueprint, request, jsonify
from data.firebaseConfig import db
from helpers.passwordUtils import check_password
from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask_jwt_extended import jwt_required

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
        
        
        acess_token = create_access_token(identity={'username' : user_data['username']}, expires_delta=timedelta(hours=1))
        return jsonify(acess_token=acess_token)
        
        
    except Exception as e:
        return jsonify({
            "erro" : str(e) or "Não foi possível efetuar o login"
        }), 500
        
@login_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify(message="Este é um endpoint protegido")