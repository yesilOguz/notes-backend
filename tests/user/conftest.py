import pytest
from faker import Faker

from notes_backend.user.models import UserRegisterModel, UserLoginModel

Faker.seed(3)
faker = Faker()


@pytest.fixture()
def UserRegisterFactory():
    def _func(email=faker.email(), password=faker.password()):
        register_model = UserRegisterModel(email=email, password=password)
        return register_model
    return _func


@pytest.fixture()
def UserLoginFactory():
    def _func(email=faker.email(), password=faker.password()):
        login_model = UserLoginModel(email=email, password=password)
        return login_model
    return _func
