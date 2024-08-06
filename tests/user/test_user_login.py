class TestUserLogin:
    def test_user_login(self, test_client, UserDBFactory, UserLoginFactory):
        user = UserDBFactory()
        user_login = UserLoginFactory(email=user.email, password=user.password)

        response = test_client.post('/user/login', json=user_login.to_json())

        assert response.status_code == 200
        assert response.json()['user']['email'] == user.email

    def test_user_login_if_email_is_wrong(self, test_client, UserDBFactory, UserLoginFactory):
        user = UserDBFactory()
        user_login = UserLoginFactory(email='fake@mail.com', password=user.password)

        response = test_client.post('/user/login', json=user_login.to_json())

        assert response.status_code == 401

    def test_user_login_if_password_is_wrong(self, test_client, UserDBFactory, UserLoginFactory):
        user = UserDBFactory()
        user_login = UserLoginFactory(email=user.email, password='123456789')

        response = test_client.post('/user/login', json=user_login.to_json())

        assert response.status_code == 401

    def test_user_login_if_password_and_email_are_wrong(self, test_client, UserLoginFactory):
        user_login = UserLoginFactory(email='fake@mail.com', password='123456789')

        response = test_client.post('/user/login', json=user_login.to_json())

        assert response.status_code == 401
