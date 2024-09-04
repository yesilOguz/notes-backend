import pytest
from bson import ObjectId
from faker import Faker
from fastapi.testclient import TestClient
from main import app
from notes_backend.auth.login_utilities import auth
from notes_backend.collections import get_collection, Collections
from notes_backend.core.mongo_database import MONGO
from notes_backend.group.models import GroupCreateModel, GroupDBModel
from notes_backend.user.models import UserDBModel, UserRegisterForTestsModel, UserType

Faker.seed(3)
faker = Faker()


@pytest.fixture()
def test_client():
    with TestClient(app) as client:
        yield client
        MONGO.drop_database()


@pytest.fixture()
def UserDBFactory():
    def _func(email=None, password=faker.password(), plan: UserType = UserType.FREE_PLAN,
              notification_credit: int = 0, group_and_note_credit: int = 0):
        if email is None:
            email = faker.email()

        register_model = UserRegisterForTestsModel(email=email, password=password, plan=plan.value,
                                                   notification_credit=notification_credit,
                                                   group_and_note_credit=group_and_note_credit)

        inserted_register = get_collection(Collections.USER_COLLECTION).insert_one(register_model.to_mongo())
        inserted_user_collection = get_collection(Collections.USER_COLLECTION).find_one(
            {'_id': inserted_register.inserted_id})
        inserted_user = UserDBModel.from_mongo(inserted_user_collection)

        return inserted_user

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


@pytest.fixture()
def GroupDBModelFactory():
    def _func(owner_id: ObjectId, group_name: str = faker.word(), group_code=faker.word(), attendees=None):
        if attendees is None:
            attendees = []

        GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
        USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

        user_db = USER_COLLECTION.find_one({'_id': owner_id})
        user = UserDBModel.from_mongo(user_db)

        if user:
            attendees.append(user.id)

        group_model = GroupCreateModel(group_owner=owner_id, group_name=group_name,
                                       group_code=group_code, attendees=attendees, notes=[])

        inserted_group = GROUP_COLLECTION.insert_one(group_model.to_mongo(exclude_unset=False))
        group_collection = GROUP_COLLECTION.find_one({'_id': inserted_group.inserted_id})
        group = GroupDBModel.from_mongo(group_collection)

        if user:
            user.groups.append(group.id)
            USER_COLLECTION.find_one_and_update(filter={'_id': user.id},
                                                update={'$set': user.to_mongo(exclude_unset=False)})

        return group

    return _func


@pytest.fixture()
def login():
    def _func(user: UserDBModel):
        authed_user = auth(user)

        access_token = authed_user.tokens.access_token
        headers = {'Authorization': f'bearer {access_token}'}

        return headers

    return _func
