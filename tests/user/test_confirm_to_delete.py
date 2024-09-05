from bson import ObjectId

from notes_backend.user.otp_types import OTP_TYPES


class TestConfirmToDelete:
    def test_confirm_to_delete(self, test_client, UserDBFactory, OtpDBFactory):
        user = UserDBFactory()
        otp = OtpDBFactory(user_id=user.id, otp_type=OTP_TYPES.REMOVE_ACC)

        response = test_client.get(f'/user/confirm-to-delete/{user.email}/{otp.otp_code}')

        assert response.status_code == 200
        assert response.json()['status'] is True

    def test_confirm_to_delete_if_mail_doesnt_match_with_pattern(self, test_client, UserDBFactory, OtpDBFactory):
        user = UserDBFactory(email='not_a_valid_mail')
        otp = OtpDBFactory(user_id=user.id, otp_type=OTP_TYPES.REMOVE_ACC)

        response = test_client.get(f'/user/confirm-to-delete/{user.email}/{otp.otp_code}')

        assert response.status_code == 400

    def test_confirm_to_delete_if_user_not_existence(self, test_client, UserDBFactory, OtpDBFactory):
        fake_mail = 'fake@fakemail.com'
        otp = OtpDBFactory(user_id=ObjectId(), otp_type=OTP_TYPES.REMOVE_ACC)

        response = test_client.get(f'/user/confirm-to-delete/{fake_mail}/{otp.otp_code}')

        assert response.status_code == 404

    def test_confirm_to_delete_if_otp_not_valid(self, test_client, UserDBFactory, OtpDBFactory):
        user = UserDBFactory()
        otp_code = 'not_a_valid_code'

        response = test_client.get(f'/user/confirm-to-delete/{user.email}/{otp_code}')

        assert response.status_code == 403