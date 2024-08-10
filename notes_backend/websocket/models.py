from typing import Annotated, Optional

from bson import ObjectId

from notes_backend.core.NotesBaseModel import NotesBaseModel, ObjectIdPydanticAnnotation

from enum import Enum


class WebsocketAction(Enum):
    SEND_NOTIFICATION = 'send_notification'
    SEND_SYSTEM_NOTIFICATION = 'send_system_notification'
    GET_ACTIVE_GROUP_MEMBERS = 'get_active_group_members'


class SendNotificationActionModel(NotesBaseModel):
    action: str = WebsocketAction.SEND_NOTIFICATION.value
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    user_ids: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []
    content: str


class SendNotificationToClientModel(NotesBaseModel):
    action: str = WebsocketAction.SEND_NOTIFICATION.value
    sender_id: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None
    group_id: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None
    content: str
