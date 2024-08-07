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
