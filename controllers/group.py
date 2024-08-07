from flask import Blueprint, jsonify, session, request
from data.firebaseConfig import db
from helpers.passwordUtils import hash_password
import datetime

group_bp = Blueprint('group', __name__)

#Rota para criar o grupo de palpites
@group_bp.route('/create_group', methods=['POST'])
def create_group():
    if 'user_id' in session:
        data = request.json
        group_name = data.get('group_name')
        password = data.get('password')
        owner_id = session.get('user_id')
        
        if not group_name or not password:
            return jsonify({
                "erro" : "Insira todos os campo"
            }), 400
        
        print(session.get('user_id'))
        hashed_password = hash_password(password)
        
        new_group = {
            'group_name' : group_name,
            'password' : hashed_password,
            'owner_id' : owner_id,
            'members' : [owner_id],
            'created_at' : datetime.datetime.now()
        }
        
        try:
            #Cria o documento e adiciona o Id gerado pelo Firebase dentro do próprio documento
            group_ref = db.collection('groups').add(new_group)
            group_id = group_ref[1].id
            db.collection('groups').document(group_id).update({'group_id' : group_id})
            
            return jsonify({
                "message" : "Grupo criado com sucesso."
            }), 200
        
        except:
            return jsonify({
                "erro" : "Não foi possível criar o grupo."
            })
        
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 400
    
#Rota para obter todos os grupos
@group_bp.route('/groups', methods=['GET'])
def get_all_groups():
    if 'user_id' in session:
        groups = db.collection('groups').stream()
        groups_list = [group.to_dict() for group in groups]       
        return jsonify(groups_list), 200
    
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 400
    
# Rota para retornar um grupo
@group_bp.route('/group/<group_id>', methods=['GET'])
def get_group(group_id):
    doc_ref = db.collection('groups').document(group_id)
    doc = doc_ref.get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    return jsonify({
        "error": "Grupo não encontrado."
    }), 404