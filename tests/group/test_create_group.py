from notes_backend.user.models import UserType


class TestCreateGroup:
    def test_create_group(self, test_client, UserDBFactory, GroupCreateModelFactory, login):
        user = UserDBFactory()
        group_create_model = GroupCreateModelFactory()

        login_header = login(user)
        response = test_client.post('/group/create-group', json=group_create_model.to_json(), headers=login_header)

        assert response.status_code == 201
        assert response.json()['group_name'] == group_create_model.group_name

    def test_create_group_with_custom_code(self, test_client, UserDBFactory, GroupCreateModelFactory, login):
        user = UserDBFactory(plan=UserType.PAID_PLAN)
        group_create_model = GroupCreateModelFactory(group_code='custom-code')

        login_header = login(user)
        response = test_client.post('/group/create-group', json=group_create_model.to_json(), headers=login_header)

        assert response.status_code == 201
        assert response.json()['group_code'] == group_create_model.group_code
        assert response.json()['group_name'] == group_create_model.group_name

    def test_create_group_with_custom_code_if_user_in_free_plan(self, test_client, UserDBFactory, GroupCreateModelFactory, login):
        user = UserDBFactory()
        group_create_model = GroupCreateModelFactory(group_code='custom-code')

        login_header = login(user)
        response = test_client.post('/group/create-group', json=group_create_model.to_json(), headers=login_header)

        assert response.status_code == 403
