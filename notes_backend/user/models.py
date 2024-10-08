import datetime
from typing import Annotated

from bson import ObjectId
from enum import Enum

from notes_backend.core.NotesBaseModel import NotesBaseModel, ObjectIdPydanticAnnotation
from notes_backend.user.otp_types import OTP_TYPES


class UserType(Enum):
    FREE_PLAN = 'freeplan'
    PAID_PLAN = 'paidplan'
    FAMILY_PLAN = 'familyplan'
    ADMIN_USER = 'adminuser'


class UserDBModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    email: str
    password: str
    plan: UserType = UserType.FREE_PLAN.value
    groups: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []
    notification_credit: int = 0
    group_and_note_credit: int = 0


class UserRegisterModel(NotesBaseModel):
    email: str
    password: str


class AdminRegisterModel(NotesBaseModel):
    email: str
    password: str
    plan: UserType = UserType.ADMIN_USER.value


class UserRegisterForTestsModel(NotesBaseModel):
    email: str
    password: str
    plan: UserType = UserType.FREE_PLAN.value
    notification_credit: int = 0
    group_and_note_credit: int = 0


class UserLoginModel(NotesBaseModel):
    email: str
    password: str


class UserRenewPassword(NotesBaseModel):
    password: str


class UserGetResponseModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    email: str
    plan: UserType = UserType.FREE_PLAN.value
    groups: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []
    notification_credit: int = 0
    group_and_note_credit: int = 0


class UserOTPModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    requested_by: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    created_time: datetime.datetime
    end_time: datetime.datetime
    otp_code: str
    otp_type: OTP_TYPES


class UserOTPCreateModel(NotesBaseModel):
    requested_by: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    created_time: datetime.datetime
    end_time: datetime.datetime
    otp_code: str
    otp_type: OTP_TYPES
