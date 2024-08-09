from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, WebSocketException, status, WebSocket

from notes_backend.collections import get_collection, Collections
from notes_backend.core.NotesBaseModel import ObjectIdPydanticAnnotation
from notes_backend.core.websocket.connection_manager import manager, Client
from notes_backend.group.models import GroupDBModel

from notes_backend.websocket.models import WebsocketAction, SendNotificationActionModel, SendNotificationToClientModel


router = APIRouter()


async def socket_message_handler(client: Client, message: any):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)

    action = message['action']

    if action == WebsocketAction.SEND_NOTIFICATION.value:
        send_notification_model = SendNotificationActionModel.from_mongo(message)

        check_group_collection = GROUP_COLLECTION.find_one({'_id': send_notification_model.group_id})
        check_group = GroupDBModel.from_mongo(check_group_collection)
        if not check_group:
            raise WebSocketException(status.HTTP_404_NOT_FOUND,
                                     reason='grup bulunamadı')

        if client.user_id not in check_group.attendees:
            raise WebSocketException(status.HTTP_403_FORBIDDEN,
                                     reason='gruba üye değilsiniz')

        send_notification_to_client_model = SendNotificationToClientModel(sender_id=client.user_id,
                                                                          group_id=send_notification_model.group_id,
                                                                          content=send_notification_model.content)
        for user_id in send_notification_model.user_ids:
            await manager.send_personal_message(send_notification_to_client_model.to_json(), user_id)


@router.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket,
                             user_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]):
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    check_user = USER_COLLECTION.find_one({'_id': user_id})

    if not check_user:
        raise WebSocketException(code=status.HTTP_404_NOT_FOUND,
                                 reason='kullanıcı bulunamadı')

    client = Client(user_id=user_id, connection=websocket)
    await manager.connect(client=client)

    while True:
        data = await websocket.receive_json()
        await socket_message_handler(client, data)
