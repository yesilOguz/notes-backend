from notes_backend.user.otp_types import OTP_TYPES


class TestCheckOtp:
    def test_check_otp(self, test_client, UserDBFactory, OtpDBFactory):
        user = UserDBFactory()
        otp = OtpDBFactory(user_id=user.id, otp_type=OTP_TYPES.PASSWORD_RESET)

        response = test_client.get(f'/user/check-otp/{user.email}/{otp.otp_code}')

        assert response.status_code == 200
        assert response.json()['status'] is True

    def test_check_otp_if_mail_doesnt_match_with_pattern(self, test_client, UserDBFactory):
        user = UserDBFactory(email='not_a_valid_mail')
        otp_code = 'not_a_valid_code'

        response = test_client.get(f'/user/check-otp/{user.email}/{otp_code}')

        assert response.status_code == 400

    def test_check_otp_if_otp_not_match(self, test_client, UserDBFactory):
        user = UserDBFactory()
        otp_code = 'not_a_valid_code'

        response = test_client.get(f'/user/check-otp/{user.email}/{otp_code}')

        assert response.status_code == 403