import pytest
from bson import ObjectId
from faker import Faker

from notes_backend.collections import get_collection, Collections
from notes_backend.group.models import GroupCreateModel, GroupDBModel, GroupUpdateModel
from notes_backend.user.models import UserDBModel

Faker.seed(3)
faker = Faker()


@pytest.fixture()
def GroupCreateModelFactory():
    def _func(group_name: str = faker.word(), group_code=None):
        return GroupCreateModel(group_name=group_name, group_code=group_code)

    return _func


@pytest.fixture()
def GroupUpdateModelFactory():
    def _func(group_name: str = faker.word()):
        return GroupUpdateModel(group_name=group_name)

    return _func


@pytest.fixture()
def GroupDBModelFactory():
    def _func(owner_id: ObjectId, group_name: str = faker.word(), group_code=faker.word(), attendees=None):
        if not attendees:
            attendees = [owner_id]
        GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
        USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

        user_db = USER_COLLECTION.find_one({'_id': owner_id})
        user = UserDBModel.from_mongo(user_db)

        group_model = GroupCreateModel(group_owner=owner_id, group_name=group_name,
                                       group_code=group_code, attendees=attendees, notes=[])

        inserted_group = GROUP_COLLECTION.insert_one(group_model.to_mongo())
        group_collection = GROUP_COLLECTION.find_one({'_id': inserted_group.inserted_id})
        group = GroupDBModel.from_mongo(group_collection)

        if user:
            user.groups.append(group.id)
            USER_COLLECTION.find_one_and_update(filter={'_id': user.id},
                                                update={'$set': user.to_mongo(exclude_unset=False)})

        return group

    return _func


@pytest.fixture()
def JoinGroups(UserDBFactory):
    def _func(user=UserDBModel, count_of_group=5):
        USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

        user_collection = USER_COLLECTION.find_one({'_id': user.id})
        user = UserDBModel.from_mongo(user_collection)

        groups = []
        group_ids = []
        for _ in range(count_of_group):
            GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)

            owner = UserDBFactory()

            group_model = GroupCreateModel(group_owner=owner.id, group_name=faker.word(),
                                           group_code=faker.word(), attendees=[owner.id, user.id], notes=[])

            inserted_group = GROUP_COLLECTION.insert_one(group_model.to_mongo())
            group_collection = GROUP_COLLECTION.find_one({'_id': inserted_group.inserted_id})
            group = GroupDBModel.from_mongo(group_collection)

            groups.append(group)
            group_ids.append(group.id)

        user.groups = group_ids
        USER_COLLECTION.find_one_and_update(filter={'_id': user.id},
                                            update={'$set': user.to_mongo(exclude_unset=False)})

        return groups

    return _func
