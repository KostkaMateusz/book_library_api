import pytest


def test_get_authors_no_records(client):
    response = client.get('api/v1/authors')
    excepted_results = {
        'success': True,
        'data': [],
        'numbers_of_records': 0,
        'pagination':  {
            'total_pages': 0,
            'total_records': 0,
            'current_page': '/api/v1/authors?page=1'
        }
    }

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.get_json() == excepted_results


def test_get_authors(client, sample_data):
    response = client.get('api/v1/authors')
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['numbers_of_records'] == 5
    assert len(response_data['data']) == 5
    assert response_data['pagination'] == {
        'total_pages': 2,
        'total_records': 10,
        'current_page': '/api/v1/authors?page=1',
        'next_page': '/api/v1/authors?page=2'
    }


def test_get_authors_with_params(client, sample_data):
    response = client.get(
        'api/v1/authors?fields=first_name&sort=-id&page=2&limit=2')
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['numbers_of_records'] == 2

    assert response_data['pagination'] == {
        'total_pages': 5,
        'total_records': 10,
        'current_page': '/api/v1/authors?page=2&fields=first_name&sort=-id&limit=2',
        'next_page': '/api/v1/authors?page=3&fields=first_name&sort=-id&limit=2',
        'previous_page': '/api/v1/authors?page=1&fields=first_name&sort=-id&limit=2'
    }


def test_get_single_authors(client, sample_data):

    response = client.get('/api/v1/authors/9')
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True

    assert (response_data['data']['first_name']) == 'Andrzej'
    assert (response_data['data']['last_name']) == 'Sapkowski'
    assert (response_data['data']['birth_date']) == '21-06-1948'


def test_get_wrong_single_authors(client):
    response = client.get('api/v1/authors/60')
    response_data = response.get_json()

    assert response.status_code == 404
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data


def test_create_single_authors(client, token, author):
    response = client.post('api/v1/authors?', json=author,
                           headers={'Authorization': f'Bearer {token}'})
    response_data = response.get_json()
    expected_result = {
        'success': True,
        'data': {
            **author,
            'id': 1,
            'books': []
        }
    }
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data == expected_result

    response = client.get('api/v1/authors/1')
    response_data = response.get_json()

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data == expected_result


@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'last_name': 'Mickiewwicz', 'birth_date': '24-12-1798'}, 'first_name'),
        ({'first_name': 'Mickiewwicz', 'birth_date': '24-12-1798'}, 'last_name'),
        ({'last_name': 'Mickiewwicz', 'first_name': 'Mickiewwicz'}, 'birth_date'),

    ]
)
def test_add_author_invalid_data(client, token, data, missing_field):
    response = client.post('/api/v1/authors', json=data,
                           headers={'Authorization': f'Bearer {token}'})

    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data


def test_add_author_invalid_content_type(client, token, author):
    response = client.post('/api/v1/authors', data=author,
                           headers={'Authorization': f'Bearer {token}'})

    response_data = response.get_json()
    assert response.status_code == 415
    assert response.headers['Content-Type'] == 'application/json'


def test_add_author_missing_token(client, author):
    response = client.post('/api/v1/authors', json=author)

    response_data = response.get_json()
    assert response.status_code == 404
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data
