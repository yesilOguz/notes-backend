import datetime
import math
import random

import pytest
from bson import ObjectId
from faker import Faker

from notes_backend.collections import get_collection, Collections
from notes_backend.core import DELETE_ACCOUNT_OTP_URL
from notes_backend.user.models import UserRegisterModel, UserLoginModel, UserOTPModel, UserOTPCreateModel, \
    UserRenewPassword
from notes_backend.user.otp_types import OTP_TYPES

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


@pytest.fixture()
def OtpDBFactory():
    def generate_otp_code():
        OTP_COLLECTION = get_collection(Collections.OTP_COLLECTION)

        digits = "0123456789"
        otp = ''

        for i in range(6):
            otp += digits[math.floor(random.random() * 10)]

        check_otp_code_for_existence_collection = OTP_COLLECTION.find_one({'otp_code': otp})
        check_otp_code_for_existence = UserOTPModel.from_mongo(check_otp_code_for_existence_collection)

        if check_otp_code_for_existence:
            if check_otp_code_for_existence.end_time < datetime.datetime.now():
                OTP_COLLECTION.find_one_and_delete({'otp_code': otp})
            else:
                return generate_otp_code()

        return otp

    def _func(user_id: ObjectId, otp_type: OTP_TYPES):
        OTP_COLLECTION = get_collection(Collections.OTP_COLLECTION)

        now = datetime.datetime.now()
        OTP_CODE_EXPIRES_IN = datetime.timedelta(minutes=5)

        generated_code = generate_otp_code()
        new_otp = UserOTPCreateModel(requested_by=user_id,
                                     created_time=now,
                                     end_time=now + OTP_CODE_EXPIRES_IN,
                                     otp_code=generated_code,
                                     otp_type=otp_type)

        OTP_COLLECTION.insert_one(new_otp.to_mongo())
        return new_otp

    return _func


@pytest.fixture()
def RenewPasswordFactory():
    def _func(password: str = faker.password()):
        return UserRenewPassword(password=password)
    return _func
