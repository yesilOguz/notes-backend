class TestUserRegister:
    def test_user_register(self, test_client, UserRegisterFactory):
        user_register = UserRegisterFactory()

        response = test_client.post('/user/user-register', json=user_register.to_json())

        assert response.status_code == 201
        assert response.json()['user']['email'] == user_register.email

    def test_user_register_if_email_exist_in_db(self, test_client, UserRegisterFactory, UserDBFactory):
        user = UserDBFactory()

        user_register = UserRegisterFactory(email=user.email)
        response = test_client.post('/user/user-register', json=user_register.to_json())

        assert response.status_code == 400

    def test_user_register_if_email_is_empty(self, test_client, UserRegisterFactory):
        user_register = UserRegisterFactory(email='')

        response = test_client.post('/user/user-register', json=user_register.to_json())

        assert response.status_code == 400
