from bson import ObjectId

from notes_backend.user.models import UserType


class TestJoinGroup:
    def test_join_group(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user = UserDBFactory()
        user_to_join = UserDBFactory()

        group = GroupDBModelFactory(owner_id=user.id)

        login_header = login(user_to_join)
        response = test_client.get(f'/group/join-group/{group.group_code}', headers=login_header)

        assert response.status_code == 200
        assert len(response.json()['attendees']) == 2

    def test_join_group_if_group_code_not_exist(self, test_client, UserDBFactory, login):
        user = UserDBFactory()

        group_code = 'not-exist'

        login_header = login(user)
        response = test_client.get(f'/group/join-group/{group_code}', headers=login_header)

        assert response.status_code == 404

    def test_join_group_if_group_owner_not_exist(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user_to_join = UserDBFactory()

        group = GroupDBModelFactory(owner_id=ObjectId())

        login_header = login(user_to_join)
        response = test_client.get(f'/group/join-group/{group.group_code}', headers=login_header)

        assert response.status_code == 404

    def test_join_group_if_owner_in_free_plan_and_invited_third_person(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user = UserDBFactory()
        user_to_join = UserDBFactory()
        user_to_join_2 = UserDBFactory()

        group = GroupDBModelFactory(owner_id=user.id)

        login_header = login(user_to_join)
        test_client.get(f'/group/join-group/{group.group_code}', headers=login_header)

        login_header_2_for_third = login(user_to_join_2)
        response = test_client.get(f'/group/join-group/{group.group_code}', headers=login_header_2_for_third)

        assert response.status_code == 403

    def test_join_group_if_owner_in_paid_plan_and_invited_third_person(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user = UserDBFactory(plan=UserType.PAID_PLAN)
        user_to_join = UserDBFactory()
        user_to_join_2 = UserDBFactory()

        group = GroupDBModelFactory(owner_id=user.id)

        login_header = login(user_to_join)
        test_client.get(f'/group/join-group/{group.group_code}', headers=login_header)

        login_header_2_for_third = login(user_to_join_2)
        response = test_client.get(f'/group/join-group/{group.group_code}', headers=login_header_2_for_third)

        assert response.status_code == 403

    def test_join_group_if_owner_in_family_plan_and_invited_third_person(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user = UserDBFactory(plan=UserType.FAMILY_PLAN)
        user_to_join = UserDBFactory()
        user_to_join_2 = UserDBFactory()

        group = GroupDBModelFactory(owner_id=user.id)

        login_header = login(user_to_join)
        test_client.get(f'/group/join-group/{group.group_code}', headers=login_header)

        login_header_2_for_third = login(user_to_join_2)
        response = test_client.get(f'/group/join-group/{group.group_code}', headers=login_header_2_for_third)

        assert response.status_code == 200
        assert len(response.json()['attendees']) == 3
