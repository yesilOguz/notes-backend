class TestSendDeleteAccountOTP:
    def test_send_delete_account_otp(self, test_client, UserDBFactory):
        user = UserDBFactory(email='oguzyesil17@gmail.com')

        response = test_client.get(f'/user/send-delete-account-otp/{user.email}')

        assert response.status_code == 200
        assert response.json()['status'] is True

    def test_send_delete_account_otp_if_mail_address_is_not_real(self, test_client, UserDBFactory):
        user = UserDBFactory(email='fake@fakemail.com')

        response = test_client.get(f'/user/send-delete-account-otp/{user.email}')

        assert response.status_code == 200

    def test_send_delete_account_otp_if_mail_address_not_valid(self, test_client, UserDBFactory):
        user = UserDBFactory(email='not_valid_email')

        response = test_client.get(f'/user/send-delete-account-otp/{user.email}')

        assert response.status_code == 400

    def test_send_delete_account_otp_if_there_is_no_user_with_that_email(self, test_client):
        fake_mail = 'fakemail@fake.com'
        response = test_client.get(f'/user/send-delete-account-otp/{fake_mail}')

        assert response.status_code == 404
