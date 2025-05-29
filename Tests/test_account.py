import pytest
from unittest.mock import patch, MagicMock
from main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'user123'
            sess['email'] = 'user@email.com'
            sess['username'] = 'user123'
        yield client


def test_get_all_users_success(client):
    with patch('controllers.account.db') as mock_db:
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {'name': 'User'}
        mock_db.collection.return_value.stream.return_value = [mock_user]

        response = client.get('/account/users')
        assert response.status_code == 200
        assert b'User' in response.data


def test_get_all_users_empty(client):
    with patch('controllers.account.db') as mock_db:
        mock_db.collection.return_value.stream.return_value = []
        response = client.get('/account/users')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Nenhum usuário cadastrado foi encontrado.'


def test_get_all_users_unauthorized():
    with app.test_client() as client:
        response = client.get('/account/users')
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] == 'Nenhum usuário conectado foi encontrado.'


def test_get_user_found(client):
    with patch('controllers.account.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'name': 'User'}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.get('/account/user/user123')
        assert response.status_code == 200
        assert b'User' in response.data


def test_get_user_not_found(client):
    with patch('controllers.account.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.get('/account/user/unknown')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Usuário não encontrado.'


def test_create_user_success(client):
    with patch('controllers.account.db') as mock_db, \
            patch('helpers.passwordUtils.hash_password', return_value='hashed'), \
            patch('helpers.userHelper.is_unique_email', return_value=True), \
            patch('helpers.userHelper.is_unique_username', return_value=True):

        response = client.post('/account/create_user', json={
            'name': 'User',
            'email': 'user@gmail.com',
            'username': 'user1234',
            'password': '123456'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Usuário criado com sucesso.'


def test_create_user_missing_fields(client):
    response = client.post('/account/create_user', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Todos os campos são obrigatórios.'


def test_create_user_email_not_unique(client):
    with patch('helpers.userHelper.is_unique_email', return_value=False):
        response = client.post('/account/create_user', json={
            'name': 'User',
            'email': 'existing@email.com',
            'username': 'user123',
            'password': '123456'
        })
        assert response.status_code == 409
        data = response.get_json()
        assert data['error'] == 'Esse e-mail já está sendo utilizado.'


def test_create_user_username_not_unique(client):
    with patch('helpers.userHelper.is_unique_email', return_value=True), \
            patch('helpers.userHelper.is_unique_username', return_value=False):
        response = client.post('/account/create_user', json={
            'name': 'User',
            'email': 'user@hotmail.com',
            'username': 'existing_user',
            'password': '123456'
        })
        assert response.status_code == 409
        data = response.get_json()
        assert data['error'] == 'Esse nome de usuário já está sendo utilizado.'


def test_update_user_success(client):
    with patch('controllers.account.db') as mock_db, \
            patch('helpers.userHelper.is_unique_email_update', return_value=True), \
            patch('helpers.userHelper.is_unique_username_update', return_value=True):

        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.put('/account/update_user', json={
            'name': 'New Name',
            'email': 'new@email.com',
            'username': 'newuser'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Dados do usuário atualizados.'


def test_update_user_conflict_email(client):
    with patch('helpers.userHelper.is_unique_email_update', return_value=False):
        response = client.put('/account/update_user', json={
            'name': 'User',
            'email': 'existing@email.com',
            'username': 'user123'
        })
        assert response.status_code == 409
        data = response.get_json()
        assert data['error'] == 'Esse e-mail já está sendo utilizado.'


def test_update_user_missing_fields(client):
    response = client.put('/account/update_user', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Todos os campos são obrigatórios.'


def test_delete_user_success(client):
    with patch('controllers.account.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.delete('/account/delete_user')
        assert response.status_code == 204


def test_delete_user_not_found(client):
    with patch('controllers.account.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.delete('/account/delete_user')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Usuário não encontrado.'
