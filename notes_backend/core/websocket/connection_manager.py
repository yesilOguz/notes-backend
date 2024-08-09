from typing import Annotated, Optional

from bson import ObjectId
from fastapi import WebSocket

from notes_backend.core.NotesBaseModel import NotesBaseModel, ObjectIdPydanticAnnotation
from notes_backend.group.models import GroupDBModel


class Client(NotesBaseModel):
    user_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    connection: WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[Client] = []

    async def connect(self, client: Client):
        await client.connection.accept()
        self.active_connections.append(client)

    def disconnect(self, websocket: WebSocket):
        will_remove_user = None
        for user in self.active_connections:
            if user.connection == websocket:
                will_remove_user = user
                break

        self.active_connections.remove(will_remove_user)

    async def send_personal_message(self, message: str, user_id: ObjectId):
        for user in self.active_connections:
            if user.user_id == user_id:
                await user.connection.send_json(message)
                break

    async def send_group_message(self, message: str, group: GroupDBModel, except_id: Optional[ObjectId] = None):
        for user in self.active_connections:
            if user.user_id in group.attendees and user.user_id != except_id:
                await user.connection.send_text(message)
                break

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.connection.send_text(message)


manager = ConnectionManager()
