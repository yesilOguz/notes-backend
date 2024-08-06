from bson import ObjectId

from notes_backend.collections import get_collection, Collections
from notes_backend.user.models import UserDBModel


class TestDeleteGroup:
    def test_delete_group(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=user.id)

        login_header = login(user)
        response = test_client.get(f'/group/delete-group/{group.id}', headers=login_header)

        assert response.status_code == 200

        group_db_collection = get_collection(Collections.GROUP_COLLECTION).find_one({'_id': group.id})

        user_db_collection = get_collection(Collections.USER_COLLECTION).find_one({'_id': user.id})
        user_db = UserDBModel.from_mongo(user_db_collection)

        assert not group_db_collection
        assert len(user_db.groups) == 0

    def test_delete_group_if_group_not_exist(self, test_client, UserDBFactory, GroupDBModelFactory, login):
        user = UserDBFactory()
        group_id = ObjectId()

        login_header = login(user)
        response = test_client.get(f'/group/delete-group/{group_id}', headers=login_header)

        assert response.status_code == 404

    def test_delete_group_if_user_not_owner(self, test_client, UserDBFactory, JoinGroups, login):
        user = UserDBFactory()
        group = JoinGroups(user, count_of_group=1)[0]

        login_header = login(user)
        response = test_client.get(f'/group/delete-group/{group.id}', headers=login_header)

        assert response.status_code == 403

