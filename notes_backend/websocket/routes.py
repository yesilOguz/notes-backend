from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, WebSocketDisconnect, WebSocketException, status, WebSocket, Security, HTTPException, Body
from fastapi_jwt import JwtAuthorizationCredentials

from notes_backend.auth.login_utilities import access_security
from notes_backend.collections import get_collection, Collections
from notes_backend.core.NotesBaseModel import ObjectIdPydanticAnnotation
from notes_backend.core.websocket.connection_manager import manager, Client
from notes_backend.group.models import GroupDBModel
from notes_backend.models import StatusResponse
from notes_backend.user.models import UserDBModel, UserType, UserGetResponseModel

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
                                                                          group_name=check_group.group_name,
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

    try:
        while True:
            data = await websocket.receive_json()
            await socket_message_handler(client, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get('/get-current-users', status_code=status.HTTP_200_OK, response_model=list[UserGetResponseModel])
def get_current_user_count(credentials: JwtAuthorizationCredentials = Security(access_security)):
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])

    user_collection = USER_COLLECTION.find_one({'_id': user_id})
    user = UserDBModel.from_mongo(user_collection)

    if user.plan != UserType.ADMIN_USER.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='yetkin yok!')

    active_clients = manager.active_connections
    active_users = []
    for client in active_clients:
        client_user_collection = USER_COLLECTION.find_one({'_id': client.user_id})
        client_user = UserGetResponseModel.from_mongo(client_user_collection)
        active_users.append(client_user)

    return active_users


@router.post('/send-notification', status_code=status.HTTP_200_OK, response_model=StatusResponse)
async def send_notification(send_notification_model: SendNotificationToClientModel = Body(...),
                      credentials: JwtAuthorizationCredentials = Security(access_security)):
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])

    user_collection = USER_COLLECTION.find_one({'_id': user_id})
    user = UserDBModel.from_mongo(user_collection)

    if user.plan != UserType.ADMIN_USER.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='yetkin yok!')

    await manager.broadcast(message=send_notification_model.to_json())

    return StatusResponse(status=True)
