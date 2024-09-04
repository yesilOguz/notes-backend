from typing import Annotated, Optional, Any

from bson import ObjectId

from notes_backend.core.NotesBaseModel import NotesBaseModel, ObjectIdPydanticAnnotation
from notes_backend.websocket.models import WebsocketAction


class Color(NotesBaseModel):
    r: int
    g: int
    b: int
    alpha: float


class NotesDBModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    color: Color
    content: Any = None


class NotesCreateModel(NotesBaseModel):
    group_id: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None
    color: Color


class NotesCreateResponse(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    action: WebsocketAction = WebsocketAction.CREATE_NOTE.value
    group_name: Optional[str] = ''
    color: Color
    content: Any = None


class NotesGetModel(NotesBaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    color: Color
    content: Any = None


class NoteSaveModel(NotesBaseModel):
    color: Color
    content: Any = None
