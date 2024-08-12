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
            }), 404
        
        user_data = users[0].to_dict()
        
        if not check_password(user_data['password'], password):
            return jsonify({
                "erro" : "Senha inválida."
            }), 401           
        
        
        user_id = users[0].id
        session['user_id'] = user_id
        return jsonify({
            "message" : "Usuário conectado com sucesso."
        }), 201
        
        
    except Exception as e:
        return jsonify({
            "erro" : str(e) or "Não foi possível efetuar o login."
        }), 500
        
#Rota para desconectar usuário
@login_bp.route('/logout', methods=['POST'])
def logout():
    if 'user_id' in session:    
        session.pop('user_id', None)
        return jsonify({
            "message" : "Usuário desconectado com sucesso."
        }), 204     
    return jsonify({
            "error" : "Nenhum usuário conectado foi encontrado."
        }), 401
        
#Rota para retornar usuário conectado
@login_bp.route('/current_user', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        user_id = session['user_id']
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()    
            return jsonify({
                "email": user_data.get('email'),
                "username": user_data.get('username')
            }), 200
        
        return jsonify({
            "erro": "Usuário não encontrado."
        }), 404
    
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 401
