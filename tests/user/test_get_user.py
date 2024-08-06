from bson import ObjectId


class TestGetUser:
    def test_get_user(self, test_client, UserDBFactory, login):
        user = UserDBFactory()
        user_to_check = UserDBFactory()

        login_headers = login(user)
        response = test_client.get(f'/user/get-user/{user_to_check.id}', headers=login_headers)

        assert response.status_code == 200
        assert response.json()['email'] == user_to_check.email

    def test_get_user_if_wanted_is_himself(self, test_client, UserDBFactory, login):
        user = UserDBFactory()

        login_headers = login(user)
        response = test_client.get(f'/user/get-user/{user.id}', headers=login_headers)

        assert response.status_code == 200
        assert response.json()['email'] == user.email

    def test_get_user_if_user_id_not_exist_in_db(self, test_client, UserDBFactory, login):
        user = UserDBFactory()

        login_headers = login(user)
        response = test_client.get(f'/user/get-user/{ObjectId()}', headers=login_headers)

        assert response.status_code == 404
