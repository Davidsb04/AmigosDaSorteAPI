import pytest
from unittest.mock import patch, MagicMock
from main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'user123'
        yield client


def test_create_group_success(client):
    with patch('controllers.group.db') as mock_db:

        mock_add = mock_db.collection.return_value.add
        mock_add.return_value = (None, MagicMock(id='group123'))

        response = client.post('/group/create_group', json={
            'group_name': 'Test Group',
            'group_password': '123456'
        })

        assert response.status_code == 201
        assert b'Grupo criado com sucesso' in response.data


def test_create_group_missing_fields(client):
    response = client.post('/group/create_group', json={})
    assert response.status_code == 400
    assert b'Insira todos os campos' in response.data


def test_get_all_groups(client):
    with patch('controllers.group.db') as mock_db:
        mock_group = MagicMock()
        mock_group.to_dict.return_value = {'group_name': 'Test Group'}
        mock_db.collection.return_value.stream.return_value = [mock_group]

        response = client.get('/group/groups')
        assert response.status_code == 200
        assert b'Test Group' in response.data


def test_get_group_found(client):
    with patch('controllers.group.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {'group_name': 'Test Group'}
        mock_db.collection.return_value.where.return_value.stream.return_value = [
            mock_doc]

        response = client.get('/group/group/Test Group')
        assert response.status_code == 200
        assert b'Test Group' in response.data


def test_get_group_not_found(client):
    with patch('controllers.group.db') as mock_db:
        mock_db.collection.return_value.where.return_value.stream.return_value = []
        response = client.get('/group/group/Nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Grupo não encontrado.'
