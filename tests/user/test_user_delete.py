class TestUserDelete:
    def test_user_delete(self, test_client, UserDBFactory, login):
        user = UserDBFactory()

        login_headers = login(user)

        response = test_client.get(f'/user/delete-user/{user.id}', headers=login_headers)

        assert response.status_code == 200
        assert response.json()['status'] is True

    def test_user_delete_if_user_is_someone_else(self, test_client, UserDBFactory, login):
        user = UserDBFactory()
        another_user = UserDBFactory()

        login_headers = login(user)

        response = test_client.get(f'/user/delete-user/{another_user.id}', headers=login_headers)

        assert response.status_code == 401
