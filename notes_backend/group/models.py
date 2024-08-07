from typing import Annotated, Optional

from bson import ObjectId

from notes_backend.core.NotesBaseModel import NotesBaseModel, ObjectIdPydanticAnnotation
from notes_backend.notes.models import NotesGetModel
from notes_backend.user.models import UserGetResponseModel


class GroupDBModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_owner: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_code: str
    group_name: str
    attendees: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []
    notes: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []


class GroupCreateModel(NotesBaseModel):
    group_owner: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None
    group_name: str
    group_code: Optional[str] = None
    attendees: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []
    notes: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []


class GroupUpdateModel(NotesBaseModel):
    group_name: Optional[str] = None


class GroupGetResponse(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_owner: UserGetResponseModel
    group_code: str
    group_name: str
    attendees: list[UserGetResponseModel] = []
    notes: list[NotesGetModel] = []
