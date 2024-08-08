from flask import Blueprint, request, jsonify, session
from data.firebaseConfig import db

bet_bp = Blueprint('bet', __name__)

#Rota para registrar aposta do usuário
@bet_bp.route('place_bet/<group_id>/<match_id>', methods=['POST'])
def place_bet(group_id, match_id):
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        home_score = data.get('home_score')
        away_score = data.get('away_score')
        
        if home_score is None or away_score is None:
            return jsonify({
                "erro" : "Placares da partida não inseridos."
            }), 400
        
        group_ref = db.collection('groups').document(group_id)
        group= group_ref.get()
        
        if group.exists and user_id in group.to_dict().get('members', []):
            bet_data = {
                "match_id" : match_id,
                "user_id" : user_id,
                "bet" : {
                    "fulltime" : {
                        "home" : home_score,
                        "away" : away_score
                    }
                },
                "result" : "aguardando resultado"
            }
            
            bet_ref = group_ref.collection('bets').document()
            bet_ref.set(bet_data)
            return jsonify({
                "message" : "Aposta registrada com sucesso."
            }), 200
        
        return jsonify({
            "erro" : "Usuário não autorizado ou grupo não encontrado."
        }), 400
    
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 400