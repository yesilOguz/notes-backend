from typing import Annotated

from bson import ObjectId
from enum import Enum

from notes_backend.core.NotesBaseModel import NotesBaseModel, ObjectIdPydanticAnnotation


class UserType(Enum):
    FREE_PLAN = 'freeplan'
    PAID_PLAN = 'paidplan'
    FAMILY_PLAN = 'familyplan'


class UserDBModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    email: str
    password: str
    plan: UserType = UserType.FREE_PLAN.value
    groups: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []


class UserRegisterModel(NotesBaseModel):
    email: str
    password: str


class UserRegisterForTestsModel(NotesBaseModel):
    email: str
    password: str
    plan: UserType = UserType.FREE_PLAN.value


class UserLoginModel(NotesBaseModel):
    email: str
    password: str


class UserGetResponseModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    email: str
    plan: UserType = UserType.FREE_PLAN.value
    groups: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []
