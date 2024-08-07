from typing import Annotated, Optional

from bson import ObjectId

from notes_backend.core.NotesBaseModel import NotesBaseModel, ObjectIdPydanticAnnotation


class Color(NotesBaseModel):
    r: int
    g: int
    b: int
    alpha: float


class NotesDBModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    color: Color
    content: str = ''


class NotesCreateModel(NotesBaseModel):
    group_id: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None
    color: Color


class NotesGetModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    color: Color
    content: str = ''
