from typing import Annotated, Optional, Any

from bson import ObjectId

from notes_backend.core.NotesBaseModel import NotesBaseModel, ObjectIdPydanticAnnotation

from enum import Enum


class WebsocketAction(Enum):
    SEND_NOTIFICATION = 'send_notification'
    GROUP_CREDIT_NOTIFICATION = 'group_credit_notification'
    NOTIFICATION_CREDIT_NOTIFICATION = 'notification_credit_notification'
    GET_ACTIVE_GROUP_MEMBERS = 'get_active_group_members'
    UPDATE_NOTE = 'update_note'
    CREATE_NOTE = 'create_note'


class SendNotificationActionModel(NotesBaseModel):
    action: str = WebsocketAction.SEND_NOTIFICATION.value
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    user_ids: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []
    content: str


class SendNotificationToClientModel(NotesBaseModel):
    action: str = WebsocketAction.SEND_NOTIFICATION.value
    sender_id: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None
    group_id: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None
    group_name: Optional[str] = None
    content: str


class UpdateNoteActionModel(NotesBaseModel):
    action: str = WebsocketAction.UPDATE_NOTE.value
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    note_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    data: Any


class UpdateNoteToClientModel(NotesBaseModel):
    action: str = WebsocketAction.UPDATE_NOTE.value
    sender_id: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None
    group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    note_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    group_name: Optional[str] = None
    data: Any
