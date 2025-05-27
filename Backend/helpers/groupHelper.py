from data.firebaseConfig import db

def get_group_for_update(group_id):
    doc_ref = db.collection('groups').document(group_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.id, doc.to_dict()
    return None