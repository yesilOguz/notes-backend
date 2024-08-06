from notes_backend.auth.login_utilities import auth, refresh


class TestAuth:
    def test_auth(self, UserDBFactory):
        user = UserDBFactory()

        authed_user = auth(user)

        assert authed_user.user.email == user.email
        assert authed_user.tokens.access_token != ''
        assert authed_user.tokens.refresh_token != ''
        assert authed_user.tokens.access_token != authed_user.tokens.refresh_token

    def test_refresh(self, UserDBFactory):
        user = UserDBFactory()

        authed_user = auth(user)

        refreshed_user = refresh({'id': str(authed_user.user.id)})

        assert refreshed_user.access_token != ''
        assert refreshed_user.refresh_token != ''
        assert refreshed_user.refresh_token != authed_user.tokens.refresh_token
        assert refreshed_user.access_token != authed_user.tokens.access_token
