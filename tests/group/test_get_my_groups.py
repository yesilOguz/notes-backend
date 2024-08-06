class TestGetMyGroups:
    def test_get_my_groups(self, test_client, UserDBFactory, JoinGroups, login):
        user = UserDBFactory()
        groups = JoinGroups(user=user, count_of_group=5)

        login_header = login(user)
        response = test_client.get('/group/get-my-groups', headers=login_header)

        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_get_my_groups_if_user_has_no_group(self, test_client, UserDBFactory, login):
        user = UserDBFactory()

        login_header = login(user)
        response = test_client.get('/group/get-my-groups', headers=login_header)

        assert response.status_code == 200
        assert len(response.json()) == 0
