from bson import ObjectId

from notes_backend.user.otp_types import OTP_TYPES


class TestRenewPassword:
    def test_renew_password(self, test_client, UserDBFactory, OtpDBFactory, RenewPasswordFactory):
        user = UserDBFactory()
        otp = OtpDBFactory(user_id=user.id, otp_type=OTP_TYPES.PASSWORD_RESET)
        renew_password = RenewPasswordFactory()

        response = test_client.post(f'/user/renew-password/{user.email}/{otp.otp_code}', json=renew_password.to_json())

        assert response.status_code == 200
        assert response.json()['status'] is True

    def test_renew_password_if_mail_doesnt_match_with_pattern(self, test_client, UserDBFactory, OtpDBFactory, RenewPasswordFactory):
        user = UserDBFactory(email='not_a_valid_mail')
        otp = OtpDBFactory(user_id=user.id, otp_type=OTP_TYPES.PASSWORD_RESET)
        renew_password = RenewPasswordFactory()

        response = test_client.post(f'/user/renew-password/{user.email}/{otp.otp_code}', json=renew_password.to_json())

        assert response.status_code == 400

    def test_renew_password_user_not_existence(self, test_client, UserDBFactory, OtpDBFactory, RenewPasswordFactory):
        fake_mail = 'fake@fakemail.com'
        otp = OtpDBFactory(user_id=ObjectId(), otp_type=OTP_TYPES.PASSWORD_RESET)
        renew_password = RenewPasswordFactory()

        response = test_client.post(f'/user/renew-password/{fake_mail}/{otp.otp_code}', json=renew_password.to_json())

        assert response.status_code == 404

    def test_renew_password_if_otp_not_valid(self, test_client, UserDBFactory, OtpDBFactory, RenewPasswordFactory):
        user = UserDBFactory()
        otp_code = 'not_a_valid_code'
        renew_password = RenewPasswordFactory()

        response = test_client.post(f'/user/renew-password/{user.email}/{otp_code}', json=renew_password.to_json())

        assert response.status_code == 403