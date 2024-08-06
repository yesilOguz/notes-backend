from bson import ObjectId

from notes_backend.collections import get_collection, Collections
from notes_backend.group.models import GroupDBModel
from notes_backend.user.models import UserDBModel


class TestLeaveGroup:
    def test_leave_group(self, test_client, UserDBFactory, JoinGroups, login):
        user = UserDBFactory()
        groups = JoinGroups(user=user, count_of_group=5)

        login_header = login(user)
        response = test_client.get(f'/group/leave-group/{groups[0].group_code}', headers=login_header)

        assert response.status_code == 200

        user_db_collection = get_collection(Collections.USER_COLLECTION).find_one({'_id': user.id})
        user_db = UserDBModel.from_mongo(user_db_collection)

        group_db_collection = get_collection(Collections.GROUP_COLLECTION).find_one({'_id': groups[0].id})
        group_db = GroupDBModel.from_mongo(group_db_collection)

        assert len(user_db.groups) == 4
        assert len(group_db.attendees) == 1

    def test_leave_group_if_user_group_owner(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=user.id)

        login_header = login(user)
        response = test_client.get(f'/group/leave-group/{group.group_code}', headers=login_header)

        assert response.status_code == 400

    def test_leave_group_if_user_not_participant(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user = UserDBFactory()
        owner_user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=owner_user.id)

        login_header = login(user)
        response = test_client.get(f'/group/leave-group/{group.group_code}', headers=login_header)

        assert response.status_code == 404

    def test_leave_group_if_group_not_exist(self, test_client, UserDBFactory, login):
        user = UserDBFactory()

        login_header = login(user)
        response = test_client.get(f'/group/leave-group/{ObjectId()}', headers=login_header)

        assert response.status_code == 404
