def test_main(test_client):
    response = test_client.get('/')

    assert response.status_code == 200
    assert response.json()['notes'] == '0.0.1b'
