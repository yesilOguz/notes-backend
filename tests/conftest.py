import pytest
from faker import Faker
from fastapi.testclient import TestClient
from main import app
from notes_backend.auth.login_utilities import auth
from notes_backend.collections import get_collection, Collections
from notes_backend.core.mongo_database import MONGO
from notes_backend.user.models import UserRegisterModel, UserDBModel, UserRegisterForTestsModel, UserType

Faker.seed(3)
faker = Faker()


@pytest.fixture()
def test_client():
    with TestClient(app) as client:
        yield client
        MONGO.drop_database()


@pytest.fixture()
def UserDBFactory():
    def _func(email=faker.email(), password=faker.password(), plan: UserType = UserType.FREE_PLAN):
        register_model = UserRegisterForTestsModel(email=email, password=password, plan=plan.value)

        inserted_register = get_collection(Collections.USER_COLLECTION).insert_one(register_model.to_mongo())
        inserted_user_collection = get_collection(Collections.USER_COLLECTION).find_one(
            {'_id': inserted_register.inserted_id})
        inserted_user = UserDBModel.from_mongo(inserted_user_collection)

        return inserted_user

    return _func


@pytest.fixture()
def login():
    def _func(user: UserDBModel):
        authed_user = auth(user)

        access_token = authed_user.tokens.access_token
        headers = {'Authorization': f'bearer {access_token}'}

        return headers

    return _func
