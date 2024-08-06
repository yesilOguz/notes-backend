from bson import ObjectId


class TestUpdateGroup:
    def test_update_group(self, test_client, UserDBFactory, GroupDBModelFactory, GroupUpdateModelFactory, login):
        user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=user.id)
        group_update_model = GroupUpdateModelFactory()

        login_header = login(user)
        response = test_client.post(f'/group/update-group/{group.id}', json=group_update_model.to_json(), headers=login_header)

        assert response.status_code == 200
        assert response.json()['group_name'] == group_update_model.group_name

    def test_update_group_if_group_id_not_exist(self, test_client, UserDBFactory, GroupUpdateModelFactory, login):
        user = UserDBFactory()
        group_id = ObjectId()
        group_update_model = GroupUpdateModelFactory()

        login_header = login(user)
        response = test_client.post(f'/group/update-group/{group_id}',
                                    json=group_update_model.to_json(), headers=login_header)

        assert response.status_code == 404

    def test_update_group_if_user_not_owner(self, test_client, UserDBFactory, GroupDBModelFactory, GroupUpdateModelFactory, login):
        user = UserDBFactory()
        user_not_owner = UserDBFactory()
        group = GroupDBModelFactory(owner_id=user.id)
        group_update_model = GroupUpdateModelFactory()

        login_header = login(user_not_owner)
        response = test_client.post(f'/group/update-group/{group.id}', json=group_update_model.to_json(), headers=login_header)

        assert response.status_code == 401
